import logging
from flask import Blueprint, jsonify, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Handle user login."""
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

        login_user(user, remember=True)
        logger.info(f"Successful login for user: {username}")
        
        return jsonify({
            "success": True,
            "user": user.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({"error": "Server error occurred"}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Handle user logout."""
    try:
        username = current_user.username
        logout_user()
        logger.info(f"User logged out: {username}")
        return jsonify({"success": True}), 200
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

@auth_bp.route('/current_user', methods=['GET'])
@login_required
def get_current_user():
    """Get current user information."""
    try:
        return jsonify({
            "user": current_user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching current user: {str(e)}", exc_info=True)
        return jsonify({"error": "Error fetching user data"}), 500