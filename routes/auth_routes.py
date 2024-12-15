import logging
from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
from datetime import timedelta

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Handle user login with JWT token generation."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        logger.info(f"Login attempt for user: {username}")
        
        if not username or not password:
            return jsonify({'error': 'Missing username or password'}), 400
            
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            logger.info(f"Successful login for user: {username}")
            return jsonify(user.to_dict()), 200
        else:
            logger.warning(f"Failed login attempt for user: {username}")
            return jsonify({'error': 'Invalid username or password'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Handle user logout."""
    try:
        logout_user()
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Handle user registration."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if not username or not password or not email:
            return jsonify({'error': 'Missing required fields'}), 400
            
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
            
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
            
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user registered: {username}")
        return jsonify(user.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    try:
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        
        response = jsonify({'success': True})
        set_access_cookies(response, access_token)
        return response, 200
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}", exc_info=True)
        return jsonify({"error": "Error refreshing token"}), 500

@auth_bp.route('/current_user', methods=['GET'])
def get_current_user():
    """Get current user information."""
    if current_user.is_authenticated:
        return jsonify({
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'has_plaid_connection': current_user.has_plaid_connection
        }), 200
    return jsonify({'error': 'Not authenticated'}), 401