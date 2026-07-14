from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

from app.db import query_one, execute
from app.utils.auth import hash_password, check_password

bp = Blueprint("auth", __name__)

VALID_ROLES = {"student", "officer", "admin"}


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True) or {}
    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = data.get("role", "student")

    if not all([first_name, last_name, email, password]):
        return jsonify({"error": "First name, last name, email and password are all required."}), 400

    if role not in VALID_ROLES:
        role = "student"
    # Officers/admins should be promoted by an admin, not self-assigned on signup
    if role != "student":
        role = "student"

    existing = query_one("SELECT user_id FROM users WHERE email = :email", {"email": email})
    if existing:
        return jsonify({"error": "An account with that email already exists."}), 409

    password_hash = hash_password(password)

    execute(
        """
        INSERT INTO users (first_name, last_name, email, password_hash, role)
        VALUES (:first_name, :last_name, :email, :password_hash, :role)
        """,
        {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password_hash": password_hash,
            "role": role,
        },
    )

    user = query_one("SELECT user_id, first_name, last_name, email, role FROM users WHERE email = :email", {"email": email})

    token = create_access_token(identity=str(user["user_id"]), additional_claims={"role": user["role"]})
    return jsonify({"user": user, "access_token": token}), 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = query_one(
        "SELECT user_id, first_name, last_name, email, password_hash, role, organization_id "
        "FROM users WHERE email = :email",
        {"email": email},
    )
    if not user or not check_password(password, user["password_hash"]):
        return jsonify({"error": "Incorrect email or password."}), 401

    token = create_access_token(identity=str(user["user_id"]), additional_claims={"role": user["role"]})
    user.pop("password_hash")
    return jsonify({"user": user, "access_token": token}), 200


@bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    # Logout endpoint — client should discard the JWT.
    return jsonify({"message": "Logged out."}), 200


@bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = query_one(
        "SELECT user_id, first_name, last_name, email, role, organization_id FROM users WHERE user_id = :id",
        {"id": user_id},
    )
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify(user), 200
