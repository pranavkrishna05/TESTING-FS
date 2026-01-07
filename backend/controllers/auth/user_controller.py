from flask import Blueprint, request, jsonify, session
from backend.models.users.user import User
from backend.repositories.users.user_repository import UserRepository
from backend import db

users = Blueprint('users', __name__)

@users.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if UserRepository.find_by_username(username):
        return jsonify({'message': 'Username already exists'}), 400

    if UserRepository.find_by_email(email):
        return jsonify({'message': 'Email already exists'}), 400

    new_user = User(username=username, email=email, password=password)
    UserRepository.save(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@users.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = UserRepository.find_by_username(username)
    if not user or user.password != password:
        return jsonify({'message': 'Invalid credentials'}), 401

    session['user_id'] = user.id

    return jsonify({'message': 'Login successful'}), 200

@users.route('/logout', methods=['POST'])
def logout_user():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'}), 200

@users.route('/profile', methods=['GET'])
def get_user_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    user = UserRepository.find_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at,
        'updated_at': user.updated_at
    }), 200