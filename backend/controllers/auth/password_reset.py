from flask import Blueprint, request, jsonify, url_for
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from backend.models.users.user import User
from backend.services.auth.email_service import EmailService
from backend.repositories.users.user_repository import UserRepository
from backend import db

auth = Blueprint('auth', __name__)
s = URLSafeTimedSerializer('ThisIsASecret!')

@auth.route('/password_reset/request', methods=['POST'])
def password_reset_request():
    data = request.get_json()
    email = data.get('email')

    user = UserRepository.find_by_email(email)

    if user is None:
        return jsonify({'message': 'Email not found'}), 404

    token = s.dumps(email, salt='password-reset-salt')
    reset_url = url_for('auth.password_reset_token', token=token, _external=True)
    EmailService.send_email(email, 'Password Reset Request', f'Click the link to reset your password: {reset_url}')

    return jsonify({'message': 'Password reset link sent'}), 200

@auth.route('/password_reset/confirm/<token>', methods=['POST'])
def password_reset_token(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=86400)
    except SignatureExpired:
        return jsonify({'message': 'The password reset link has expired'}), 400
    except BadSignature:
        return jsonify({'message': 'Invalid token'}), 400

    data = request.get_json()
    new_password = data.get('password')

    if len(new_password) < 8:
        return jsonify({'message': 'Password must be at least 8 characters long'}), 400

    user = UserRepository.find_by_email(email)
    user.set_password(new_password)
    UserRepository.save(user)

    return jsonify({'message': 'Password has been reset successfully'}), 200