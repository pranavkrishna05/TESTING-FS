from flask import Blueprint, request, jsonify
from backend.services.categories.category_service import CategoryService

category_bp = Blueprint('category', __name__)
category_service = CategoryService()

@category_bp.route('/add', methods=['POST'])
def add_category():
    data = request.json
    name = data.get('name')
    parent_id = data.get('parent_id')

    if not name:
        return jsonify({"message": "Category name is required"}), 400

    category = category_service.add_category(name, parent_id)
    return jsonify({"message": "Category added successfully", "category_id": category.id}), 201

@category_bp.route('/update', methods=['POST'])
def update_category():
    data = request.json
    category_id = data.get('id')
    name = data.get('name')
    parent_id = data.get('parent_id')

    if not category_id:
        return jsonify({"message": "Category ID is required"}), 400

    success = category_service.update_category(category_id, name, parent_id)
    if success:
        return jsonify({"message": "Category updated successfully"}), 200
    return jsonify({"message": "Category not found"}), 404

@category_bp.route('/all', methods=['GET'])
def get_all_categories():
    categories = category_service.get_all_categories()
    return jsonify([category.dict() for category in categories]), 200