from flask import Blueprint, request, jsonify
from backend.models.products.product import Product
from backend.repositories.products.product_repository import ProductRepository
from backend import db

products = Blueprint('products', __name__)

@products.route('/add', methods=['POST'])
def add_product():
    data = request.get_json()

    name = data.get('name')
    price = data.get('price')
    description = data.get('description')

    if not name or ProductRepository.find_by_name(name):
        return jsonify({'message': 'Product name is required and must be unique'}), 400

    if price is None or price <= 0:
        return jsonify({'message': 'Product price must be a positive number'}), 400

    if not description:
        return jsonify({'message': 'Product description cannot be empty'}), 400

    new_product = Product(name=name, price=price, description=description)
    ProductRepository.save(new_product)
    db.session.commit()

    return jsonify({'message': 'Product added successfully'}), 201

@products.route('/update/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()

    if not data.get('is_admin', False):
        return jsonify({'message': 'Unauthorized'}), 403

    product = ProductRepository.find_by_id(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    name = data.get('name')
    price = data.get('price')
    description = data.get('description')

    if name and name != product.name:
        if ProductRepository.find_by_name(name):
            return jsonify({'message': 'Product name is required and must be unique'}), 400
        product.name = name

    if price is not None:
        if price <= 0:
            return jsonify({'message': 'Product price must be a positive number'}), 400
        product.price = price

    if description:
        product.description = description

    ProductRepository.save(product)
    db.session.commit()

    return jsonify({'message': 'Product updated successfully'}), 200

@products.route('/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    data = request.get_json()

    if not data.get('is_admin', False):
        return jsonify({'message': 'Unauthorized'}), 403

    product = ProductRepository.find_by_id(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    if not data.get('confirm', False):
        return jsonify({'message': 'Confirmation required'}), 400

    ProductRepository.delete(product)
    db.session.commit()

    return jsonify({'message': 'Product deleted successfully'}), 200

@products.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    products, total = ProductRepository.search(query, page, per_page)
    
    result = []
    for product in products:
        result.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description,
            'created_at': product.created_at,
            'updated_at': product.updated_at
        })

    return jsonify({
        'products': result,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200