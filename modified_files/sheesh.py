import os
import logging
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify, send_from_directory
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
from dotenv import load_dotenv
import toml
from models import Transaction, User, db
from routes.plaid_routes import plaid_bp
from routes.auth_routes import auth_bp
from routes.transactions_routes import transaction_bp
from plaid_integration import fetch_and_preprocess_transactions
from ai_integration import AIFinancialAdvisor
import numpy as np
from routes.budget_routes import budget_bp
from routes.savings_routes import savings_bp
from typing import List, Dict

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='frontend/dist', static_url_path='/')

# Application Configuration
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'your_super_secret_key'),
    SESSION_COOKIE_SECURE=False,  # Set to True in production
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    REMEMBER_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_DURATION=timedelta(days=7),
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'postgresql://raunch:rekaja20@localhost:5432/RaunchData'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    PLAID_CLIENT_ID=os.getenv('PLAID_CLIENT_ID'),
    PLAID_SECRET=os.getenv('PLAID_SECRET'),
    PLAID_ENV=os.getenv('PLAID_ENV', 'https://sandbox.plaid.com'),  # Updated to full URL
    OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')
)

# Initialize Extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
ai_advisor = AIFinancialAdvisor()
# Initialize CORS with specific origins
CORS(app,
     resources={r"/api/*": {"origins": os.getenv('FRONTEND_URL', 'http://localhost:3000')}},
     supports_credentials=True)


# Logging Configuration
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Register blueprints
app.register_blueprint(plaid_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(transaction_bp, url_prefix='/api')
app.register_blueprint(budget_bp, url_prefix='/api')
app.register_blueprint(savings_bp, url_prefix='/api')
# Load Plaid credentials from environment or secrets file
try:
    config = toml.load("secrets.toml")
    app.config.update(
        PLAID_CLIENT_ID=config.get('PLAID_CLIENT_ID'),
        PLAID_SECRET=config.get('PLAID_SECRET')
    )
except Exception as e:
    logger.warning("Could not load secrets.toml: %s. Using environment variables.", e)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/api/current_user', methods=['GET'])
@login_required
def get_current_user():
    """Fetch details of the currently authenticated user."""
    try:
        return jsonify({
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'has_plaid_connection': current_user.has_plaid_connection
        }), 200
    except Exception as e:
        logger.error("Error fetching current user: %s", e)
        return jsonify({'error': 'Failed to fetch current user'}), 500
    
@app.route('/api/check_bank_connection', methods=['GET'])
@login_required
def check_bank_connection():
    """Check if the user has a bank connection."""
    try:
        return jsonify({'has_plaid_connection': current_user.has_plaid_connection}), 200
    except Exception as e:
        logger.error(f"Error checking bank connection: {e}")
        return jsonify({'error': 'Failed to check bank connection'}), 500


@app.route('/api/account_summary', methods=['GET'])
@login_required
def account_summary():
    """Return account summary for authenticated user."""
    try:
        transactions = Transaction.query.filter_by(user_id=current_user.id).all()

        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
        net_balance = total_income - total_expenses

        logger.debug(f"Account Summary for User {current_user.id}: "
                     f"Income: {total_income}, Expenses: {total_expenses}, Net Balance: {net_balance}")

        return jsonify({
            'total_income': round(total_income, 2),
            'total_expenses': round(total_expenses, 2),
            'net_balance': round(net_balance, 2),
            'has_plaid_connection': current_user.has_plaid_connection
        }), 200
    except Exception as e:
        logger.error("Error fetching account summary: %s", e)
        return jsonify({'error': 'Failed to fetch account summary'}), 500


@app.before_request
def handle_options_request():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        headers = response.headers

        # Add CORS headers
        headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Requested-With"
        headers["Access-Control-Allow-Credentials"] = "true"

        return response

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Requested-With"
    return response


@app.route('/api/transactions/sync', methods=['POST'])
@login_required
def sync_transactions():
    try:
        if not current_user.plaid_access_token:
            return jsonify({'error': 'No bank account connected'}), 400

        transactions = fetch_and_preprocess_transactions(current_user.plaid_access_token)
        new_transactions = []

        for transaction in transactions:
            if not Transaction.query.filter_by(transaction_id=transaction['transaction_id']).first():
                new_transaction = Transaction(
                    user_id=current_user.id,
                    **transaction  # Unpack transaction details
                )
                db.session.add(new_transaction)
                new_transactions.append(new_transaction)

        db.session.commit()
        return jsonify({
            'message': 'Transactions synced successfully',
            'new_transactions': len(new_transactions)
        }), 200

    except Exception as e:
        logger.error(f"Error syncing transactions: {e}")
        return jsonify({'error': 'Failed to sync transactions'}), 500




    
@app.route('/api/recent_transactions', methods=['GET'])
@login_required
def recent_transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc())\
        .limit(5)\
        .all()
    
    # Add AI categorization for uncategorized transactions
    for transaction in transactions:
        if transaction.category == 'Uncategorized':
            advisor = AIFinancialAdvisor()
            ai_category = advisor.enhance_transaction_categorization(transaction.name)
            transaction.ai_category = ai_category
    
    transaction_dicts = [t.to_dict() for t in transactions]
    logger.debug(f"Recent Transactions for User {current_user.id}: {transaction_dicts}")
    return jsonify([t.to_dict() for t in transactions]), 200


