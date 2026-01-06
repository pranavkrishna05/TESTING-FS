import logging
import sys
from datetime import datetime
from typing import Any
from flask import Flask, jsonify, request, session
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

USERS: dict[int, dict[str, Any]] = {}
PRODUCTS: dict[int, dict[str, Any]] = {}
CARTS: dict[int, list[dict[str, Any]]] = {}
USER_ID_COUNTER = 1
PRODUCT_ID_COUNTER = 1

def create_app() -> Flask:
    configure_logging()
    app = Flask(__name__)
    app.secret_key = "supersecretkey"

    @app.route("/health", methods=["GET"])
    def health_check() -> Any:
        return jsonify({"status": "ok"}), 200

    @app.route("/users", methods=["POST"])
    def create_user() -> Any:
        nonlocal USER_ID_COUNTER
        data = request.get_json(silent=True) or {}
        username = data.get("username")
        if not username:
            return jsonify({"error": "Username required"}), 400
        if any(u["username"] == username for u in USERS.values()):
            return jsonify({"error": "Username already exists"}), 400

        user = {
            "id": USER_ID_COUNTER,
            "username": username,
            "created_at": datetime.utcnow().isoformat(),
        }
        USERS[USER_ID_COUNTER] = user
        CARTS[USER_ID_COUNTER] = []
        USER_ID_COUNTER += 1
        return jsonify({"message": "User created", "user": user}), 201

    @app.route("/products", methods=["POST"])
    def create_product() -> Any:
        nonlocal PRODUCT_ID_COUNTER
        data = request.get_json(silent=True) or {}
        name, price, description = data.get("name"), data.get("price"), data.get("description")
        if not name or not description or price is None:
            return jsonify({"error": "Name, description and price are required"}), 400
        if not isinstance(price, (int, float)) or price <= 0:
            return jsonify({"error": "Invalid price"}), 400

        product = {
            "id": PRODUCT_ID_COUNTER,
            "name": name,
            "price": price,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
        }
        PRODUCTS[PRODUCT_ID_COUNTER] = product
        PRODUCT_ID_COUNTER += 1
        app.logger.info("Product '%s' created successfully.", name)
        return jsonify({"message": "Product created", "product": product}), 201

    @app.route("/login/<int:user_id>", methods=["POST"])
    def login(user_id: int) -> Any:
        if user_id not in USERS:
            return jsonify({"error": "Invalid user id"}), 400
        session["user_id"] = user_id
        return jsonify({"message": f"User {user_id} logged in."}), 200

    @app.route("/logout", methods=["POST"])
    def logout() -> Any:
        session.pop("user_id", None)
        app.logger.info("User logged out successfully.")
        return jsonify({"message": "User logged out successfully"}), 200

    @app.route("/cart/add", methods=["POST"])
    def add_to_cart() -> Any:
        user_id = session.get("user_id")
        data = request.get_json(silent=True) or {}
        product_id = data.get("product_id")
        quantity = data.get("quantity", 1)
        if not user_id:
            return jsonify({"error": "Login required"}), 401
        if product_id not in PRODUCTS:
            return jsonify({"error": "Invalid product ID"}), 400
        if not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"error": "Quantity must be positive"}), 400

        user_cart = CARTS[user_id]
        existing_item = next((item for item in user_cart if item["product_id"] == product_id), None)
        if existing_item:
            existing_item["quantity"] += quantity
        else:
            user_cart.append({"product_id": product_id, "quantity": quantity})
        CARTS[user_id] = user_cart
        app.logger.info("User %s added product %s to cart.", user_id, product_id)
        return jsonify({"message": "Added to cart"}), 200

    @app.route("/cart/remove", methods=["DELETE"])
    def remove_from_cart() -> Any:
        user_id = session.get("user_id")
        data = request.get_json(silent=True) or {}
        product_id = data.get("product_id")
        confirm = str(data.get("confirm", "false")).lower()
        if not user_id:
            return jsonify({"error": "Login required"}), 401
        if confirm != "true":
            return jsonify({"error": "Confirmation required"}), 400
        user_cart = CARTS.get(user_id, [])
        new_cart = [item for item in user_cart if item["product_id"] != product_id]
        if len(user_cart) == len(new_cart):
            return jsonify({"error": "Product not found in cart"}), 404
        CARTS[user_id] = new_cart
        app.logger.info("User %s removed product %s from cart.", user_id, product_id)
        total_price = sum(PRODUCTS[i["product_id"]]["price"] * i["quantity"] for i in new_cart)
        return jsonify({"message": "Product removed", "total_price": total_price}), 200

    @app.route("/cart", methods=["GET"])
    def view_cart() -> Any:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Login required"}), 401
        cart = CARTS.get(user_id, [])
        detailed = []
        for item in cart:
            product = PRODUCTS.get(item["product_id"])
            if product:
                detailed.append({
                    "product_id": product["id"],
                    "name": product["name"],
                    "quantity": item["quantity"],
                    "price": product["price"],
                    "total": product["price"] * item["quantity"]
                })
        total_price = sum(p["total"] for p in detailed)
        return jsonify({"items": detailed, "total_price": total_price}), 200

    @app.errorhandler(Exception)
    def handle_exception(e: Exception) -> Any:
        app.logger.error("Unhandled exception: %s", str(e), exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=5000, debug=False)