import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
from dotenv import load_dotenv
from models import Transaction, User, db
from routes.plaid_routes import plaid_bp
from routes.auth_routes import auth_bp
from routes.transactions_routes import transaction_bp
from plaid_integration import fetch_transactions
from ai_services import FinancialAdvisor, TransactionAnalyzer, BudgetAdvisor, SentimentAnalyzer
from routes.budget_routes import budget_bp
from routes.savings_routes import savings_bp
from flask_jwt_extended import JWTManager
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
    SESSION_COOKIE_DOMAIN=None,  # Allow cookies to work on localhost
    REMEMBER_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_DURATION=timedelta(days=7),
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///app.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    PLAID_CLIENT_ID=os.getenv('PLAID_CLIENT_ID'),
    PLAID_SECRET=os.getenv('PLAID_SECRET'),
    PLAID_ENV=os.getenv('PLAID_ENV', 'https://sandbox.plaid.com'),
    OPENAI_API_KEY=os.getenv('OPENAI_API_KEY'),
    JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key'),
    JWT_TOKEN_LOCATION=['headers', 'cookies'],
    JWT_HEADER_NAME="Authorization",
    JWT_HEADER_TYPE="Bearer",
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1),
    JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30),
    JWT_COOKIE_SECURE=False,
    JWT_COOKIE_CSRF_PROTECT=True,
    JWT_ACCESS_COOKIE_NAME='access_token_cookie',
    JWT_REFRESH_COOKIE_NAME='refresh_token_cookie',
    JWT_ACCESS_CSRF_COOKIE_NAME='csrf_access_token',
    JWT_REFRESH_CSRF_COOKIE_NAME='csrf_refresh_token',
    JWT_ACCESS_CSRF_HEADER_NAME='X-CSRF-TOKEN',
    JWT_REFRESH_CSRF_HEADER_NAME='X-CSRF-TOKEN',
    JWT_CSRF_IN_COOKIES=True,
    JWT_COOKIE_DOMAIN=None,
    JWT_ACCESS_CSRF_FIELD_NAME='csrf_token',
    JWT_REFRESH_CSRF_FIELD_NAME='csrf_token',
    JWT_CSRF_CHECK_FORM=False,
    JWT_CSRF_METHODS=['POST', 'PUT', 'PATCH', 'DELETE']
)

# Initialize JWT Manager
jwt = JWTManager(app)

# Initialize database
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# Initialize AI Services
ai_advisor = FinancialAdvisor()
transaction_analyzer = TransactionAnalyzer()
budget_advisor = BudgetAdvisor()
sentiment_analyzer = SentimentAnalyzer()

# Add CORS configuration
CORS(app,
     resources={r"/api/*": {"origins": ["http://localhost:3000"]}},
     supports_credentials=True)
# Logging Configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Update the plaid routes registration
app.register_blueprint(plaid_bp, url_prefix='/api/plaid')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(transaction_bp, url_prefix='/api/transactions')
app.register_blueprint(budget_bp, url_prefix='/api/budget')
app.register_blueprint(savings_bp, url_prefix='/api/savings')

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/api/transactions/sync', methods=['POST'])
@login_required
def sync_transactions():
    try:
        if not current_user.plaid_access_token:
            return jsonify({'error': 'No bank account connected'}), 400

        transactions = fetch_transactions(current_user.plaid_access_token)
        new_transactions = []

        for transaction in transactions:
            if not Transaction.query.filter_by(transaction_id=transaction['transaction_id']).first():
                new_transaction = Transaction(
                    user_id=current_user.id,
                    **transaction
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

@app.route('/api/ai_advice', methods=['GET'])
@login_required
def get_ai_advice():
    try:
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        transactions = Transaction.query.filter_by(user_id=current_user.id)\
            .filter(Transaction.date >= start_date)\
            .all()

        if not transactions:
            return jsonify({'advice': 'No transactions to analyze.'}), 200

        transaction_data = [t.to_dict() for t in transactions]
        analysis = transaction_analyzer.analyze_spending_patterns(transaction_data)
        advice = ai_advisor.get_financial_advice(analysis)

        return jsonify({
            'advice': advice,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error generating AI advice: {e}")
        return jsonify({'error': 'Failed to generate AI advice'}), 500

@app.route('/api/analyze_sentiment', methods=['POST'])
@login_required
def analyze_sentiment():
    try:
        description = request.json.get('description')
        if not description:
            return jsonify({'error': 'No description provided'}), 400
        
        sentiment = sentiment_analyzer.analyze_transaction_sentiment(description)
        return jsonify(sentiment), 200
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return jsonify({'error': 'Failed to analyze sentiment'}), 500

@app.route('/api/budget_recommendations', methods=['GET'])
@login_required
def get_budget_recommendations():
    try:
        transactions = Transaction.query.filter_by(user_id=current_user.id)\
            .order_by(Transaction.date.desc())\
            .limit(100)\
            .all()
        
        if not transactions:
            return jsonify({'recommendations': 'No transaction history available'}), 200
            
        spending_history = [t.to_dict() for t in transactions]
        recommendations = budget_advisor.get_budget_recommendations(spending_history)
        
        return jsonify({'recommendations': recommendations}), 200
    except Exception as e:
        logger.error(f"Error getting budget recommendations: {e}")
        return jsonify({'error': 'Failed to get budget recommendations'}), 500

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

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error("Error creating database tables: %s", e)
            raise
    app.run(debug=True, port=5000)