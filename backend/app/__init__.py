from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.config import Config
from app.db import init_pool, register_teardown, query_one, get_db_kind


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGIN"]}}, supports_credentials=True)
    JWTManager(app)

    init_pool(app)
    register_teardown(app)

    from app.routes import auth, events, organizations, dashboard, users

    app.register_blueprint(auth.bp, url_prefix="/api")
    app.register_blueprint(events.bp, url_prefix="/api")
    app.register_blueprint(organizations.bp, url_prefix="/api")
    app.register_blueprint(dashboard.bp, url_prefix="/api")
    app.register_blueprint(users.bp, url_prefix="/api")

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/api/db-health", methods=["GET"])
    def db_health():
        try:
            # Use dialect-appropriate SQL
            if get_db_kind() == "oracle":
                res = query_one("SELECT 1 AS ok FROM DUAL")
            else:
                res = query_one("SELECT 1 AS ok")
            return jsonify({"db": "ok", "result": res}), 200
        except Exception as exc:
            return jsonify({"db": "error", "message": str(exc)}), 500

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found."}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Something went wrong on the server."}), 500

    return app
