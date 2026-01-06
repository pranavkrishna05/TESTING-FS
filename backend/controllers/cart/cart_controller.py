from flask import Blueprint, request, jsonify
from backend.services.shopping_cart.shopping_cart_service import ShoppingCartService

cart_bp = Blueprint('cart', __name__)
cart_service = ShoppingCartService()

@cart_bp.route('/add', methods=['POST'])
def add_item_to_cart():
    data = request.json
    user_id = data.get('user_id')
    session_id = data.get('session_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not product_id or not quantity:
        return jsonify({"message": "Product ID and quantity are required"}), 400

    cart_item = cart_service.add_item_to_cart(user_id, session_id, product_id, quantity)
    return jsonify({"message": "Item added to cart", "cart_item_id": cart_item.id}), 201

@cart_bp.route('/items', methods=['GET'])
def get_cart_items():
    user_id = request.args.get('user_id', type=int)
    session_id = request.args.get('session_id', type=str)

    if not user_id and not session_id:
        return jsonify({"message": "User ID or Session ID is required"}), 400

    cart_items = cart_service.get_cart_items(user_id, session_id)
    return jsonify([item.dict() for item in cart_items]), 200

@cart_bp.route('/remove', methods=['POST'])
def remove_item_from_cart():
    data = request.json
    cart_item_id = data.get('cart_item_id')

    if not cart_item_id:
        return jsonify({"message": "Cart Item ID is required"}), 400

    success = cart_service.remove_item_from_cart(cart_item_id)
    if success:
        total_price = cart_service.get_total_price(user_id=data.get('user_id'), session_id=data.get('session_id'))
        return jsonify({"message": "Item removed from cart", "total_price": total_price}), 200
    return jsonify({"message": "Item not found"}), 404

@cart_bp.route('/update_quantity', methods=['POST'])
def update_item_quantity():
    data = request.json
    cart_item_id = data.get('cart_item_id')
    quantity = data.get('quantity')

    if not cart_item_id or not quantity:
        return jsonify({"message": "Cart Item ID and quantity are required"}), 400

    if quantity <= 0:
        return jsonify({"message": "Quantity must be a positive integer"}), 400

    success = cart_service.update_item_quantity(cart_item_id, quantity)
    if success:
        total_price = cart_service.get_total_price(user_id=data.get('user_id'), session_id=data.get('session_id'))
        return jsonify({"message": "Quantity updated", "total_price": total_price}), 200
    return jsonify({"message": "Item not found"}), 404

@cart_bp.route('/total', methods=['GET'])
def get_total_price():
    user_id = request.args.get('user_id', type=int)
    session_id = request.args.get('session_id', type=str)

    if not user_id and not session_id:
        return jsonify({"message": "User ID or Session ID is required"}), 400

    total_price = cart_service.get_total_price(user_id, session_id)
    return jsonify({"total_price": total_price}), 200

@cart_bp.route('/save', methods=['POST'])
def save_user_cart():
    data = request.json
    user_id = data.get('user_id')
    session_id = data.get('session_id')

    if not user_id or not session_id:
        return jsonify({"message": "User ID and Session ID are required"}), 400

    cart_service.save_user_cart(user_id, session_id)
    return jsonify({"message": "Cart saved for user"}), 200