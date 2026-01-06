from flask import Blueprint, request, jsonify
from backend.services.auth.user_service import UserService
from backend.models.user import User

user_bp = Blueprint('user', __name__)
user_service = UserService()

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if user_service.register_user(email, password):
        return jsonify({"message": "User registered successfully"}), 201
    return jsonify({"message": "User registration failed"}), 400

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    session = user_service.validate_user(email, password)
    if session:
        return jsonify({"message": "Login successful", "session_id": session.id}), 200
    
    user = user_service.get_user_by_email(email)
    if user:
        user_service.handle_failed_login(user)
    
    return jsonify({"message": "Invalid email or password"}), 401

@user_bp.route('/password_reset', methods=['POST'])
def password_reset():
    data = request.json
    email = data.get('email')

    password_reset = user_service.create_password_reset(email)
    if password_reset:
        # Here would be the place to send the reset token via email
        return jsonify({"message": "Password reset email sent", "token": password_reset.token}), 200
    return jsonify({"message": "User not found"}), 404

@user_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    token = data.get('token')
    new_password = data.get('new_password')

    if user_service.reset_password(token, new_password):
        return jsonify({"message": "Password reset successfully"}), 200
    return jsonify({"message": "Invalid or expired token"}), 400

@user_bp.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.json
    user = User(**data)

    user_service.update_user_profile(user)
    return jsonify({"message": "User profile updated successfully"}), 200