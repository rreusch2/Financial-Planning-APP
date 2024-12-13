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
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
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

@app.route('/api/dashboard/insights', methods=['GET'])
@login_required
def get_dashboard_insights():
    try:
        # First verify the user
        if not current_user or not current_user.is_authenticated:
            logger.error("User not authenticated")
            return jsonify({'error': 'Authentication required'}), 401

        logger.info(f"Getting insights for user {current_user.id}")
        
        # Test database connection
        try:
            db.session.execute(text('SELECT 1'))
            db.session.commit()
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return jsonify({'error': 'Database connection error'}), 500

        # Return empty data if no transactions
        transactions = Transaction.query.filter_by(user_id=current_user.id)\
            .order_by(Transaction.date.desc())\
            .limit(100)\
            .all()

        if not transactions:
            return jsonify({
                'insights': {'predictions': []},
                'recent_transactions': [],
                'spending_patterns': {
                    'trend': 0,
                    'categories': {},
                    'predictions': []
                }
            }), 200

        # Process transactions
        return jsonify({
            'insights': {
                'predictions': generate_insights(transactions)
            },
            'recent_transactions': [t.to_dict() for t in transactions[:10]],
            'spending_patterns': calculate_spending_patterns(transactions)
        }), 200

    except Exception as e:
        logger.error(f"Dashboard insights error: {e}")
        return jsonify({'error': str(e)}), 500

def calculate_spending_trend(transactions):
    """Calculate spending trend percentage change."""
    try:
        if not transactions:
            return 0
            
        # Group transactions by month
        monthly_totals = {}
        for t in transactions:
            month = t.date.strftime('%Y-%m')
            monthly_totals[month] = monthly_totals.get(month, 0) + float(t.amount)

        # Get the last two months
        sorted_months = sorted(monthly_totals.keys())
        if len(sorted_months) < 2:
            return 0

        current_month = monthly_totals[sorted_months[-1]]
        previous_month = monthly_totals[sorted_months[-2]]

        # Calculate percentage change
        if previous_month == 0:
            return 0
        return round(((current_month - previous_month) / abs(previous_month)) * 100, 2)
    except Exception as e:
        logger.error("Error calculating spending trend: %s", e)
        return 0

def get_category_breakdown(transactions):
    """Get spending breakdown by category."""
    try:
        categories = {}
        for t in transactions:
            category = t.category or 'Uncategorized'
            categories[category] = categories.get(category, 0) + abs(float(t.amount))
        return {k: round(v, 2) for k, v in categories.items()}
    except Exception as e:
        logger.error("Error getting category breakdown: %s", e)
        return {}

def generate_spending_predictions(transactions):
    """Generate simple spending predictions."""
    try:
        if not transactions:
            return []

        # Calculate average monthly spending
        monthly_totals = {}
        for t in transactions:
            month = t.date.strftime('%Y-%m')
            monthly_totals[month] = monthly_totals.get(month, 0) + abs(float(t.amount))

        avg_spending = sum(monthly_totals.values()) / len(monthly_totals) if monthly_totals else 0

        # Generate predictions for next 3 months
        predictions = []
        current_date = datetime.now()
        for i in range(1, 4):
            future_date = current_date + timedelta(days=30 * i)
            predictions.append({
                'date': future_date.strftime('%Y-%m'),
                'amount': round(avg_spending * (1 + (i * 0.02)), 2)  # Assume 2% increase each month
            })
        return predictions
    except Exception as e:
        logger.error("Error generating spending predictions: %s", e)
        return []

@app.route('/api/debug/db-status', methods=['GET'])
@login_required
def check_db_status():
    try:
        # Check if tables exist
        user_table = db.inspect(db.engine).has_table("user")
        transaction_table = db.inspect(db.engine).has_table("transaction")
        
        # Get table schemas
        inspector = db.inspect(db.engine)
        user_columns = [col['name'] for col in inspector.get_columns('user')] if user_table else []
        transaction_columns = [col['name'] for col in inspector.get_columns('transaction')] if transaction_table else []
        
        return jsonify({
            'status': 'ok',
            'tables': {
                'user': {
                    'exists': user_table,
                    'columns': user_columns
                },
                'transaction': {
                    'exists': transaction_table,
                    'columns': transaction_columns
                }
            }
        }), 200
    except Exception as e:
        logger.error(f"Error checking database status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/auth-check', methods=['GET'])
@login_required
def auth_check():
    try:
        return jsonify({
            'user_id': current_user.id,
            'authenticated': current_user.is_authenticated,
            'db_connection': db.session.is_active
        }), 200
    except Exception as e:
        logger.error(f"Auth check error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/db-schema', methods=['GET'])
@login_required
def check_db_schema():
    try:
        inspector = db.inspect(db.engine)
        columns = inspector.get_columns('transaction')
        return jsonify({
            'columns': [col['name'] for col in columns]
        }), 200
    except Exception as e:
        logger.error(f"Error checking schema: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/verify-schema', methods=['GET'])
@login_required
def verify_schema():
    try:
        # Get the actual database schema
        inspector = db.inspect(db.engine)
        actual_columns = {col['name'] for col in inspector.get_columns('transaction')}
        
        # Get the expected columns from our model
        model_columns = {col.key for col in Transaction.__table__.columns}
        
        return jsonify({
            'actual_columns': list(actual_columns),
            'model_columns': list(model_columns),
            'missing_columns': list(model_columns - actual_columns),
            'extra_columns': list(actual_columns - model_columns)
        }), 200
    except Exception as e:
        logger.error(f"Schema verification error: {e}")
        return jsonify({'error': str(e)}), 500

# Add this temporary route to fix the schema
@app.route('/api/debug/fix-schema', methods=['GET'])
@login_required
def fix_schema():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE transaction 
                ADD COLUMN IF NOT EXISTS account_id VARCHAR(100)
            """))
            conn.commit()
        return jsonify({'message': 'Schema fixed successfully'}), 200
    except Exception as e:
        logger.error(f"Schema fix error: {e}")
        return jsonify({'error': str(e)}), 500

# Add this temporary route to recreate the table
@app.route('/api/debug/recreate-table', methods=['GET'])
@login_required
def recreate_table():
    try:
        with db.engine.connect() as conn:
            # Drop existing table
            conn.execute(text('DROP TABLE IF EXISTS "transaction" CASCADE'))
            conn.execute(text("""
                CREATE TABLE "transaction" (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    transaction_id VARCHAR(100) NOT NULL UNIQUE,
                    account_id VARCHAR(100),
                    category VARCHAR(100),
                    date DATE NOT NULL,
                    name VARCHAR(200),
                    amount FLOAT NOT NULL,
                    pending BOOLEAN DEFAULT FALSE,
                    CONSTRAINT fk_user
                        FOREIGN KEY(user_id)
                        REFERENCES "user"(id)
                        ON DELETE CASCADE
                );
                CREATE INDEX ix_transaction_user_id ON "transaction" (user_id);
                CREATE INDEX ix_transaction_date ON "transaction" (date);
            """))
            conn.commit()
            
        # Verify the schema after recreation
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('transaction')]
        logger.info(f"Table recreated with columns: {columns}")
            
        return jsonify({
            'message': 'Table recreated successfully',
            'columns': columns
        }), 200
    except Exception as e:
        logger.error(f"Table recreation error: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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

# After app configuration:
try:
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    logger.info("Database connection successful")
except SQLAlchemyError as e:
    logger.error(f"Database connection failed: {e}")