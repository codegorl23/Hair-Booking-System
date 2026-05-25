from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from app import db
from app.models.user import User
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


# Access Control:
# POST /auth/register   - No auth required - Public
# POST /auth/login      - No auth required - Public

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('role'):
        return jsonify({'error': 'email, password, and role are required'}), 400
    if data['role'] not in ['stylist', 'client']:
        return jsonify({'error': 'role must be stylist or client'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    user = User(email=data['email'], role=data['role'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'email and password are required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        logger.warning(f"Failed login attempt for email: {data.get('email')}")
        return jsonify({'error': 'Invalid email or password'}), 401
    token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role}
    )

    logger.info(f"Login successful: user_id={user.id} role={user.role}")
    return jsonify({'access_token': token, 'role': user.role}), 200