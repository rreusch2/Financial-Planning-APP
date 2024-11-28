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

# Initialize CORS with specific origins
CORS(app,
     resources={r"/api/*": {"origins": "http://localhost:3000"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     expose_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

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

@app.route('/api/account_summary', methods=['GET'])
@login_required
def account_summary():
    """Return account summary for authenticated user."""
    try:
        transactions = Transaction.query.filter_by(user_id=current_user.id).all()
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
        net_balance = total_income - total_expenses

        return jsonify({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': net_balance,
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
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Requested-With"
    return response

# Pagination for Transaction Syncing
@app.route('/api/transactions/sync', methods=['POST'])
@login_required
def sync_transactions():
    """Sync bank transactions using Plaid with pagination."""
    try:
        if not current_user.plaid_access_token:
            return jsonify({'error': 'No bank account connected'}), 400

        # Fetch transactions with pagination
        transactions = fetch_and_preprocess_transactions(current_user.plaid_access_token)
        new_transactions_count = 0

        for transaction in transactions:
            # Check for duplicates
            if not Transaction.query.filter_by(transaction_id=transaction['transaction_id']).first():
                # Log each transaction
                logger.info(f"New transaction: {transaction['name']} on {transaction['date']} for {transaction['amount']}")

                # Create new transaction entry
                new_transaction = Transaction(
                    user_id=current_user.id,
                    transaction_id=transaction['transaction_id'],
                    date=datetime.fromisoformat(transaction['date']),
                    name=transaction['name'],
                    amount=transaction['amount'],
                    category=transaction.get('category', 'Uncategorized'),
                    merchant_name=transaction.get('merchant_name'),
                    pending=transaction.get('pending', False)
                )
                db.session.add(new_transaction)
                new_transactions_count += 1

        # Update last sync time
        current_user.last_plaid_sync = datetime.now(timezone.utc)
        db.session.commit()

        return jsonify({
            'message': 'Transactions synced successfully',
            'new_transactions': new_transactions_count
        }), 200
    except Exception as e:
        logger.error("Error syncing transactions: %s", e)
        db.session.rollback()
        return jsonify({'error': 'Failed to sync transactions'}), 500

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


@app.route('/api/ai_advice', methods=['GET'])
@login_required
def get_ai_advice():
    logger.debug("Received request for AI advice.")  # Log request start
    try:
        transactions = Transaction.query.filter_by(user_id=current_user.id) \
            .order_by(Transaction.date.desc()) \
            .limit(50) \
            .all()
        logger.debug(f"Fetched {len(transactions)} transactions for user {current_user.id}.")  # Log data fetched

        if not transactions:
            logger.info("No transactions found for analysis.")
            return jsonify({'advice': 'No transactions available for analysis.'}), 200

        transaction_data = [t.to_dict() for t in transactions]
        logger.debug(f"Prepared transaction data for AI analysis: {transaction_data}")  # Log prepared data

        advisor = AIFinancialAdvisor(api_key=app.config['OPENAI_API_KEY'])
        response = advisor.analyze_spending_patterns(transaction_data)
        logger.debug(f"AI advice response: {response}")  # Log AI response

        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error generating AI advice: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
        
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
    """Handle 404 errors."""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'API route not found'}), 404
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
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
    app.run(debug=True, port=5028)