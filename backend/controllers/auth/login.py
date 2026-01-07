from flask import Blueprint, request, jsonify, session
from datetime import timedelta
from werkzeug.security import check_password_hash
from backend.models.users.user import User
from backend import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user is None or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    session['user_id'] = user.id
    session.permanent = True
    db.app.permanent_session_lifetime = timedelta(minutes=30)

    return jsonify({'message': 'Login successful', 'user_id': user.id}), 200

@auth.before_app_request
def make_session_permanent():
    session.permanent = True
    db.app.permanent_session_lifetime = timedelta(minutes=30)