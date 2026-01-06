import logging
import re
import sys
from datetime import datetime
from typing import Any
from flask import Flask, jsonify, request
from logging.config import dictConfig
from werkzeug.security import generate_password_hash

def configure_logging() -> None:
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "default"
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]}
    })

USERS: dict[int, dict[str, Any]] = {}
USER_ID_COUNTER = 1

def is_valid_password(password: str) -> bool:
    return (
        len(password) >= 8
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"\d", password)
        and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )

def create_app() -> Flask:
    configure_logging()
    app = Flask(__name__)

    @app.route("/health", methods=["GET"])
    def health() -> Any:
        return jsonify({"status": "ok"}), 200

    @app.route("/register", methods=["POST"])
    def register_user() -> Any:
        nonlocal USER_ID_COUNTER
        data = request.get_json(silent=True) or {}
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email:
            return jsonify({"error": "Email is required"}), 400
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "Invalid email format"}), 400
        if not password:
            return jsonify({"error": "Password is required"}), 400
        if not is_valid_password(password):
            return jsonify({"error": "Password must be at least 8 characters long, include uppercase, lowercase, number, and symbol"}), 400
        if any(u["email"] == email for u in USERS.values()):
            return jsonify({"error": "Email already registered"}), 400

        hashed_password = generate_password_hash(password)
        USERS[USER_ID_COUNTER] = {
            "id": USER_ID_COUNTER,
            "email": email,
            "password_hash": hashed_password,
            "created_at": datetime.utcnow().isoformat(),
        }
        USER_ID_COUNTER += 1
        app.logger.info("New user registered with email: %s", email)
        return jsonify({"message": "User registered successfully"}), 201

    @app.route("/users", methods=["GET"])
    def list_users() -> Any:
        return jsonify([
            {"id": u["id"], "email": u["email"], "created_at": u["created_at"]}
            for u in USERS.values()
        ]), 200

    @app.errorhandler(Exception)
    def on_error(e: Exception) -> Any:
        app.logger.error("Unhandled exception: %s", str(e), exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=5000, debug=False)