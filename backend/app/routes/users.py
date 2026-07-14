from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.db import query_all, query_one, execute
from app.utils.auth import hash_password

bp = Blueprint("users", __name__)

VALID_ROLES = {"student", "officer", "admin"}


def _require_admin():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Only administrators can manage users."}), 403
    return None


@bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    auth_error = _require_admin()
    if auth_error:
        return auth_error

    users = query_all(
        "SELECT user_id, first_name, last_name, email, role, organization_id, created_at FROM users ORDER BY role DESC, last_name ASC"
    )
    return jsonify(users), 200


@bp.route("/users", methods=["POST"])
@jwt_required()
def create_user():
    auth_error = _require_admin()
    if auth_error:
        return auth_error

    data = request.get_json(force=True) or {}
    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "student").strip().lower()
    organization_id = data.get("organization_id")

    if not all([first_name, last_name, email, password]):
        return jsonify({"error": "First name, last name, email, and password are required."}), 400
    if role not in VALID_ROLES:
        return jsonify({"error": "Role must be student, officer, or admin."}), 400
    if role == "officer" and not organization_id:
        return jsonify({"error": "Officer accounts must be assigned to an organization."}), 400
    if role != "officer":
        organization_id = None

    existing = query_one("SELECT user_id FROM users WHERE email = :email", {"email": email})
    if existing:
        return jsonify({"error": "An account with that email already exists."}), 409

    password_hash = hash_password(password)
    execute(
        """
        INSERT INTO users (first_name, last_name, email, password_hash, role, organization_id)
        VALUES (:first_name, :last_name, :email, :password_hash, :role, :organization_id)
        """,
        {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "organization_id": organization_id,
        },
    )

    user = query_one(
        "SELECT user_id, first_name, last_name, email, role, organization_id, created_at FROM users WHERE email = :email",
        {"email": email},
    )
    return jsonify(user), 201


@bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    auth_error = _require_admin()
    if auth_error:
        return auth_error

    user = query_one("SELECT user_id, email, role, organization_id FROM users WHERE user_id = :id", {"id": user_id})
    if not user:
        return jsonify({"error": "User not found."}), 404

    data = request.get_json(force=True) or {}
    role = (data.get("role") or user["role"]).strip().lower()
    organization_id = data.get("organization_id", user["organization_id"])

    if role not in VALID_ROLES:
        return jsonify({"error": "Role must be student, officer, or admin."}), 400
    if role == "officer" and not organization_id:
        return jsonify({"error": "Officer accounts must be assigned to an organization."}), 400
    if role != "officer":
        organization_id = None

    execute(
        """
        UPDATE users
        SET role = :role,
            organization_id = :organization_id
        WHERE user_id = :id
        """,
        {
            "role": role,
            "organization_id": organization_id,
            "id": user_id,
        },
    )

    updated = query_one(
        "SELECT user_id, first_name, last_name, email, role, organization_id, created_at FROM users WHERE user_id = :id",
        {"id": user_id},
    )
    return jsonify(updated), 200


@bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    auth_error = _require_admin()
    if auth_error:
        return auth_error

    user = query_one("SELECT user_id FROM users WHERE user_id = :id", {"id": user_id})
    if not user:
        return jsonify({"error": "User not found."}), 404

    execute("DELETE FROM users WHERE user_id = :id", {"id": user_id})
    return jsonify({"message": "User deleted."}), 200
