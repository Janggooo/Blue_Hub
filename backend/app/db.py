import os
import re
import sqlite3
import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import oracledb  # type: ignore
from typing import cast

# oracledb has no type stubs in this environment; treat it as Any for static checks
oracledb = cast(Any, oracledb)
from flask import g

_pool: Any = None
_kind: Optional[str] = None  # 'oracle' or 'sqlite'
_sqlite_path: Optional[str] = None
_pool_dsn: Optional[str] = None


def _normalize_value(value: Any) -> Any:
    """Convert Oracle-specific values to JSON-serializable Python objects."""
    if value is None:
        return None
    # LOBs and file-like objects expose a `read()` method
    read_fn = getattr(value, "read", None)
    if callable(read_fn):
        try:
            return read_fn()
        except Exception:
            return str(value)
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _translate_named_params(sql: str, params: Optional[Dict[str, Any]]) -> Tuple[str, Optional[Tuple[Any, ...]]]:
    """Translate Oracle-style :name params to sqlite ? placeholders.
    Returns (translated_sql, param_tuple).
    If `params` is not a dict or there are no named parameters, returns (sql, None).
    """
    if not params:
        return sql, None

    # find :name occurrences (simple identifier rule)
    names = re.findall(r":([A-Za-z_]\w*)", sql)
    if not names:
        return sql, None

    new_sql = re.sub(r":([A-Za-z_]\w*)", "?", sql)
    param_tuple = tuple(params.get(n) for n in names)
    return new_sql, param_tuple


def _build_dsn_candidates(cfg: Dict[str, Any]) -> List[str]:
    """Return a list of DSN candidates for Oracle XE and common alternatives."""
    provided = (cfg.get("ORACLE_DSN") or "").strip()
    if provided:
        return [provided]

    host = cfg.get("ORACLE_HOST", "localhost")
    port_value = cfg.get("ORACLE_PORT", "1521")
    try:
        port = int(port_value)
    except (TypeError, ValueError):
        port = 1521

    service_names: List[str] = []
    raw_service = (cfg.get("ORACLE_SERVICE_NAME") or "").strip()
    if raw_service:
        service_names.append(raw_service)
    service_names.extend(["XEPDB1", "XE", "ORCL", "PDB1"])

    seen: set[str] = set()
    candidates: List[str] = []
    for service_name in service_names:
        if not service_name or service_name in seen:
            continue
        seen.add(service_name)
        candidates.append(oracledb.makedsn(host, port, service_name=service_name))
    return candidates


def _init_oracle_client(cfg: Dict[str, Any]) -> None:
    """Initialize Oracle client if `ORACLE_CLIENT_LIB_DIR` is set."""
    client_lib_dir = (cfg.get("ORACLE_CLIENT_LIB_DIR") or "").strip()
    if not client_lib_dir:
        return
    try:
        oracledb.init_oracle_client(lib_dir=client_lib_dir)  # type: ignore
    except Exception:
        # If initialization fails, connection attempts will surface the problem.
        pass


def init_pool(app: Any) -> None:
    """Initialize DB backend. Uses Oracle if credentials present, otherwise SQLite."""
    global _pool, _kind, _sqlite_path, _pool_dsn
    # copy config into a typed mapping to satisfy static analysis
    cfg: Dict[str, Any] = dict(app.config)

    # Prefer Oracle when ORACLE_USER and ORACLE_PASSWORD are set
    if cfg.get("ORACLE_USER") and cfg.get("ORACLE_PASSWORD"):
        _kind = "oracle"
        _init_oracle_client(cfg)
        errors: List[str] = []
        for dsn in _build_dsn_candidates(cfg):
            try:
                conn = oracledb.connect(  # type: ignore
                    user=cfg["ORACLE_USER"],
                    password=cfg["ORACLE_PASSWORD"],
                    dsn=dsn,
                )
                conn.close()
                _pool = oracledb.create_pool(  # type: ignore
                    user=cfg["ORACLE_USER"],
                    password=cfg["ORACLE_PASSWORD"],
                    dsn=dsn,
                    min=1,
                    max=5,
                    increment=1,
                )
                _pool_dsn = dsn
                return
            except Exception as exc:
                errors.append(f"{dsn}: {exc}")

        # Fall back to SQLite if Oracle is unreachable
        _kind = "sqlite"
        _pool = None
        _pool_dsn = None
        print("Warning: Oracle unavailable, falling back to SQLite dev.db. Details:", "; ".join(errors))

    if _kind != "oracle":
        _kind = "sqlite"
        # Use a sqlite file path relative to the app package
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        _sqlite_path = os.path.abspath(os.path.join(base, cfg.get("SQLITE_PATH", "dev.db")))
        # ensure file exists
        dirpath = os.path.dirname(_sqlite_path)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)


def get_db_kind() -> Optional[str]:
    return _kind


def get_connection() -> Any:
    """Return a connection for the current request context."""
    if _kind == "oracle":
        if "db_conn" not in g:
            # _pool is typed Any; at runtime it will be a real pool with acquire()
            g.db_conn = _pool.acquire()
        return g.db_conn
    if "db_conn" not in g:
        # _sqlite_path is set during init_pool when using sqlite
        assert _sqlite_path is not None
        conn = sqlite3.connect(_sqlite_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        g.db_conn = conn
    return g.db_conn


def close_connection(e: Optional[BaseException] = None) -> None:
    conn = g.pop("db_conn", None)
    if conn is None:
        return
    if _kind == "oracle":
        # _pool is Any at type-check time
        _pool.release(conn)
    else:
        conn.close()


def register_teardown(app: Any) -> None:
    app.teardown_appcontext(close_connection)


def query_all(sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Run a SELECT and return a list of dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    if _kind == "sqlite":
        sql_t, param_tuple = _translate_named_params(sql, params)
        cursor.execute(sql_t, param_tuple or [])
    else:
        cursor.execute(sql, params or {})

    columns = [col[0].lower() for col in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    normalized_rows: List[Dict[str, Any]] = []
    for row in rows:
        item: Dict[str, Any] = {}
        for col, value in zip(columns, row):
            item[col] = _normalize_value(value)
        normalized_rows.append(item)
    return normalized_rows


def query_one(sql: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    rows = query_all(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: Optional[Dict[str, Any]] = None, commit: bool = True) -> Any:
    """Run an INSERT/UPDATE/DELETE. Returns the cursor."""
    conn = get_connection()
    cursor = conn.cursor()
    if _kind == "sqlite":
        sql_t, param_tuple = _translate_named_params(sql, params)
        cursor.execute(sql_t, param_tuple or [])
    else:
        cursor.execute(sql, params or {})

    if commit:
        conn.commit()
    return cursor
