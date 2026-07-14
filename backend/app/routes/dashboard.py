from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.db import query_all, query_one

bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    user = query_one(
        "SELECT user_id, first_name, last_name, email, role, organization_id FROM users WHERE user_id = :id",
        {"id": user_id},
    )

    if role in ("officer", "admin") and user.get("organization_id"):
        events = query_all(
            """
            SELECT event_id, title, venue, event_date, category, image_url
            FROM events
            WHERE organization_id = :oid
            ORDER BY event_date DESC
            """,
            {"oid": user["organization_id"]},
        )
        org = query_one(
            "SELECT organization_id, organization_name, description, category FROM organizations WHERE organization_id = :oid",
            {"oid": user["organization_id"]},
        )
    else:
        events = []
        org = None

    return jsonify({"user": user, "organization": org, "managed_events": events}), 200
