# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from visuals import generate_expense_charts
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user

from plaid_integration import (
    create_link_token,
    exchange_public_token,
    fetch_transactions,
    fetch_and_preprocess_transactions
)

# AI and utility imports
from openai_utils import generate_financial_advice
from datetime import datetime, timedelta, date
from models import User, Transaction, CustomIncome, UserIncome, UserCategoryPreference

# Additional imports
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

# Import db from extensions and models
from extensions import db  # Import db from extensions to avoid reinitializing it

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
app.config['SECRET_KEY'] = 'Rekajarekaja2020'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://finance_user:Rekaja20@localhost:5432/personal_finance_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 20,
    'pool_recycle': 280,
    'max_overflow': 0
}

# Initialize CORS
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:3050"}})

# Initialize db with the app
db.init_app(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'api_login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Load credentials from secrets.toml
config = toml.load("secrets.toml")
PLAID_CLIENT_ID = config["plaid"]["client_id"]
PLAID_SECRET = config["plaid"]["secret"]

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Additional setup and routes
# (Continue with the rest of your code here...)

def fetch_transactions_data(user):
    access_token = user.access_token  # Use the stored access token
    if not access_token:
        return []  # Return an empty list if access_token is not set

    try:
        # Set the date range for the past 30 days
        start_date = (datetime.now() - timedelta(days=30)).date()
        end_date = datetime.now().date()

        app.logger.debug(f"Using access token: {access_token}")
        app.logger.debug(f"Fetching transactions from {start_date} to {end_date}")

        # Fetch transactions using plaid_integration.py
        transactions = fetch_transactions(access_token, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        app.logger.debug(f"Transactions fetched from Plaid: {len(transactions)}")

        # Save transactions to the database
        for t in transactions:
            app.logger.debug(f"Processing transaction {t['name']} for {t['amount']}")
            # Check if the transaction already exists in the database
            existing_transaction = Transaction.query.filter_by(transaction_id=t['transaction_id']).first()
            if not existing_transaction:
                # Categorize the transaction if it is uncategorized
                category = t['category'][0] if t['category'] else categorize_transaction_with_openai(t['name'], t['amount'])

                new_transaction = Transaction(
                    user_id=user.id,
                    transaction_id=t['transaction_id'],
                    date=t['date'] if isinstance(t['date'], date) else datetime.strptime(t['date'], '%Y-%m-%d').date(),
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

def categorize_transaction_with_openai(transaction_name, transaction_amount):
    try:
        # Use OpenAI API to suggest a category
        user_input = f"Categorize this transaction based on its name and amount: '{transaction_name}', amount: ${transaction_amount}."
        response = generate_financial_advice(user_input)
        
        # Extract the category from the response (assuming the response is directly usable)
        category = response.strip()
        return category
    except Exception as e:
        app.logger.error(f"Error categorizing transaction with OpenAI: {e}")
        return 'Uncategorized'

@app.route('/api/income', methods=['GET', 'POST'])
def handle_income():
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
            type_ = data.get('type')

            if not all([source_name, amount, frequency, type_]):
                return jsonify({'error': 'Missing fields'}), 400

            new_income = CustomIncome(
                user_id=session['user_id'],
                source_name=source_name,
                amount=amount,
                frequency=frequency,
                type=type_
            )
            db.session.add(new_income)
            db.session.commit()

            return jsonify(new_income.to_dict()), 201
        except Exception as e:
            app.logger.error(f"Error adding income source: {e}")
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/income/<int:income_id>', methods=['PUT', 'DELETE'])
def modify_income(income_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        income = CustomIncome.query.filter_by(id=income_id, user_id=session['user_id']).first()
        if not income:
            return jsonify({'error': 'Income source not found'}), 404

        if request.method == 'PUT':
            data = request.get_json()
            income.source_name = data.get('source_name', income.source_name)
            income.amount = data.get('amount', income.amount)
            income.frequency = data.get('frequency', income.frequency)
            income.type = data.get('type', income.type)
            db.session.commit()
            return jsonify(income.to_dict()), 200

        elif request.method == 'DELETE':
            db.session.delete(income)
            db.session.commit()
            return jsonify({'message': 'Income source deleted'}), 200
    except Exception as e:
        app.logger.error(f"Error modifying income source: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    messages = []

    # Basic validation for missing fields
    if not username or not email or not password or not confirm_password:
        messages.append({'category': 'error', 'message': 'Please fill out all fields.'})
        return jsonify({'messages': messages}), 400

    # Check if passwords match
    if password != confirm_password:
        messages.append({'category': 'error', 'message': 'Passwords do not match.'})
        return jsonify({'messages': messages}), 400

    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        messages.append({'category': 'error', 'message': 'Username already exists.'})
        return jsonify({'messages': messages}), 400

    # Check if email already exists
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        messages.append({'category': 'error', 'message': 'An account with this email already exists.'})
        return jsonify({'messages': messages}), 400

    # Create new user instance and hash password
    new_user = User(username=username, email=email)
    new_user.set_password(password)  # Ensure this method hashes the password

    try:
        db.session.add(new_user)
        db.session.commit()
        messages.append({'category': 'success', 'message': 'Registration successful. Please log in.'})
        return jsonify({'messages': messages}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error during registration: {e}')
        messages.append({'category': 'error', 'message': 'An unexpected error occurred. Please try again later.'})
        return jsonify({'messages': messages}), 500

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500

# Serve other static files
@app.route('/<path:path>')
def static_proxy(path):
    if path.startswith('static/') or path in ['manifest.json', 'favicon.ico']:
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/current_user', methods=['GET'])
@login_required
def current_user_route():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email
        # Add other fields as needed
    }), 200

@app.route('/api/ai_advice', methods=['GET'])
def get_ai_advice():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        # Get recent transactions and account summary
        user_id = session['user_id']
        recent_transactions = Transaction.query.filter_by(user_id=user_id)\
            .order_by(Transaction.date.desc())\
            .limit(30).all()
        
        # Calculate spending patterns
        spending_by_category = {}
        for transaction in recent_transactions:
            if transaction.amount < 0:  # Only consider expenses
                category = transaction.category or 'Uncategorized'
                if category not in spending_by_category:
                    spending_by_category[category] = 0
                spending_by_category[category] += abs(transaction.amount)

        # Format transaction data for AI analysis
        transaction_summary = {
            'total_spending': sum(amt for amt in spending_by_category.values()),
            'categories': spending_by_category,
            'transaction_count': len(recent_transactions)
        }

        # Generate personalized advice using OpenAI
        prompt = f"""
        Based on the following financial data, provide personalized financial advice:
        
        Total Spending: ${transaction_summary['total_spending']}
        Spending by Category: {spending_by_category}
        
        Please provide:
        1. A main insight about the spending pattern
        2. 2-3 specific recommendations
        3. Key spending insights
        4. 2-4 actionable items
        
        Format the response as a JSON object with keys: mainInsight, recommendations, spendingInsights, actionItems
        """

        response = generate_financial_advice(prompt)
        
        # Parse the response and return structured advice
        return jsonify({
            'advice': response
        })

    except Exception as e:
        app.logger.error(f"Error generating AI advice: {e}")
        return jsonify({
            'error': 'Unable to generate advice at this time'
        }), 500

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
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                # Add other user fields if necessary
            },
            'transactions': [t.to_dict() for t in transactions],
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': net_balance,
        }

        app.logger.debug(f"Dashboard Data: {dashboard_data}")

        return jsonify(dashboard_data), 200
    except Exception as e:
        app.logger.error(f"Error fetching dashboard data: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/recent_transactions')
def recent_transactions():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        limit = int(request.args.get('limit', 8))
        offset = int(request.args.get('offset', 0))
        
        transactions = Transaction.query\
            .filter_by(user_id=session['user_id'])\
            .order_by(Transaction.date.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()

        return jsonify({
            'transactions': [{
                'date': t.date.strftime('%Y-%m-%d'),
                'name': t.name,
                'amount': float(t.amount),
                'category': t.category or 'Uncategorized'
            } for t in transactions]
        })

    except Exception as e:
        app.logger.error(f"Error fetching transactions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/filter_transactions', methods=['GET'])
def filter_transactions():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized access. Please log in.'}), 401

    try:
        # Extract start_date and end_date from query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not start_date_str or not end_date_str:
            return jsonify({'error': 'Start date and end date are required.'}), 400

        # Convert strings to date objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Query transactions within the date range for the logged-in user
        user = db.session.get(User, session.get('user_id'))
        filtered_transactions = Transaction.query.filter(
            Transaction.user_id == user.id,
            Transaction.date.between(start_date, end_date)
        ).order_by(Transaction.date.desc()).all()

        transactions_list = [
            {
                'date': t.date.strftime('%Y-%m-%d'),
                'name': t.name,
                'amount': t.amount,
                'category': t.category
            } for t in filtered_transactions
        ]

        return jsonify({'transactions': transactions_list})
    except Exception as e:
        app.logger.error(f"Error while filtering transactions: {e}")
        return jsonify({'error': 'An error occurred while filtering transactions.'}), 500

@app.route('/all_transactions')
def all_transactions():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        # Start a session and fetch the user by ID
        with db.session() as db_session:  # Renamed to avoid shadowing
            user = db_session.get(User, session['user_id'])

            # Get last year's transactions by default
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)

            transactions = db_session.query(Transaction).filter(
                Transaction.user_id == user.id,
                Transaction.date.between(start_date, end_date)
            ).order_by(Transaction.date.desc()).all()

            # Calculate monthly expenses
            monthly_expenses = calculate_monthly_expenses(transactions)

        return jsonify({
            'transactions': [transaction.to_dict() for transaction in transactions],
            'monthly_expenses': monthly_expenses
        })
    except Exception as e:
        app.logger.error(f"Error while fetching transactions: {e}")
        return jsonify({'error': 'An error occurred while fetching transactions.'}), 500

def calculate_monthly_expenses(transactions):
    # Group expenses by month and category
    monthly_data = {}
    for t in transactions:
        if t.amount < 0:  # Only consider expenses
            month = t.date.strftime('%Y-%m')
            if month not in monthly_data:
                monthly_data[month] = {}
            category = t.category or 'Miscellaneous'
            monthly_data[month][category] = monthly_data[month].get(category, 0) + abs(t.amount)
    
    # Calculate averages
    category_totals = {}
    num_months = max(len(monthly_data), 1)
    
    for month_data in monthly_data.values():
        for category, amount in month_data.items():
            category_totals[category] = category_totals.get(category, 0) + amount
    
    return {cat: total/num_months for cat, total in category_totals.items()}

@app.route('/add_income', methods=['POST'])
def add_income():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401

    try:
        income_source = request.form.get('income_source')
        income_amount = float(request.form.get('income_amount'))
        income_frequency = request.form.get('income_frequency')

        if not income_source or not income_amount:
            return jsonify({"success": False, "error": "Incomplete income data"}), 400

        user_id = session['user_id']
        new_income = CustomIncome(
            user_id=user_id,
            source_name=income_source,
            amount=income_amount,
            frequency=income_frequency
        )
        db.session.add(new_income)
        db.session.commit()

        # Calculate updated income totals for the user
        custom_income_sources = CustomIncome.query.filter_by(user_id=user_id).all()
        total_income = sum(source.amount for source in custom_income_sources)
        total_monthly_income = sum(
            source.amount for source in custom_income_sources if source.frequency == "monthly"
        )

        return jsonify({
            "success": True,
            "total_income": total_income,
            "total_monthly_income": total_monthly_income
        })
    except Exception as e:
        app.logger.error(f"Error adding income: {e}")
        db.session.rollback()
        return jsonify({"success": False, "error": "Internal Server Error"}), 500

@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/create_link_token', methods=['GET'])
def create_link_token_route():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in."}), 401
    try:
        link_token = create_link_token(user_id)
        return jsonify({"link_token": link_token}), 200
    except Exception as e:
        logging.error(f"Error creating link token: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/sync-bank', methods=['POST'])
def sync_bank_route():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "User not logged in."}), 401

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found."}), 404

        if not user.access_token:
            return jsonify({"error": "No access token available for user."}), 400

        # Define your date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)  # Example: last 30 days

        # Fetch transactions using plaid_integration.py
        transactions = fetch_transactions(user.access_token, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        # Process and save transactions
        for txn in transactions:
            transaction = Transaction(
                user_id=user.id,
                transaction_id=txn['transaction_id'],
                date=datetime.strptime(txn['date'], '%Y-%m-%d').date() if isinstance(txn['date'], str) else txn['date'],
                amount=txn['amount'],
                category=txn['category'][0] if txn['category'] else 'Uncategorized',
                name=txn['name']
            )
            db.session.add(transaction)
        db.session.commit()

        logging.debug("Bank data synced successfully.")
        return jsonify({"message": "Bank data synced successfully."}), 200

    except Exception as e:
        logging.error(f"Error syncing bank data: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
@app.route('/api/exchange_public_token', methods=['POST'])
def exchange_public_token_route():
    try:
        public_token = request.json.get('public_token')
        if not public_token:
            return jsonify({"error": "Public token is missing."}), 400

        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "User not logged in."}), 401

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found."}), 404

        # Exchange the public token for an access token
        access_token = exchange_public_token(public_token)
        if not access_token:
            return jsonify({"error": "Failed to exchange public token."}), 400

        # Save the access token to the user
        user.access_token = access_token
        db.session.commit()

        logging.debug("Access token saved successfully.")
        return jsonify({"message": "Access token saved"}), 200

    except Exception as e:
        app.logger.error(f"Error exchanging public token: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/update_charts')
def update_charts():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        period = request.args.get('period', 'monthly')
        user = db.session.get(User, session.get('user_id'))
        
        transactions = Transaction.query.filter_by(user_id=user.id).all()
        chart = generate_expense_charts(transactions, period)
        
        return jsonify({'category_chart': chart})
    except Exception as e:
        app.logger.error(f"Error updating charts: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/account_summary', methods=['GET'])
def fetch_account_summary():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User is not logged in.'}), 401

    try:
        # Fetch all transactions for the user
        transactions = Transaction.query.filter_by(user_id=user_id).all()
        
        # Calculate total income and expenses
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = sum(-t.amount for t in transactions if t.amount < 0)  # Negative for expenses

        # Assume net_balance is income minus expenses (you may adjust this logic)
        net_balance = total_income - total_expenses

        # Structure the summary data
        summary_data = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': net_balance
        }

        return jsonify(summary_data)
    except Exception as e:
        app.logger.error(f"Unexpected error in account summary: {e}")
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

@app.route('/api/transactions', methods=['GET'])
@login_required
def fetch_transactions_route():
    try:
        user = current_user
        start_date_str = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date_str = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        transactions = Transaction.query.filter(
            Transaction.user_id == user.id,
            Transaction.date.between(start_date, end_date)
        ).order_by(Transaction.date.desc()).all()

        transactions_data = [
            {
                'transaction_id': t.transaction_id,
                'name': t.name,
                'amount': float(t.amount),
                'date': t.date.strftime('%Y-%m-%d'),
                'category': t.category or 'Uncategorized'
            }
            for t in transactions
        ]

        return jsonify({'transactions': transactions_data}), 200
    except Exception as e:
        app.logger.error(f"Error fetching transactions: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/expenses_summary', methods=['GET'])
def get_expenses_summary():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    period = request.args.get('period', 'monthly')
    try:
        # Example logic for expenses summary
        if period == 'monthly':
            summary = {
                'total_expenses': 1500,
                'category_breakdown': {
                    'Housing': 800,
                    'Food': 400,
                    'Transportation': 300
                }
            }
        elif period == 'yearly':
            summary = {
                'total_expenses': 18000,
                'category_breakdown': {
                    'Housing': 9600,
                    'Food': 4800,
                    'Transportation': 3600
                }
            }
        else:
            return jsonify({'error': 'Invalid period specified'}), 400

        return jsonify(summary), 200
    except Exception as e:
        app.logger.error(f"Error fetching expenses summary: {e}")
        return jsonify({'error': str(e)}), 500

# Ensure you have a `to_dict` method in your CustomIncome model
# (Refer to the models.py example above)

# Run the Flask app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5028)