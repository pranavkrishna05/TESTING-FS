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