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
        db.session.rollback()  # Add this line to roll back the transaction
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

def generate_insights(transactions):
    """Generate comprehensive financial insights from transactions."""
    if not transactions:
        return []
        
    insights = []
    
    # Convert transactions to dicts if they aren't already
    transaction_dicts = [t.to_dict() if hasattr(t, 'to_dict') else t for t in transactions]
    
    # Calculate total spending and income
    total_spending = sum(t['amount'] for t in transaction_dicts if t['amount'] > 0)
    total_income = abs(sum(t['amount'] for t in transaction_dicts if t['amount'] < 0))
    
    # Calculate spending by category with trends
    category_spending = {}
    category_trends = {}
    for t in transaction_dicts:
        if t['amount'] > 0:  # Only consider expenses
            category = t['category'] or 'Uncategorized'
            if category not in category_spending:
                category_spending[category] = []
            category_spending[category].append({
                'amount': t['amount'],
                'date': datetime.strptime(t['date'], '%Y-%m-%d') if isinstance(t['date'], str) else t['date']
            })
    
    # Calculate category trends and averages
    for category, transactions in category_spending.items():
        sorted_trans = sorted(transactions, key=lambda x: x['date'])
        if len(sorted_trans) >= 2:
            first_half = sum(t['amount'] for t in sorted_trans[:len(sorted_trans)//2])
            second_half = sum(t['amount'] for t in sorted_trans[len(sorted_trans)//2:])
            trend = ((second_half - first_half) / first_half) if first_half else 0
            category_trends[category] = trend
    
    # Generate summary insights
    savings_rate = ((total_income - total_spending) / total_income * 100) if total_income else 0
    insights.append({
        'type': 'summary',
        'message': f'Financial Summary',
        'details': [
            f'Total spending: ${total_spending:.2f}',
            f'Total income: ${total_income:.2f}',
            f'Savings rate: {savings_rate:.1f}%'
        ]
    })
    
    # Top spending categories with trends
    top_categories = sorted(
        [(cat, sum(t['amount'] for t in trans)) 
         for cat, trans in category_spending.items()],
        key=lambda x: x[1],
        reverse=True
    )[:3]
    
    if top_categories:
        insights.append({
            'type': 'categories',
            'message': 'Top Spending Categories:',
            'details': [
                f'{cat}: ${amt:.2f} ({get_trend_indicator(category_trends.get(cat, 0))})'
                for cat, amt in top_categories
            ]
        })
    
    # Large transactions
    large_transactions = [t for t in transaction_dicts if t['amount'] > 100]
    if large_transactions:
        insights.append({
            'type': 'large_transactions',
            'message': 'Recent Large Transactions:',
            'details': [
                f"{t['name']}: ${t['amount']:.2f} on {t['date']}"
                for t in sorted(large_transactions, key=lambda x: x['date'], reverse=True)[:3]
            ]
        })
    
    # Generate recommendations
    recommendations = generate_recommendations(
        total_spending, 
        total_income, 
        category_spending, 
        category_trends
    )
    if recommendations:
        insights.append({
            'type': 'recommendations',
            'message': 'Financial Recommendations:',
            'details': recommendations
        })
    
    return insights

def get_trend_indicator(trend):
    """Convert trend number to readable format."""
    if trend > 0.1:
        return '↑ Increasing'
    elif trend < -0.1:
        return '↓ Decreasing'
    else:
        return '→ Stable'

def generate_recommendations(total_spending, total_income, category_spending, category_trends):
    """Generate personalized financial recommendations."""
    recommendations = []
    
    # Check savings rate
    savings_rate = ((total_income - total_spending) / total_income * 100) if total_income else 0
    if savings_rate < 20:
        recommendations.append(
            "Consider increasing your savings rate to at least 20% of income"
        )
    
    # Analyze category trends
    for category, trend in category_trends.items():
        if trend > 0.2:  # Significant increase
            recommendations.append(
                f"Your spending in {category} has increased significantly. "
                "Consider reviewing this category for potential savings."
            )
    
    # Check for high-spending categories
    category_totals = {
        cat: sum(t['amount'] for t in trans)
        for cat, trans in category_spending.items()
    }
    
    if 'Entertainment' in category_totals and category_totals['Entertainment'] > total_income * 0.1:
        recommendations.append(
            "Entertainment spending is over 10% of income. "
            "Consider setting a budget for discretionary spending."
        )
    
    return recommendations

@app.route('/api/dashboard/insights', methods=['GET'])
@login_required
def get_dashboard_insights():
    try:
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

        # Get recent transactions with error handling
        try:
            transactions = Transaction.query.filter_by(user_id=current_user.id)\
                .order_by(Transaction.date.desc())\
                .limit(100)\
                .all()
            logger.info(f"Found {len(transactions)} transactions")
        except Exception as e:
            logger.error(f"Transaction query failed: {e}")
            return jsonify({'error': 'Failed to fetch transactions'}), 500

        # Return empty data if no transactions
        if not transactions:
            logger.info("No transactions found, returning empty data")
            return jsonify({
                'insights': {
                    'predictions': []
                },
                'recent_transactions': [],
                'spending_patterns': {
                    'trend': 0,
                    'categories': {},
                    'predictions': []
                }
            }), 200

        # Process transactions with error handling
        try:
            logger.info("Generating insights...")
            insights = generate_insights(transactions)
            logger.info("Generated insights successfully")
            
            logger.info("Calculating spending patterns...")
            spending_patterns = calculate_spending_patterns(transactions)
            logger.info("Calculated spending patterns successfully")
            
            response_data = {
                'insights': {
                    'predictions': insights
                },
                'recent_transactions': [t.to_dict() for t in transactions[:10]],
                'spending_patterns': spending_patterns
            }
            logger.info("Prepared response data successfully")
            
            return jsonify(response_data), 200
            
        except Exception as e:
            logger.error(f"Error processing insights: {e}", exc_info=True)  # Added exc_info for stack trace
            return jsonify({'error': 'Failed to process insights'}), 500

    except Exception as e:
        logger.error(f"Dashboard insights error: {e}", exc_info=True)  # Added exc_info for stack trace
        return jsonify({'error': str(e)}), 500

def calculate_spending_patterns(transactions):
    """Calculate comprehensive spending patterns and trends."""
    if not transactions:
        return {
            'trend': 0,
            'categories': {},
            'predictions': [],
            'monthly_analysis': {},
            'spending_velocity': 0
        }
    
    # Convert transactions to dicts if they aren't already
    transaction_dicts = [t.to_dict() if hasattr(t, 'to_dict') else t for t in transactions]
    
    # Group transactions by month and category
    monthly_data = {}
    categories = {}
    
    for t in transaction_dicts:
        if t['amount'] > 0:  # Only consider expenses
            # Monthly grouping
            date = datetime.strptime(t['date'], '%Y-%m-%d') if isinstance(t['date'], str) else t['date']
            month_key = date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'total': 0,
                    'categories': {}
                }
            monthly_data[month_key]['total'] += t['amount']
            
            # Category grouping
            category = t['category'] or 'Uncategorized'
            if category not in categories:
                categories[category] = []
            categories[category].append(t['amount'])
            
            # Update monthly category data
            if category not in monthly_data[month_key]['categories']:
                monthly_data[month_key]['categories'][category] = 0
            monthly_data[month_key]['categories'][category] += t['amount']
    
    # Calculate category averages and trends
    category_analysis = {}
    for category, amounts in categories.items():
        if amounts:  # Only process if there are amounts
            avg = sum(amounts) / len(amounts)
            std_dev = calculate_std_dev(amounts, avg)
            category_analysis[category] = {
                'average': avg,
                'std_dev': std_dev,
                'volatility': std_dev / avg if avg else 0
            }
    
    # Calculate overall trend
    months = sorted(monthly_data.keys())
    trend = 0
    
    if len(months) >= 4:  # Need at least 4 months for meaningful trend
        recent_months = months[-3:]  # Last 3 months
        older_months = months[:-3]   # Earlier months
        
        if older_months:  # Check if we have older months
            recent_avg = sum(monthly_data[m]['total'] for m in recent_months) / len(recent_months)
            older_avg = sum(monthly_data[m]['total'] for m in older_months) / len(older_months)
            
            trend = (recent_avg - older_avg) / older_avg if older_avg else 0
    
    # Calculate spending velocity (rate of change)
    velocity = 0
    if len(months) >= 2:
        first_month = monthly_data[months[0]]['total']
        last_month = monthly_data[months[-1]]['total']
        months_between = len(months)
        velocity = (last_month - first_month) / months_between if months_between else 0
    
    # Generate predictions
    predictions = predict_future_spending(monthly_data, category_analysis)
    
    return {
        'trend': trend,
        'categories': category_analysis,
        'predictions': predictions,
        'monthly_analysis': monthly_data,
        'spending_velocity': velocity
    }

def calculate_std_dev(values, mean):
    """Calculate standard deviation."""
    if len(values) < 2:
        return 0
    squared_diff_sum = sum((x - mean) ** 2 for x in values)
    return (squared_diff_sum / (len(values) - 1)) ** 0.5

def predict_future_spending(monthly_data, category_analysis):
    """Generate spending predictions using simple trend analysis."""
    predictions = []
    months = sorted(monthly_data.keys())
    
    if len(months) >= 3:
        # Calculate monthly growth rate
        monthly_totals = [monthly_data[m]['total'] for m in months]
        growth_rates = []
        
        # Calculate growth rates safely
        for i in range(1, len(monthly_totals)):
            if monthly_totals[i-1] != 0:  # Avoid division by zero
                growth_rate = (monthly_totals[i] - monthly_totals[i-1]) / monthly_totals[i-1]
                growth_rates.append(growth_rate)
        
        if growth_rates:  # Only proceed if we have growth rates
            avg_growth_rate = sum(growth_rates) / len(growth_rates)
            
            # Generate predictions for next 3 months
            last_total = monthly_totals[-1]
            for i in range(1, 4):
                predicted_amount = last_total * (1 + avg_growth_rate) ** i
                predictions.append({
                    'month': increment_month(months[-1], i),
                    'amount': predicted_amount,
                    'confidence': calculate_prediction_confidence(growth_rates)
                })
    
    return predictions

def increment_month(month_str, increment):
    """Increment a month string by a number of months."""
    year, month = map(int, month_str.split('-'))
    month += increment
    year += (month - 1) // 12
    month = ((month - 1) % 12) + 1
    return f"{year}-{month:02d}"

def calculate_prediction_confidence(growth_rates):
    """Calculate confidence level for predictions based on volatility."""
    if not growth_rates:
        return 0
    
    mean = sum(growth_rates) / len(growth_rates)
    std_dev = calculate_std_dev(growth_rates, mean)
    
    # Higher volatility = lower confidence
    confidence = 1 / (1 + std_dev)
    return min(max(confidence, 0), 1)  # Normalize to 0-1

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
        inspector = db.inspect(db.engine)
        columns = inspector.get_columns('transaction')
        column_names = [col['name'] for col in columns]
        
        expected_columns = [
            'id', 'user_id', 'transaction_id', 'account_id', 'date', 
            'name', 'amount', 'category', 'merchant_name', 'pending',
            'created_at', 'updated_at'
        ]
        
        missing = [col for col in expected_columns if col not in column_names]
        extra = [col for col in column_names if col not in expected_columns]
        
        return jsonify({
            'current_columns': column_names,
            'expected_columns': expected_columns,
            'missing_columns': missing,
            'extra_columns': extra,
            'schema_matches': not missing and not extra
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