from typing import Any, Dict, Optional, cast

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt  # type: ignore[reportUnknownVariableType]

from app.db import query_all, query_one, execute

JSONDict = Dict[str, Any]

bp = Blueprint("events", __name__)


@bp.route("/events", methods=["GET"])
def list_events():
    """Public event list with optional search + filters:
    ?q=keyword&category=Sports&organization_id=3&date_from=2026-08-01&date_to=2026-08-31
    """
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    organization_id = request.args.get("organization_id", "").strip()
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()

    sql = """
        SELECT e.event_id, e.title, e.description, e.venue, e.event_date, e.category,
               e.image_url, e.organization_id, o.organization_name
        FROM events e
        JOIN organizations o ON o.organization_id = e.organization_id
        WHERE 1 = 1
    """
    params = {}

    if q:
        sql += " AND (LOWER(e.title) LIKE :q OR LOWER(e.description) LIKE :q)"
        params["q"] = f"%{q.lower()}%"
    if category:
        sql += " AND e.category = :category"
        params["category"] = category
    if organization_id:
        sql += " AND e.organization_id = :organization_id"
        params["organization_id"] = organization_id
    if date_from:
        sql += " AND e.event_date >= TO_DATE(:date_from, 'YYYY-MM-DD')"
        params["date_from"] = date_from
    if date_to:
        sql += " AND e.event_date <= TO_DATE(:date_to, 'YYYY-MM-DD')"
        params["date_to"] = date_to

    sql += " ORDER BY e.event_date ASC"

    params: Dict[str, Any] = params
    events = query_all(sql, params)
    return jsonify(events), 200


@bp.route("/events/<int:event_id>", methods=["GET"])
def get_event(event_id: int) -> Any:
    event = query_one(
        """
        SELECT e.event_id, e.title, e.description, e.venue, e.event_date, e.category,
               e.image_url, e.organization_id, o.organization_name
        FROM events e
        JOIN organizations o ON o.organization_id = e.organization_id
        WHERE e.event_id = :id
        """,
        {"id": event_id},
    )
    if not event:
        return jsonify({"error": "Event not found."}), 404
    return jsonify(event), 200


def _assert_owns_organization(user_id: str, organization_id: Any, role: Optional[str]) -> bool:
    """Officers may only manage events for their own organization; admins can manage any."""
    if role == "admin":
        return True
    officer = query_one(
        "SELECT organization_id FROM users WHERE user_id = :id",
        {"id": user_id},
    )
    return bool(officer and str(officer["organization_id"]) == str(organization_id))


@bp.route("/events", methods=["POST"])
@jwt_required()
def create_event() -> Any:
    claims = cast(JSONDict, get_jwt())  # type: ignore[reportUnknownVariableType]
    role = cast(Optional[str], claims.get("role"))
    user_id = cast(str, get_jwt_identity())

    if role not in ("officer", "admin"):
        return jsonify({"error": "Only organization officers can create events."}), 403

    data: JSONDict = request.get_json(force=True) or {}
    organization_id: Any = data.get("organization_id")
    title = (data.get("title") or "").strip()
    description = cast(str, data.get("description", ""))
    venue = cast(str, data.get("venue", ""))
    event_date = cast(Optional[str], data.get("event_date"))  # 'YYYY-MM-DD'
    category = cast(str, data.get("category", ""))
    image_url = cast(str, data.get("image_url", ""))

    if not all([organization_id is not None, title, event_date]):
        return jsonify({"error": "organization_id, title and event_date are required."}), 400

    if not _assert_owns_organization(user_id, organization_id, role):
        return jsonify({"error": "You can only create events for your own organization."}), 403

    execute(
        """
        INSERT INTO events (organization_id, title, description, venue, event_date, category, image_url, created_by)
        VALUES (:organization_id, :title, :description, :venue, TO_DATE(:event_date, 'YYYY-MM-DD'),
                :category, :image_url, :created_by)
        """,
        {
            "organization_id": organization_id,
            "title": title,
            "description": description,
            "venue": venue,
            "event_date": event_date,
            "category": category,
            "image_url": image_url,
            "created_by": user_id,
        },
    )

    created = query_one(
        "SELECT MAX(event_id) AS event_id FROM events WHERE organization_id = :oid AND title = :title",
        {"oid": organization_id, "title": title},
    )
    if not created or not created.get("event_id"):
        return jsonify({"error": "Event created but could not be retrieved."}), 500

    new_event = query_one("SELECT * FROM events WHERE event_id = :id", {"id": created["event_id"]})
    return jsonify(new_event), 201


@bp.route("/events/<int:event_id>", methods=["PUT"])
@jwt_required()
def update_event(event_id: int) -> Any:
    claims = cast(JSONDict, get_jwt())  # type: ignore[reportUnknownVariableType]
    role = cast(Optional[str], claims.get("role"))
    user_id = cast(str, get_jwt_identity())

    event = query_one("SELECT * FROM events WHERE event_id = :id", {"id": event_id})
    if not event:
        return jsonify({"error": "Event not found."}), 404

    if not _assert_owns_organization(user_id, event["organization_id"], role):
        return jsonify({"error": "You can only edit events for your own organization."}), 403

    data: JSONDict = request.get_json(force=True) or {}
    fields: Dict[str, Any] = {
        "title": data.get("title", event["title"]),
        "description": data.get("description", event["description"]),
        "venue": data.get("venue", event["venue"]),
        "category": data.get("category", event["category"]),
        "image_url": data.get("image_url", event["image_url"]),
        "event_date": data.get("event_date"),
        "id": event_id,
    }

    if fields["event_date"]:
        execute(
            """
            UPDATE events
            SET title = :title, description = :description, venue = :venue,
                category = :category, image_url = :image_url,
                event_date = TO_DATE(:event_date, 'YYYY-MM-DD')
            WHERE event_id = :id
            """,
            fields,
        )
    else:
        fields.pop("event_date")
        execute(
            """
            UPDATE events
            SET title = :title, description = :description, venue = :venue,
                category = :category, image_url = :image_url
            WHERE event_id = :id
            """,
            fields,
        )

    updated = query_one("SELECT * FROM events WHERE event_id = :id", {"id": event_id})
    return jsonify(updated), 200


@bp.route("/events/<int:event_id>", methods=["DELETE"])
@jwt_required()
def delete_event(event_id: int) -> Any:
    claims = cast(JSONDict, get_jwt())  # type: ignore[reportUnknownVariableType]
    role = cast(Optional[str], claims.get("role"))
    user_id = cast(str, get_jwt_identity())

    event = query_one("SELECT * FROM events WHERE event_id = :id", {"id": event_id})
    if not event:
        return jsonify({"error": "Event not found."}), 404

    if not _assert_owns_organization(user_id, event["organization_id"], role):
        return jsonify({"error": "You can only delete events for your own organization."}), 403

    execute("DELETE FROM events WHERE event_id = :id", {"id": event_id})
    return jsonify({"message": "Event deleted."}), 200
