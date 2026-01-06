import logging
import sys
from typing import Any
from flask import Flask, jsonify, request
from logging.config import dictConfig
from datetime import datetime, timedelta

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
        "root": {
            "level": "INFO",
            "handlers": ["wsgi"]
        }
    })

FAILED_ATTEMPTS: dict[str, int] = {}
LAST_LOGIN: dict[str, datetime] = {}
SESSION_EXPIRY: dict[str, datetime] = {}
MAX_ATTEMPTS = 5
SESSION_TIMEOUT_MINUTES = 30

def create_app() -> Flask:
    configure_logging()
    app = Flask(__name__)

    @app.route("/health", methods=["GET"])
    def health_check() -> Any:
        return jsonify({"status": "ok"}), 200

    @app.route("/login", methods=["POST"])
    def login_user() -> Any:
        data = request.get_json(silent=True) or {}
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            app.logger.warning("Missing email or password during login.")
            return jsonify({"error": "Email and password are required"}), 400

        if FAILED_ATTEMPTS.get(email, 0) >= MAX_ATTEMPTS:
            app.logger.warning("Account locked due to excessive failed attempts for %s", email)
            return jsonify({"error": "Account locked due to too many failed attempts"}), 403

        # Dummy validation for demonstration
        if password != "securePassword123":
            FAILED_ATTEMPTS[email] = FAILED_ATTEMPTS.get(email, 0) + 1
            remaining = MAX_ATTEMPTS - FAILED_ATTEMPTS[email]
            app.logger.info("Invalid login attempt for %s, %d attempts left", email, remaining)
            return jsonify({"error": f"Invalid credentials. {remaining} attempts remaining"}), 401

        FAILED_ATTEMPTS.pop(email, None)
        LAST_LOGIN[email] = datetime.utcnow()
        SESSION_EXPIRY[email] = datetime.utcnow() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
        app.logger.info("User %s logged in successfully", email)
        return jsonify({
            "message": "Login successful",
            "session_expires_at": SESSION_EXPIRY[email].isoformat()
        }), 200

    @app.route("/session", methods=["GET"])
    def session_status() -> Any:
        email = request.args.get("email")
        if not email or email not in SESSION_EXPIRY:
            return jsonify({"error": "Invalid session"}), 401
        if datetime.utcnow() > SESSION_EXPIRY[email]:
            SESSION_EXPIRY.pop(email)
            app.logger.info("Session expired for %s", email)
            return jsonify({"error": "Session expired"}), 403
        return jsonify({"message": "Session active"}), 200

    @app.errorhandler(Exception)
    def handle_exception(e: Exception) -> Any:
        app.logger.error("Unhandled exception: %s", str(e), exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=5000, debug=False)