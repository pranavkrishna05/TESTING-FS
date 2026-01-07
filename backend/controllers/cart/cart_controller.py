from flask import Blueprint, request, jsonify, session
from backend.models.cart.cart import Cart, CartItem
from backend.models.products.product import Product
from backend.repositories.cart.cart_repository import CartRepository
from backend import db

cart = Blueprint('cart', __name__)

@cart.route('/add', methods=['POST'])
def add_product_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    user_id = session.get('user_id')
    session_id = session.sid

    if user_id:
        cart = CartRepository.find_or_create_by_user(user_id)
    else:
        cart = CartRepository.find_or_create_by_session(session_id)

    cart_item = CartRepository.find_item(cart, product_id)
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        CartRepository.save_item(cart_item)

    db.session.commit()

    return jsonify({'message': 'Product added to cart successfully'}), 200

@cart.route('/items', methods=['GET'])
def get_cart_items():
    user_id = session.get('user_id')
    session_id = session.sid

    if user_id:
        cart = CartRepository.find_by_user(user_id)
    else:
        cart = CartRepository.find_by_session(session_id)

    if not cart:
        return jsonify({'message': 'Cart is empty'}), 200

    items = []
    for item in cart.items:
        items.append({
            'product_id': item.product_id,
            'quantity': item.quantity,
            'name': item.product.name,
            'price': item.product.price
        })

    return jsonify({'items': items}), 200

@cart.route('/remove', methods=['DELETE'])
def remove_product_from_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    confirm = data.get('confirm', False)

    if not confirm:
        return jsonify({'message': 'Confirmation required'}), 400

    user_id = session.get('user_id')
    session_id = session.sid

    if user_id:
        cart = CartRepository.find_by_user(user_id)
    else:
        cart = CartRepository.find_by_session(session_id)

    if not cart:
        return jsonify({'message': 'Cart is empty'}), 404

    cart_item = CartRepository.find_item(cart, product_id)
    if not cart_item:
        return jsonify({'message': 'Product not found in cart'}), 404

    CartRepository.delete_item(cart_item)
    db.session.commit()

    return jsonify({'message': 'Product removed from cart successfully'}), 200