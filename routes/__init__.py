from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__)
plaid_bp = Blueprint('plaid', __name__)
transaction_bp = Blueprint('transaction', __name__)

# Initialize other variables
__all__ = ['auth_bp', 'plaid_bp', 'transaction_bp']