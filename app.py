import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from sqlalchemy import desc
import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from openai import openai
import toml


from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin

from visuals import generate_expense_charts
from plaid_integration import create_link_token, exchange_public_token, fetch_transactions, fetch_and_preprocess_transactions, fetch_and_process_transactions
from openai_utils import generate_financial_advice
from datetime import datetime, timedelta, date
from models import Transaction, db
import plaid
from plaid.api import plaid_api
from sqlalchemy import desc
from plaid.exceptions import ApiException

# Add these imports at the top
from models import User, CustomIncome  # Add User import
from plaid.configuration import Configuration
from plaid.api_client import ApiClient


import io
import base64
import toml
import openai
import joblib
from gtts import gTTS
import os
import logging
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
from extensions import db  # Import db from extensions to avoid reinitializing it
from openai_utils import generate_financial_advice, generate_transaction_category
import plaid

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
app.config['SECRET_KEY'] = 'Rekajarekaja2020'  # Keep your existing secret key
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session lasts 7 days
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)

CORS(app, 
     supports_credentials=True,
     resources={r"/api/*": {
         "origins": ["http://localhost:3000"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "expose_headers": ["Content-Range", "X-Content-Range"],
         "supports_credentials": True
     }}
)


logger = logging.getLogger(__name__)

def init_plaid_client(app):
    """
    Initialize the Plaid client and attach it to the Flask app instance.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        None
    """
    try:
        configuration = Configuration(
            host=Configuration.DEFAULT_HOST,
            api_key={
                'clientId': PLAID_CLIENT_ID,
                'secret': PLAID_SECRET,
            }
        )
        api_client = ApiClient(configuration)
        app.plaid_client = plaid_api.PlaidApi(api_client)
    except ApiException as e:
        logging.error(f"An error occurred while initializing the Plaid client: {e}")
# Add this after app initialization
init_plaid_client(app)


# Initialize db with the app
db.init_app(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))



# Load credentials from secrets.toml
config = toml.load("secrets.toml")
PLAID_CLIENT_ID = config["plaid"]["client_id"]
PLAID_SECRET = config["plaid"]["secret"]

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Utility functions


def fetch_transactions_data(user):
    access_token = user.access_token
    if not access_token:
        return []

    try:
        start_date = (datetime.now() - timedelta(days=30)).date()
        end_date = datetime.now().date()

        app.logger.debug(f"Using access token: {access_token}")
        transactions = fetch_transactions(access_token, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        app.logger.debug(f"Transactions fetched from Plaid: {len(transactions)}")

        for t in transactions:
            existing_transaction = Transaction.query.filter_by(transaction_id=t['transaction_id']).first()
            if not existing_transaction:
                category = t['category'][0] if t['category'] else 'Uncategorized'

                new_transaction = Transaction(
                    user_id=user.id,
                    transaction_id=t['transaction_id'],
                    date=datetime.strptime(t['date'], '%Y-%m-%d').date(),
                    name=t['name'],
                    amount=t['amount'],
                    category=category
                )
                db.session.add(new_transaction)

        db.session.commit()
        return transactions
    except Exception as e:
        app.logger.error(f"Error fetching transactions: {e}")
        return []

def fetch_bank_transactions(access_token):
    client = plaid_api.PlaidApi(plaid.Client(client_id='your_client_id', secret='your_secret', environment='sandbox'))
    
    try:
        response = client.TransactionsGet({
            'access_token': access_token,
            'start_date': '2023-01-01',
            'end_date': '2024-11-18',
        })
        transactions = response['transactions']
        return transactions
    except Exception as e:
        app.logger.error(f"Error fetching transactions: {e}")
        return []

# Routes


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user, remember=True)  # Enable remember me
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/create_link_token', methods=['GET'])
@login_required
def create_link_token_route():
    try:
        # Use current_user.id instead of session
        link_token = create_link_token(str(current_user.id))
        return jsonify({"link_token": link_token}), 200
    except Exception as e:
        app.logger.error(f"Error creating link token: {e}")
        return jsonify({"error": str(e)}), 500




@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not username or not email or not password or not confirm_password:
        return jsonify({'error': 'All fields are required'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'error': 'User already exists'}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error during registration: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Add a route to check authentication status
@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email
            }
        }), 200
    return jsonify({'authenticated': False}), 401

