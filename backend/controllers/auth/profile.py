from flask import Blueprint, request, jsonify
from backend.models.users.user import User
from backend.repositories.users.user_repository import UserRepository
from backend import db

auth = Blueprint('auth', __name__)

@auth.route('/profile', methods=['GET'])
def get_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    user = UserRepository.find_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'email': user.email,
        'created_at': user.created_at,
        'updated_at': user.updated_at
    }), 200

@auth.route('/profile', methods=['PUT'])
def update_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    user = UserRepository.find_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if email:
        if UserRepository.find_by_email(email):
            return jsonify({'message': 'Email already in use'}), 400
        user.email = email

    if password:
        if len(password) < 8:
            return jsonify({'message': 'Password must be at least 8 characters long'}), 400
        user.set_password(password)

    UserRepository.save(user)
    db.session.commit()

    return jsonify({'message': 'Profile updated successfully'}), 200