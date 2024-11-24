# routes/__init__.py
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
transactions_bp = Blueprint('transactions', __name__)
plaid_bp = Blueprint('plaid', __name__)
dashboard_bp = Blueprint('dashboard', __name__)

# Import routes after blueprint creation to avoid circular imports
from routes.auth import *
from routes.transactions import *
from routes.plaid import *
from routes.dashboard import *