@app.route('/api/dashboard', methods=['GET'])
@login_required
def get_dashboard_data():
    try:
        user = current_user
        transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.date.desc()).all()

        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = sum(-t.amount for t in transactions if t.amount < 0)
        net_balance = total_income - total_expenses

        dashboard_data = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': net_balance,
            'transactions': [t.to_dict() for t in transactions],
        }

        return jsonify(dashboard_data), 200
    except Exception as e:
        app.logger.error(f"Error fetching dashboard data: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
    

from plaid_integration import fetch_and_preprocess_transactions

# Update sync_transactions route to use the proper Plaid client
@app.route('/api/transactions/sync', methods=['POST'])
@login_required
def sync_transactions():
    try:
        if not current_user.plaid_access_token:
            return jsonify({'error': 'No bank account connected'}), 400

        # Fetch new transactions from Plaid using the proper client
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Use the correct Plaid client method
        response = current_app.plaid_client.transactions_get(
            access_token=current_user.plaid_access_token,
            start_date=start_date,
            end_date=end_date
        )
        
        transactions = response['transactions']
        new_transactions_count = 0
        
        for transaction in transactions:
            existing = Transaction.query.filter_by(
                transaction_id=transaction['transaction_id']
            ).first()
            
            if not existing:
                new_transaction = Transaction(
                    user_id=current_user.id,
                    transaction_id=transaction['transaction_id'],
                    date=datetime.strptime(transaction['date'], '%Y-%m-%d'),
                    name=transaction['name'],
                    amount=float(transaction['amount']),
                    category=transaction['category'][0] if transaction.get('category') else 'Uncategorized'
                )
                db.session.add(new_transaction)
                new_transactions_count += 1

        db.session.commit()

        return jsonify({
            'message': f'Successfully synced {new_transactions_count} new transactions',
            'new_transactions_count': new_transactions_count
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error syncing transactions: {str(e)}")
        return jsonify({'error': 'Failed to sync transactions'}), 500


@app.route('/api/transactions/categories', methods=['GET'])
@login_required
def get_transaction_categories():
    """
    Get list of unique transaction categories for the current user
    """
    try:
        categories = db.session.query(Transaction.category)\
            .filter(Transaction.user_id == current_user.id)\
            .distinct()\
            .all()
        
        return jsonify({
            'categories': [category[0] for category in categories if category[0]]
        }), 200

    except Exception as e:
        logger.error(f"Error fetching transaction categories: {str(e)}")
        return jsonify({'error': 'Failed to fetch categories'}), 500


@app.route('/api/create_link_token', methods=['GET'])
def create_link_token_route():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    try:
        link_token = create_link_token(user_id)
        return jsonify({"link_token": link_token}), 200
    except Exception as e:
        app.logger.error(f"Error creating link token: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/api/exchange_public_token', methods=['POST'])
@login_required
def exchange_public_token():
    try:
        data = request.json
        public_token = data.get('public_token')
        if not public_token:
            return jsonify({'error': 'Public token is required.'}), 400
        
        access_token = exchange_public_token(public_token)  # From plaid_integration.py
        current_user.plaid_access_token = access_token
        db.session.commit()

        return jsonify({'message': 'Access token saved successfully.'}), 200
    except Exception as e:
        app.logger.error(f"Error exchanging public token: {e}")
        return jsonify({'error': 'Internal server error.'}), 500



@app.route('/api/income', methods=['GET', 'POST'])
def handle_income_route():  # Change the function name here
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    if request.method == 'GET':
        try:
            incomes = CustomIncome.query.filter_by(user_id=session['user_id']).all()
            incomes_data = [income.to_dict() for income in incomes]
            return jsonify(incomes_data), 200
        except Exception as e:
            app.logger.error(f"Error fetching income sources: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()
            source_name = data.get('source_name')
            amount = data.get('amount')
            frequency = data.get('frequency')

            if not all([source_name, amount, frequency]):
                return jsonify({'error': 'Missing fields'}), 400

            new_income = CustomIncome(
                user_id=session['user_id'],
                source_name=source_name,
                amount=amount,
                frequency=frequency
            )
            db.session.add(new_income)
            db.session.commit()

            return jsonify(new_income.to_dict()), 201
        except Exception as e:
            app.logger.error(f"Error adding income source: {e}")
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/api/ai_advice', methods=['GET'])
def get_ai_advice():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Generate personalized financial advice
        advice = {
            "mainInsight": "You are spending a lot on dining out.",
            "recommendations": ["Cook at home more often", "Set a dining out budget"],
            "spendingInsights": ["Dining: $300", "Groceries: $200"],
            "actionItems": ["Limit dining out to $150", "Plan weekly meals"]
        }
        return jsonify(advice), 200
    except Exception as e:
        app.logger.error(f"Error generating AI advice: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
    
@app.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    """
    Fetch transactions with filtering, sorting, and pagination.
    Query parameters:
    - start_date: Filter transactions from this date (YYYY-MM-DD)
    - end_date: Filter transactions until this date (YYYY-MM-DD)
    - category: Filter by transaction category
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    - sort: Sort field (date, amount, category)
    - order: Sort order (asc, desc)
    """
    try:
        # Get query parameters with defaults
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        sort_field = request.args.get('sort', 'date')
        sort_order = request.args.get('order', 'desc')
        
        # Date filtering
        try:
            start_date = datetime.strptime(request.args.get('start_date', ''), '%Y-%m-%d') if request.args.get('start_date') else datetime.now() - timedelta(days=30)
            end_date = datetime.strptime(request.args.get('end_date', ''), '%Y-%m-%d') if request.args.get('end_date') else datetime.now()
        except ValueError as e:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Build query
        query = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.date.between(start_date, end_date)
        )

        # Category filtering
        category = request.args.get('category')
        if category:
            query = query.filter(Transaction.category == category)

        # Sorting
        if sort_field not in ['date', 'amount', 'category', 'name']:
            return jsonify({'error': 'Invalid sort field'}), 400
        
        sort_column = getattr(Transaction, sort_field)
        if sort_order == 'desc':
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)

        # Execute paginated query
        paginated_transactions = query.paginate(
            page=page, 
            per_page=per_page,
            error_out=False
        )

        # Calculate summary statistics
        total_income = sum(t.amount for t in paginated_transactions.items if t.amount > 0)
        total_expenses = sum(abs(t.amount) for t in paginated_transactions.items if t.amount < 0)

        # Prepare response
        transactions_data = [{
            'id': t.id,
            'transaction_id': t.transaction_id,
            'date': t.date.strftime('%Y-%m-%d'),
            'name': t.name,
            'amount': float(t.amount),
            'category': t.category
        } for t in paginated_transactions.items]

        return jsonify({
            'transactions': transactions_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': paginated_transactions.pages,
                'total_items': paginated_transactions.total
            },
            'summary': {
                'total_income': float(total_income),
                'total_expenses': float(total_expenses),
                'net_amount': float(total_income - total_expenses)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        return jsonify({'error': 'Failed to fetch transactions'}), 500


# Remove duplicate route and keep the more comprehensive version
@app.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    """
    Fetch transactions with filtering, sorting, and pagination.
    Query parameters:
    - start_date: Filter transactions from this date (YYYY-MM-DD)
    - end_date: Filter transactions until this date (YYYY-MM-DD)
    - category: Filter by transaction category
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    - sort: Sort field (date, amount, category)
    - order: Sort order (asc, desc)
    """
    try:
        # Get query parameters with defaults
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        sort_field = request.args.get('sort', 'date')
        sort_order = request.args.get('order', 'desc')
        
        # Date filtering
        try:
            start_date = datetime.strptime(request.args.get('start_date', ''), '%Y-%m-%d') if request.args.get('start_date') else datetime.now() - timedelta(days=30)
            end_date = datetime.strptime(request.args.get('end_date', ''), '%Y-%m-%d') if request.args.get('end_date') else datetime.now()
        except ValueError as e:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Build query
        query = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.date.between(start_date, end_date)
        )

        # Category filtering
        category = request.args.get('category')
        if category:
            query = query.filter(Transaction.category == category)

        # Sorting
        if sort_field not in ['date', 'amount', 'category', 'name']:
            return jsonify({'error': 'Invalid sort field'}), 400
        
        sort_column = getattr(Transaction, sort_field)
        if sort_order == 'desc':
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)

        # Execute paginated query
        paginated_transactions = query.paginate(
            page=page, 
            per_page=per_page,
            error_out=False
        )

        # Calculate summary statistics
        total_income = sum(t.amount for t in paginated_transactions.items if t.amount > 0)
        total_expenses = sum(abs(t.amount) for t in paginated_transactions.items if t.amount < 0)

        # Prepare response
        transactions_data = [{
            'id': t.id,
            'transaction_id': t.transaction_id,
            'date': t.date.strftime('%Y-%m-%d'),
            'name': t.name,
            'amount': float(t.amount),
            'category': t.category
        } for t in paginated_transactions.items]

        return jsonify({
            'transactions': transactions_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': paginated_transactions.pages,
                'total_items': paginated_transactions.total
            },
            'summary': {
                'total_income': float(total_income),
                'total_expenses': float(total_expenses),
                'net_amount': float(total_income - total_expenses)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        return jsonify({'error': 'Failed to fetch transactions'}), 500

@app.route('/api/expenses_summary', methods=['GET'])
@login_required
def get_expenses_summary():
    try:
        user = current_user
        # Example summary logic
        total_expenses = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.amount < 0
        ).scalar() or 0

        category_breakdown = db.session.query(
            Transaction.category, db.func.sum(Transaction.amount)
        ).filter(
            Transaction.user_id == user.id,
            Transaction.amount < 0
        ).group_by(Transaction.category).all()

        summary = {
            'total_expenses': abs(total_expenses),
            'category_breakdown': {
                category or 'Uncategorized': abs(amount) for category, amount in category_breakdown
            }
        }

        return jsonify(summary), 200
    except Exception as e:
        app.logger.error(f"Error fetching expenses summary: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500



# Static and Error Handling
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'API route not found'}), 404
    return send_from_directory(app.static_folder, 'index.html')


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5028)
