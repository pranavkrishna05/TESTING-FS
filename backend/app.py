import logging
import signal
import sys
from flask import Flask, jsonify
from logging.config import dictConfig
from types import FrameType
from typing import Any


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {"format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"}
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                }
            },
            "root": {"level": "INFO", "handlers": ["wsgi"]},
        }
    )


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    @app.route("/health", methods=["GET"])
    def health() -> Any:
        return jsonify({"status": "healthy"}), 200

    return app


def graceful_shutdown(sig: int, frame: FrameType | None) -> None:
    logging.info("Received shutdown signal %s. Terminating gracefully.", sig)
    sys.exit(0)


def main() -> None:
    configure_logging()
    app = create_app()

    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    logging.info("Starting Flask server on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()