@app.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        transactions_query = Transaction.query.filter_by(user_id=current_user.id)\
            .filter(Transaction.date >= start_date, Transaction.date <= end_date)\
            .order_by(Transaction.date.desc())

        total_transactions = transactions_query.count()
        transactions = transactions_query.offset((page - 1) * per_page).limit(per_page).all()

        # Log the data being returned
        logger.debug(f"Transactions response: {[t.to_dict() for t in transactions]}")

        return jsonify({
            "transactions": [t.to_dict() for t in transactions],
            "total_transactions": total_transactions,
            "total_pages": (total_transactions + per_page - 1) // per_page
        }), 200
    except Exception as e:
        logger.error(f"Error fetching transactions: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch transactions'}), 500



@app.route('/api/chart_data', methods=['GET'])
@login_required
def chart_data():
    """Generate spending data for charts."""
    try:
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        transactions = Transaction.query.filter_by(user_id=current_user.id)\
            .filter(Transaction.date >= start_date, Transaction.date <= end_date)\
            .all()

        category_data = {}
        for transaction in transactions:
            category = transaction.category or "Uncategorized"
            category_data[category] = category_data.get(category, 0) + transaction.amount

        logger.debug(f"Chart data for User {current_user.id}: {category_data}")
        return jsonify(category_data), 200
    except Exception as e:
        logger.error(f"Error generating chart data: {e}", exc_info=True)
        return jsonify({'error': 'Failed to generate chart data'}), 500


@app.route('/api/categorize-transaction', methods=['POST'])
def categorize_transaction():
    try:
        data = request.get_json()
        transaction_name = data.get('transaction_name')
        if not transaction_name:
            return jsonify({'error': 'Transaction name is required'}), 400

        # Get AI categorization
        ai_category = ai_advisor.enhance_transaction_categorization(transaction_name)

        return jsonify({
            'category': ai_category.get('category'),
            'confidence': ai_category.get('confidence'),
            'additional_info': ai_category.get('additional_info', {})
        }), 200
    except Exception as e:
        logger.error(f"Error categorizing transaction: {e}", exc_info=True)
        return jsonify({'error': 'Failed to categorize transaction'}), 500


@app.route('/api/analyze-spending', methods=['POST'])
def analyze_spending():
    try:
        data = request.get_json()
        transactions = data.get('transactions', [])
        
        analysis = ai_advisor.analyze_spending_patterns(transactions)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/forecast', methods=['POST'])
def forecast():
    data = request.json
    initial_value = data['initial_value']
    mean_return = data['mean_return']
    volatility = data['volatility']
    time_horizon = data['time_horizon']
    steps_per_year = data.get('steps_per_year', 252)
    num_simulations = data.get('num_simulations', 100)

    gbm = tff.models.GenericItoProcess(
        drift_fn=lambda t, x: mean_return * tf.ones_like(x),
        volatility_fn=lambda t, x: volatility * tf.ones_like(x)
    )

    times = np.linspace(0.0, time_horizon, time_horizon * steps_per_year)
    samples = gbm.sample_paths(
        initial_state=[initial_value],
        times=times,
        num_samples=num_simulations,
        seed=42
    )

    final_values = samples[:, -1, 0].numpy().tolist()
    return jsonify({
        "final_values": final_values,
        "mean_value": np.mean(final_values),
        "time_points": times.tolist(),
        "sample_paths": samples.numpy().tolist()
    })


@app.route("/api/code-review", methods=["POST"])
def code_review():
    # Path to your project files
    project_path = "C:/Users/reidr/OneDrive/Desktop/APP/Financial-Planning-APP"
    results = review_code(project_path)
    return jsonify(results)

@app.route('/api/ai_advice', methods=['GET'])
@login_required
def get_ai_advice():
    try:
        # Get transactions from the last 90 days for better analysis
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        transactions = Transaction.query.filter_by(user_id=current_user.id)\
            .filter(Transaction.date >= start_date)\
            .all()

        if not transactions:
            return jsonify({'advice': 'No transactions to analyze.'}), 200

        transaction_data = [t.to_dict() for t in transactions]
        ai_response = ai_advisor.analyze_spending_patterns(transaction_data)

        # Extract the enhanced analysis components
        return jsonify({
            'analysis': ai_response.get('analysis'),
            'spending_data': ai_response.get('spending_data'),
            'trends': ai_response.get('trends'),
            'unusual_transactions': ai_response.get('unusual_transactions'),
            'recurring_expenses': ai_response.get('recurring_expenses'),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error generating AI advice: {e}")
        return jsonify({'error': 'Failed to generate AI advice'}), 500
    
@app.route('/api/category_analysis', methods=['GET'])
@login_required
def get_category_analysis():
    try:
        category = request.args.get('category')
        start_date = request.args.get('start_date', 
            (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', 
            datetime.now().strftime('%Y-%m-%d'))

        transactions = Transaction.query.filter_by(
            user_id=current_user.id,
            category=category
        ).filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()

        transaction_data = [t.to_dict() for t in transactions]
        
        # Calculate category statistics
        amounts = [abs(t['amount']) for t in transaction_data]
        stats = {
            'total': sum(amounts),
            'average': np.mean(amounts) if amounts else 0,
            'max': max(amounts) if amounts else 0,
            'min': min(amounts) if amounts else 0,
            'count': len(amounts),
            'std_dev': np.std(amounts) if amounts else 0
        }

        return jsonify({
            'statistics': stats,
            'transactions': transaction_data
        }), 200
    except Exception as e:
        logger.error(f"Error analyzing category: {e}")
        return jsonify({'error': 'Failed to analyze category'}), 500


@app.route('/api/transaction_insights', methods=['POST'])
@login_required
def get_transaction_insights():
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        
        transaction = Transaction.query.filter_by(
            user_id=current_user.id,
            transaction_id=transaction_id
        ).first()
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404

        # Get enhanced transaction analysis
        insights = ai_advisor.enhance_transaction_categorization(
            transaction.name,
            transaction.category
        )
        
        return jsonify(insights), 200
    except Exception as e:
        logger.error(f"Error getting transaction insights: {e}")
        return jsonify({'error': 'Failed to get transaction insights'}), 500
    
@app.route('/api/spending_forecast', methods=['GET'])
@login_required
def get_spending_forecast():
    try:
        # Get historical spending data
        transactions = Transaction.query.filter_by(user_id=current_user.id)\
            .filter(Transaction.amount < 0)\
            .order_by(Transaction.date.desc())\
            .all()

        if not transactions:
            return jsonify({'error': 'No transaction history available'}), 400

        # Group transactions by month
        monthly_spending = {}
        for transaction in transactions:
            month_key = transaction.date.strftime('%Y-%m')
            if month_key not in monthly_spending:
                monthly_spending[month_key] = 0
            monthly_spending[month_key] += abs(transaction.amount)

        # Calculate trend and forecast
        months = sorted(monthly_spending.keys())
        spending_values = [monthly_spending[m] for m in months]
        
        # Simple linear trend (you could make this more sophisticated)
        x = np.arange(len(spending_values))
        z = np.polyfit(x, spending_values, 1)
        p = np.poly1d(z)
        
        # Forecast next 3 months
        next_months = []
        next_month = datetime.strptime(months[-1], '%Y-%m')
        for i in range(1, 4):
            next_month = (next_month + timedelta(days=32)).replace(day=1)
            next_months.append(next_month.strftime('%Y-%m'))
        
        forecast_values = p(np.arange(len(spending_values), len(spending_values) + 3))

        return jsonify({
            'historical': {
                'months': months,
                'values': spending_values
            },
            'forecast': {
                'months': next_months,
                'values': forecast_values.tolist()
            }
        }), 200
    except Exception as e:
        logger.error(f"Error generating spending forecast: {e}")
        return jsonify({'error': 'Failed to generate forecast'}), 500

@app.route('/api/dashboard_data', methods=['GET'])
@login_required
def get_dashboard_data():
    try:
        # Get recent transactions
        recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
            .order_by(Transaction.date.desc())\
            .limit(5)\
            .all()

        # Get account summary
        transactions = Transaction.query.filter_by(user_id=current_user.id).all()
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
        net_balance = total_income - total_expenses

        # Get AI insights
        transaction_data = [t.to_dict() for t in transactions]
        ai_response = ai_advisor.analyze_spending_patterns(transaction_data)

        return jsonify({
            'summary': {
                'total_income': round(total_income, 2),
                'total_expenses': round(total_expenses, 2),
                'net_balance': round(net_balance, 2)
            },
            'recent_transactions': [t.to_dict() for t in recent_transactions],
            'ai_insights': {
                'analysis': ai_response.get('analysis'),
                'trends': ai_response.get('trends'),
                'unusual_transactions': ai_response.get('unusual_transactions'),
                'recurring_expenses': ai_response.get('recurring_expenses')
            },
            'has_plaid_connection': current_user.has_plaid_connection
        }), 200
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        return jsonify({'error': 'Failed to fetch dashboard data'}), 500        

        
@app.route('/api/analyze_sentiment', methods=['POST'])
@login_required
def analyze_sentiment():
    try:
        description = request.json.get('description')
        if not description:
            return jsonify({'error': 'No description provided'}), 400
        
        from nlp_integration import analyze_transaction_sentiment
        sentiment = analyze_transaction_sentiment(description)
        return jsonify({'description': description, 'sentiment': sentiment}), 200
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return jsonify({'error': 'Failed to analyze sentiment'}), 500


@app.route('/api/get_user_id', methods=['GET'])
@login_required
def get_user_id():
    """Return the ID of the currently authenticated user."""
    return jsonify({'user_id': current_user.id}), 200


# Serve React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
    
 


# Error Handlers
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'API route not found'}), 404
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(500)
def internal_error(error):
    logger.error("Internal server error: %s", error)
    return jsonify({'error': 'Internal Server Error'}), 500



# Server startup
if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error("Error creating database tables: %s", e)
            raise
    app.run(debug=True, port=5000)