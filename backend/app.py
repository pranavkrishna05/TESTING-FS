import logging
import sys
import time
from datetime import datetime, timedelta
from typing import Any
from flask import Flask, jsonify, request, session
from logging.config import dictConfig
from werkzeug.security import check_password_hash, generate_password_hash

def configure_logging() -> None:
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"}
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
MAX_LOGIN_ATTEMPTS = 5
SESSION_TIMEOUT_MINUTES = 15

def create_app() -> Flask:
    configure_logging()
    app = Flask(__name__)
    app.secret_key = "SESSION_SECRET_KEY"

    @app.route("/health", methods=["GET"])
    def health() -> Any:
        return jsonify({"status": "ok"}), 200

    @app.route("/register", methods=["POST"])
    def register_user() -> Any:
        nonlocal USER_ID_COUNTER
        data = request.get_json(silent=True) or {}
        email, password = data.get("email", "").strip().lower(), data.get("password", "")
        if not email or "@" not in email:
            return jsonify({"error": "Invalid email"}), 400
        if not password or len(password) < 8:
            return jsonify({"error": "Password too short; must be at least 8 chars"}), 400
        if any(u["email"] == email for u in USERS.values()):
            return jsonify({"error": "Email already registered"}), 400

        USERS[USER_ID_COUNTER] = {
            "id": USER_ID_COUNTER,
            "email": email,
            "password_hash": generate_password_hash(password),
            "failed_attempts": 0,
            "last_login": None,
            "locked": False,
            "created_at": datetime.utcnow().isoformat()
        }
        USER_ID_COUNTER += 1
        app.logger.info("Registered new user with email: %s", email)
        return jsonify({"message": "User registered successfully"}), 201

    @app.route("/login", methods=["POST"])
    def login() -> Any:
        data = request.get_json(silent=True) or {}
        email, password = data.get("email", "").strip().lower(), data.get("password", "")
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = next((u for u in USERS.values() if u["email"] == email), None)
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        if user["locked"]:
            return jsonify({"error": "Account locked due to too many failed attempts"}), 403

        if not check_password_hash(user["password_hash"], password):
            user["failed_attempts"] += 1
            if user["failed_attempts"] >= MAX_LOGIN_ATTEMPTS:
                user["locked"] = True
            return jsonify({
                "error": "Invalid credentials",
                "remaining_attempts": max(0, MAX_LOGIN_ATTEMPTS - user["failed_attempts"])
            }), 401

        user["failed_attempts"] = 0
        user["last_login"] = datetime.utcnow().isoformat()
        session["user_id"] = user["id"]
        session["logged_in_at"] = time.time()
        app.logger.info("User %s logged in successfully.", email)
        return jsonify({"message": "Logged in successfully", "user_id": user["id"]}), 200

    @app.before_request
    def session_timeout() -> None:
        user_id = session.get("user_id")
        if not user_id:
            return None
        last_activity = session.get("logged_in_at")
        if not last_activity:
            return None
        elapsed = time.time() - last_activity
        if elapsed > SESSION_TIMEOUT_MINUTES * 60:
            session.clear()
            app.logger.info("Session timed out for user_id %s", user_id)
            return jsonify({"error": "Session timed out, please log in again"}), 440
        session["logged_in_at"] = time.time()

    @app.route("/logout", methods=["POST"])
    def logout() -> Any:
        session.clear()
        return jsonify({"message": "Logged out successfully"}), 200

    @app.route("/users", methods=["GET"])
    def list_users() -> Any:
        safe_list = [{"id": u["id"], "email": u["email"], "locked": u["locked"], "created_at": u["created_at"]} for u in USERS.values()]
        return jsonify(safe_list), 200

    @app.errorhandler(Exception)
    def handle_exception(e: Exception) -> Any:
        app.logger.error("Unhandled Exception: %s", e, exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)