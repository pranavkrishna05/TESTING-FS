import logging
import secrets
import sys
from datetime import datetime, timedelta
from typing import Any
from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash
from logging.config import dictConfig

def configure_logging() -> None:
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"}
        },
        "handlers": {
            "wsgi": {"class": "logging.StreamHandler", "stream": sys.stdout, "formatter": "default"}
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]}
    })

USERS: dict[int, dict[str, Any]] = {}
RESETS: dict[str, dict[str, Any]] = {}
USER_ID_COUNTER = 1

def create_app() -> Flask:
    configure_logging()
    app = Flask(__name__)

    @app.route("/health", methods=["GET"])
    def health() -> Any:
        return jsonify({"status": "ok"}), 200

    @app.route("/register", methods=["POST"])
    def register() -> Any:
        nonlocal USER_ID_COUNTER
        data = request.get_json(silent=True) or {}
        email, password = data.get("email", "").strip().lower(), data.get("password", "")
        if not email or "@" not in email:
            return jsonify({"error": "Invalid email"}), 400
        if not password or len(password) < 8:
            return jsonify({"error": "Password too short"}), 400
        if any(u["email"] == email for u in USERS.values()):
            return jsonify({"error": "Email already registered"}), 400

        USERS[USER_ID_COUNTER] = {
            "id": USER_ID_COUNTER,
            "email": email,
            "password_hash": generate_password_hash(password),
            "created_at": datetime.utcnow().isoformat()
        }
        USER_ID_COUNTER += 1
        app.logger.info("Registered new user with email: %s", email)
        return jsonify({"message": "User registered successfully"}), 201

    @app.route("/password/forgot", methods=["POST"])
    def initiate_password_reset() -> Any:
        data = request.get_json(silent=True) or {}
        email = data.get("email", "").strip().lower()
        if not email or "@" not in email:
            return jsonify({"error": "Invalid email"}), 400
        user = next((u for u in USERS.values() if u["email"] == email), None)
        if not user:
            return jsonify({"error": "Email not found"}), 404

        token = secrets.token_urlsafe(32)
        expiration = datetime.utcnow() + timedelta(hours=24)
        RESETS[token] = {"user_id": user["id"], "expires_at": expiration}
        app.logger.info("Password reset token generated for %s expiring at %s", email, expiration)
        return jsonify({"message": "Password reset link sent to email", "token": token}), 200

    @app.route("/password/reset", methods=["POST"])
    def reset_password() -> Any:
        data = request.get_json(silent=True) or {}
        token, new_password = data.get("token"), data.get("new_password")
        if not token or not new_password:
            return jsonify({"error": "Token and new password required"}), 400
        reset_entry = RESETS.get(token)
        if not reset_entry:
            return jsonify({"error": "Invalid token"}), 400
        if datetime.utcnow() > reset_entry["expires_at"]:
            del RESETS[token]
            return jsonify({"error": "Token expired"}), 400
        if len(new_password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400

        user_id = reset_entry["user_id"]
        user = USERS.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        user["password_hash"] = generate_password_hash(new_password)
        del RESETS[token]
        app.logger.info("User %s successfully reset their password.", user["email"])
        return jsonify({"message": "Password has been reset"}), 200

    @app.errorhandler(Exception)
    def handle_exception(e: Exception) -> Any:
        app.logger.error("Unhandled Exception: %s", e, exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)