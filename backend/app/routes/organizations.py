from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.db import query_all, query_one, execute

bp = Blueprint("organizations", __name__)


@bp.route("/organizations", methods=["GET"])
def list_organizations():
    """Public org directory with optional ?q=keyword and ?category=Category filters."""
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    sql = "SELECT organization_id, organization_name, description, category, contact_email, logo_url FROM organizations WHERE 1 = 1"
    params = {}
    if q:
        sql += " AND LOWER(organization_name) LIKE :q"
        params["q"] = f"%{q.lower()}%"
    if category:
        sql += " AND category = :category"
        params["category"] = category
    sql += " ORDER BY organization_name ASC"

    orgs = query_all(sql, params)
    return jsonify(orgs), 200


@bp.route("/organizations/<int:organization_id>", methods=["GET"])
def get_organization(organization_id):
    org = query_one(
        "SELECT organization_id, organization_name, description, category, contact_email, logo_url "
        "FROM organizations WHERE organization_id = :id",
        {"id": organization_id},
    )
    if not org:
        return jsonify({"error": "Organization not found."}), 404

    upcoming_events = query_all(
        """
        SELECT event_id, title, venue, event_date, category, image_url
        FROM events
        WHERE organization_id = :id AND event_date >= SYSDATE
        ORDER BY event_date ASC
        """,
        {"id": organization_id},
    )
    org["upcoming_events"] = upcoming_events
    return jsonify(org), 200


@bp.route("/organizations", methods=["POST"])
@jwt_required()
def create_organization():
    """Admin-only: register a new organization in the directory."""
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Only administrators can create organizations."}), 403

    data = request.get_json(force=True) or {}
    name = (data.get("organization_name") or "").strip()
    if not name:
        return jsonify({"error": "organization_name is required."}), 400

    execute(
        """
        INSERT INTO organizations (organization_name, description, category, contact_email, logo_url)
        VALUES (:organization_name, :description, :category, :contact_email, :logo_url)
        """,
        {
            "organization_name": name,
            "description": data.get("description", ""),
            "category": data.get("category", ""),
            "contact_email": data.get("contact_email", ""),
            "logo_url": data.get("logo_url", ""),
        },
    )
    new_org = query_one(
        "SELECT * FROM organizations WHERE organization_name = :name ORDER BY organization_id DESC FETCH FIRST 1 ROWS ONLY",
        {"name": name},
    )
    return jsonify(new_org), 201


@bp.route("/organizations/<int:organization_id>", methods=["PUT"])
@jwt_required()
def update_organization(organization_id):
    claims = get_jwt()
    role = claims.get("role")
    user_id = get_jwt_identity()

    if role == "officer":
        officer = query_one("SELECT organization_id FROM users WHERE user_id = :id", {"id": user_id})
        if not officer or str(officer["organization_id"]) != str(organization_id):
            return jsonify({"error": "You can only edit your own organization's profile."}), 403
    elif role != "admin":
        return jsonify({"error": "You don't have permission to edit organizations."}), 403

    org = query_one("SELECT * FROM organizations WHERE organization_id = :id", {"id": organization_id})
    if not org:
        return jsonify({"error": "Organization not found."}), 404

    data = request.get_json(force=True) or {}
    execute(
        """
        UPDATE organizations
        SET organization_name = :organization_name,
            description = :description,
            category = :category,
            contact_email = :contact_email,
            logo_url = :logo_url
        WHERE organization_id = :id
        """,
        {
            "organization_name": data.get("organization_name", org["organization_name"]),
            "description": data.get("description", org["description"]),
            "category": data.get("category", org["category"]),
            "contact_email": data.get("contact_email", org["contact_email"]),
            "logo_url": data.get("logo_url", org["logo_url"]),
            "id": organization_id,
        },
    )
    updated = query_one("SELECT * FROM organizations WHERE organization_id = :id", {"id": organization_id})
    return jsonify(updated), 200


@bp.route("/categories", methods=["GET"])
def list_categories():
    categories = query_all("SELECT category_id, category_name FROM categories ORDER BY category_name")
    return jsonify(categories), 200
