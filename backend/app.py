import logging
import sys
from datetime import datetime
from typing import Any
from flask import Flask, jsonify, request
from logging.config import dictConfig

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

PRODUCTS: dict[int, dict[str, Any]] = {}
CATEGORIES: dict[int, dict[str, Any]] = {}
ADMIN_TOKENS = {"admin12345"}
PRODUCT_ID_COUNTER = 1
CATEGORY_ID_COUNTER = 1

def create_app() -> Flask:
    configure_logging()
    app = Flask(__name__)

    @app.route("/health", methods=["GET"])
    def health_check() -> Any:
        return jsonify({"status": "ok"}), 200

    @app.route("/categories", methods=["POST"])
    def create_category() -> Any:
        nonlocal CATEGORY_ID_COUNTER
        token = request.headers.get("X-Admin-Token")
        if token not in ADMIN_TOKENS:
            return jsonify({"error": "Unauthorized - Admin access required"}), 403

        data = request.get_json(silent=True) or {}
        name = data.get("name")
        parent_id = data.get("parent_id")

        if not name:
            return jsonify({"error": "Category name is required"}), 400
        if any(cat["name"].lower() == name.lower() for cat in CATEGORIES.values()):
            return jsonify({"error": "Category name must be unique"}), 400
        if parent_id and parent_id not in CATEGORIES:
            return jsonify({"error": "Parent category not found"}), 400

        CATEGORIES[CATEGORY_ID_COUNTER] = {
            "id": CATEGORY_ID_COUNTER,
            "name": name.lower(),
            "parent_id": parent_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        app.logger.info("Category '%s' created successfully.", name)
        CATEGORY_ID_COUNTER += 1
        return jsonify({"message": "Category created successfully"}), 201

    @app.route("/categories", methods=["GET"])
    def list_categories() -> Any:
        return jsonify(list(CATEGORIES.values())), 200

    @app.route("/products", methods=["POST"])
    def create_product() -> Any:
        nonlocal PRODUCT_ID_COUNTER
        token = request.headers.get("X-Admin-Token")
        if token not in ADMIN_TOKENS:
            return jsonify({"error": "Unauthorized - Admin access required"}), 403

        data = request.get_json(silent=True) or {}
        name = data.get("name")
        price = data.get("price")
        description = data.get("description")
        category_ids = data.get("category_ids")

        if not name or not description or price is None:
            return jsonify({"error": "Name, description and price are required"}), 400
        if not isinstance(price, (int, float)) or price <= 0:
            return jsonify({"error": "Price must be numeric and greater than zero"}), 400
        if not category_ids or not isinstance(category_ids, list) or len(category_ids) == 0:
            return jsonify({"error": "At least one category is required"}), 400
        for cid in category_ids:
            if cid not in CATEGORIES:
                return jsonify({"error": f"Invalid category ID: {cid}"}), 400
        if any(prod["name"].lower() == name.lower() for prod in PRODUCTS.values()):
            return jsonify({"error": "Product name must be unique"}), 400

        PRODUCTS[PRODUCT_ID_COUNTER] = {
            "id": PRODUCT_ID_COUNTER,
            "name": name,
            "price": price,
            "description": description,
            "category_ids": category_ids,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        app.logger.info("Product '%s' created with categories %s.", name, category_ids)
        PRODUCT_ID_COUNTER += 1
        return jsonify({"message": "Product created successfully"}), 201

    @app.route("/products", methods=["GET"])
    def list_products() -> Any:
        data = []
        for p in PRODUCTS.values():
            categories = [CATEGORIES[cid]["name"] for cid in p["category_ids"] if cid in CATEGORIES]
            item = {**p, "categories": categories}
            data.append(item)
        return jsonify(data), 200

    @app.errorhandler(Exception)
    def handle_exception(e: Exception) -> Any:
        app.logger.error("Unhandled exception: %s", str(e), exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=5000, debug=False)