# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownVariableType=false

import os
from pathlib import Path
from typing import Any, Sequence, cast
from dotenv import load_dotenv
import oracledb

oracledb = cast(Any, oracledb)

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)


def _env_str(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise ValueError(f"Environment variable {name} must be set")
    return value


def connect():
    client_dir = os.getenv("ORACLE_CLIENT_LIB_DIR")
    if client_dir:
        oracledb.init_oracle_client(lib_dir=client_dir)

    conn = oracledb.connect(
        user=_env_str("ORACLE_USER"),
        password=_env_str("ORACLE_PASSWORD"),
        dsn=oracledb.makedsn(
            _env_str("ORACLE_HOST", "localhost"),
            int(_env_str("ORACLE_PORT", "1521")),
            service_name=_env_str("ORACLE_SERVICE_NAME", "XE"),
        ),
    )
    return conn


def execute_many(cursor: Any, statements: Sequence[str]) -> None:
    for stmt in statements:
        if not stmt.strip():
            continue
        cursor.execute(stmt)


def main():
    conn = connect()
    cur = conn.cursor()

    try:
        execute_many(
            cur,
            [
                "BEGIN EXECUTE IMMEDIATE 'DROP TABLE events'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;",
                "BEGIN EXECUTE IMMEDIATE 'DROP TABLE users'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;",
                "BEGIN EXECUTE IMMEDIATE 'DROP TABLE organizations'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;",
                "BEGIN EXECUTE IMMEDIATE 'DROP TABLE categories'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;",
                "BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE organizations_seq'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -2289 THEN RAISE; END IF; END;",
                "BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE users_seq'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -2289 THEN RAISE; END IF; END;",
                "BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE categories_seq'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -2289 THEN RAISE; END IF; END;",
                "BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE events_seq'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -2289 THEN RAISE; END IF; END;",
                "BEGIN EXECUTE IMMEDIATE 'DROP TRIGGER organizations_bi'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -4080 THEN RAISE; END IF; END;",
                "BEGIN EXECUTE IMMEDIATE 'DROP TRIGGER users_bi'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -4080 THEN RAISE; END IF; END;",
                "BEGIN EXECUTE IMMEDIATE 'DROP TRIGGER categories_bi'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -4080 THEN RAISE; END IF; END;",
                "BEGIN EXECUTE IMMEDIATE 'DROP TRIGGER events_bi'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -4080 THEN RAISE; END IF; END;",
            ],
        )

        cur.execute("CREATE SEQUENCE organizations_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE")
        cur.execute("CREATE SEQUENCE users_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE")
        cur.execute("CREATE SEQUENCE categories_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE")
        cur.execute("CREATE SEQUENCE events_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE")

        cur.execute(
            """
            CREATE TABLE organizations (
                organization_id NUMBER PRIMARY KEY,
                organization_name VARCHAR2(150) NOT NULL,
                description CLOB,
                category VARCHAR2(100),
                contact_email VARCHAR2(150),
                logo_url VARCHAR2(500),
                created_at TIMESTAMP DEFAULT SYSTIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE users (
                user_id NUMBER PRIMARY KEY,
                first_name VARCHAR2(100) NOT NULL,
                last_name VARCHAR2(100) NOT NULL,
                email VARCHAR2(150) NOT NULL UNIQUE,
                password_hash VARCHAR2(255) NOT NULL,
                role VARCHAR2(20) DEFAULT 'student' NOT NULL,
                organization_id NUMBER,
                created_at TIMESTAMP DEFAULT SYSTIMESTAMP,
                CONSTRAINT chk_users_role CHECK (role IN ('student', 'officer', 'admin')),
                CONSTRAINT fk_users_org FOREIGN KEY (organization_id)
                    REFERENCES organizations (organization_id) ON DELETE SET NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE categories (
                category_id NUMBER PRIMARY KEY,
                category_name VARCHAR2(100) NOT NULL UNIQUE
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE events (
                event_id NUMBER PRIMARY KEY,
                organization_id NUMBER NOT NULL,
                title VARCHAR2(200) NOT NULL,
                description CLOB,
                venue VARCHAR2(200),
                event_date DATE NOT NULL,
                category VARCHAR2(100),
                image_url VARCHAR2(500),
                created_by NUMBER,
                created_at TIMESTAMP DEFAULT SYSTIMESTAMP,
                CONSTRAINT fk_events_org FOREIGN KEY (organization_id)
                    REFERENCES organizations (organization_id) ON DELETE CASCADE,
                CONSTRAINT fk_events_creator FOREIGN KEY (created_by)
                    REFERENCES users (user_id) ON DELETE SET NULL
            )
            """
        )

        cur.execute(
            """
            CREATE OR REPLACE TRIGGER organizations_bi
            BEFORE INSERT ON organizations
            FOR EACH ROW
            BEGIN
                IF :NEW.organization_id IS NULL THEN
                    SELECT organizations_seq.NEXTVAL INTO :NEW.organization_id FROM dual;
                END IF;
            END;
            """
        )
        cur.execute(
            """
            CREATE OR REPLACE TRIGGER users_bi
            BEFORE INSERT ON users
            FOR EACH ROW
            BEGIN
                IF :NEW.user_id IS NULL THEN
                    SELECT users_seq.NEXTVAL INTO :NEW.user_id FROM dual;
                END IF;
            END;
            """
        )
        cur.execute(
            """
            CREATE OR REPLACE TRIGGER categories_bi
            BEFORE INSERT ON categories
            FOR EACH ROW
            BEGIN
                IF :NEW.category_id IS NULL THEN
                    SELECT categories_seq.NEXTVAL INTO :NEW.category_id FROM dual;
                END IF;
            END;
            """
        )
        cur.execute(
            """
            CREATE OR REPLACE TRIGGER events_bi
            BEFORE INSERT ON events
            FOR EACH ROW
            BEGIN
                IF :NEW.event_id IS NULL THEN
                    SELECT events_seq.NEXTVAL INTO :NEW.event_id FROM dual;
                END IF;
            END;
            """
        )

        cur.execute("CREATE INDEX idx_events_date ON events (event_date)")
        cur.execute("CREATE INDEX idx_events_org ON events (organization_id)")
        cur.execute("CREATE INDEX idx_events_category ON events (category)")
        cur.execute("CREATE INDEX idx_orgs_category ON organizations (category)")

        # All seeded users share the password: password123
        seed_data = [
            "INSERT INTO categories (category_name) VALUES ('Academic')",
            "INSERT INTO categories (category_name) VALUES ('Sports')",
            "INSERT INTO categories (category_name) VALUES ('Cultural')",
            "INSERT INTO categories (category_name) VALUES ('Volunteer')",
            "INSERT INTO categories (category_name) VALUES ('Technology')",
            "INSERT INTO organizations (organization_name, description, category, contact_email) VALUES ('The Ateneo Consortium of Technological, Information, and Computing Sciences (TACTICS)', 'The Official Organization for Department of Computer Studies.', 'Technology', 'tactics@adnu.edu.ph')",
            "INSERT INTO organizations (organization_name, description, category, contact_email) VALUES ('Ateneo Film Society (AFS)', 'An Organization for Aspiring Film Makers.', 'Cultural', 'afs@adnu.edu.ph')",
            "INSERT INTO organizations (organization_name, description, category, contact_email) VALUES ('ThePILLARS Publication', 'University Publication', 'Academic', 'thepillars@adnu.edu.ph')",
            "INSERT INTO organizations (organization_name, description, category, contact_email) VALUES ('Ateneo Golden Knights (AKG)', 'University Basketball Varsity Team', 'Sports', 'akg@adnu.edu.ph')",
            "INSERT INTO organizations (organization_name, description, category, contact_email) VALUES ('Liderato kan Nueva Atenista', 'University Student Government', 'Volunteer', 'liderato@adnu.edu.ph')",
            "INSERT INTO users (first_name, last_name, email, password_hash, role, organization_id) VALUES ('Ada', 'Admin', 'admin@adnu.edu.ph', '$2b$12$1UNPEWIHjkLghPxw26T6jeHb1/gYssvVJVjPJ8AGV.O24hmAdqDUG', 'admin', NULL)",
            "INSERT INTO users (first_name, last_name, email, password_hash, role, organization_id) VALUES ('Bluehub', 'Admin', 'bluehub@adnu.edu.ph', '$2b$12$Fs1zXkzKy/ByVjPW.F/USuEL1J609TO3ZLHHagh34wD18pkLFtKi.', 'admin', NULL)",
            "INSERT INTO users (first_name, last_name, email, password_hash, role, organization_id) VALUES ('Micco', 'Alcantara', 'officer@adnu.edu.ph', '$2b$12$1UNPEWIHjkLghPxw26T6jeHb1/gYssvVJVjPJ8AGV.O24hmAdqDUG', 'officer', 1)",
            "INSERT INTO users (first_name, last_name, email, password_hash, role, organization_id) VALUES ('Sam', 'Student', 'student@adnu.edu.ph', '$2b$12$1UNPEWIHjkLghPxw26T6jeHb1/gYssvVJVjPJ8AGV.O24hmAdqDUG', 'student', NULL)",
            "INSERT INTO events (organization_id, title, description, venue, event_date, category, created_by) VALUES (1, 'TACTICS Tech Showcase', 'A showcase of student projects from the Department of Computer Studies.', 'Computer Labs', TO_DATE('2026-09-10', 'YYYY-MM-DD'), 'Technology', 2)",
            "INSERT INTO events (organization_id, title, description, venue, event_date, category, created_by) VALUES (2, 'AFS Short Film Night', 'An evening of original short films created by aspiring filmmakers.', 'Multipurpose Hall', TO_DATE('2026-09-17', 'YYYY-MM-DD'), 'Cultural', 3)",
            "INSERT INTO events (organization_id, title, description, venue, event_date, category, created_by) VALUES (3, 'ThePILLARS Journalism Forum', 'A discussion on university publication and student journalism.', 'Ateneo Avenue', TO_DATE('2026-09-24', 'YYYY-MM-DD'), 'Academic', 3)",
            "INSERT INTO events (organization_id, title, description, venue, event_date, category, created_by) VALUES (4, 'AKG Home Game', 'Support the Ateneo Golden Knights at their university basketball match.', 'University Gymnasium', TO_DATE('2026-10-01', 'YYYY-MM-DD'), 'Sports', 3)",
            "INSERT INTO events (organization_id, title, description, venue, event_date, category, created_by) VALUES (5, 'Liderato Townhall', 'Student government town hall meeting for the campus community.', 'Ignatius Park', TO_DATE('2026-10-08', 'YYYY-MM-DD'), 'Volunteer', 3)",
        ]
        for sql in seed_data:
            cur.execute(sql)

        conn.commit()
        print("Schema and seed applied successfully.")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
