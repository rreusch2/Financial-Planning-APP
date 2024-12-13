import logging
from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, current_user
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
        if not data:
            logger.warning("No JSON data in login request")
            return jsonify({"error": "Missing login credentials"}), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            logger.warning("Missing username or password in login request")
            return jsonify({"error": "Username and password are required"}), 400

        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            logger.warning(f"Failed login attempt for username: {username}")
            return jsonify({"error": "Invalid username or password"}), 401

        # Create tokens
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "username": user.username,
                "email": user.email
            }
        )
        refresh_token = create_refresh_token(
            identity=str(user.id)
        )

        # Login user with Flask-Login
        login_user(user, remember=True)
        logger.info(f"Successful login for user: {username}")
        
        response = jsonify({
            "success": True,
            "user": user.to_dict()
        })

        # Set JWT cookies
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        
        return response, 200

    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({"error": "Server error occurred"}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required(optional=True)
def logout():
    """Handle user logout."""
    try:
        if current_user.is_authenticated:
            username = current_user.username
            logout_user()
            logger.info(f"User logged out: {username}")
        
        response = jsonify({"success": True})
        unset_jwt_cookies(response)
        return response, 200
    except Exception as e:
        logger.error(f"Logout error: {str(e)}", exc_info=True)
        return jsonify({"error": "Error during logout"}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Handle user registration."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing registration data"}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not all([username, email, password]):
            return jsonify({"error": "All fields are required"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 409

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 409

        new_user = User(
            username=username,
            email=email
        )
        new_user.password_hash = generate_password_hash(password)

        db.session.add(new_user)
        db.session.commit()

        logger.info(f"New user registered: {username}")
        return jsonify({"success": True, "message": "Registration successful"}), 201

    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({"error": "Server error occurred"}), 500

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
@jwt_required()
def get_current_user():
    """Get current user information."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify({
            "user": user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching current user: {str(e)}", exc_info=True)
        return jsonify({"error": "Error fetching user data"}), 500