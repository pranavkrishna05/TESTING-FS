from flask import Blueprint, request, jsonify
from backend.services.products.product_service import ProductService

product_bp = Blueprint('product', __name__)
product_service = ProductService()

@product_bp.route('/add', methods=['POST'])
def add_product():
    data = request.json
    name = data.get('name')
    price = data.get('price')
    description = data.get('description')
    category_id = data.get('category_id')

    if not all([name, price, description, category_id]):
        return jsonify({"message": "Name, price, description, and category_id are required"}), 400

    existing_product = product_service.get_product_by_name(name)
    if existing_product:
        return jsonify({"message": "Product with this name already exists"}), 400

    product = product_service.add_product(name, price, description, category_id)
    return jsonify({"message": "Product added successfully", "product_id": product.id}), 201

@product_bp.route('/update', methods=['POST'])
def update_product():
    data = request.json
    product_id = data.get('id')
    name = data.get('name')
    price = data.get('price')
    description = data.get('description')
    category_id = data.get('category_id')

    if not product_id:
        return jsonify({"message": "Product ID is required"}), 400

    if price is not None and not isinstance(price, (float, int)):
        return jsonify({"message": "Price must be a numeric value"}), 400

    success = product_service.update_product(product_id, name, price, description, category_id)
    if success:
        return jsonify({"message": "Product updated successfully"}), 200
    return jsonify({"message": "Product not found"}), 404

@product_bp.route('/delete', methods=['POST'])
def delete_product():
    data = request.json
    product_id = data.get('id')

    if not product_id:
        return jsonify({"message": "Product ID is required"}), 400

    success = product_service.delete_product(product_id)
    if success:
        return jsonify({"message": "Product deleted successfully"}), 200
    return jsonify({"message": "Product not found"}), 404

@product_bp.route('/all', methods=['GET'])
def get_all_products():
    products = product_service.get_all_products()
    return jsonify([product.dict() for product in products]), 200

@product_bp.route('/search', methods=['GET'])
def search_products():
    term = request.args.get('term', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    products = product_service.search_products(term, page, per_page)
    return jsonify([product.dict() for product in products]), 200