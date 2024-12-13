# Import necessary modules
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import Transaction
from datetime import datetime, timedelta
from sqlalchemy import func
import logging
from collections import defaultdict  # Add this import

# Create a logger
logger = logging.getLogger(__name__)

# Import your transaction analyzer service
from ai_services.transaction_analyzer import TransactionAnalyzer

# Define the Blueprint
transaction_bp = Blueprint('transaction_bp', __name__)

@transaction_bp.route('/analyze', methods=['POST'])
@login_required
def analyze_transaction():
    """Analyze a single transaction using AI."""
    try:
        data = request.get_json()
        description = data.get('description')
        amount = data.get('amount')

        if not description or amount is None:
            return jsonify({'error': 'Missing required fields'}), 400

        analysis = TransactionAnalyzer.categorize_transaction(description, amount)
        return jsonify(analysis), 200
    except Exception as e:
        logger.error(f"Error analyzing transaction: {e}")
        return jsonify({'error': 'Failed to analyze transaction'}), 500

@transaction_bp.route('/insights', methods=['GET'])
@login_required
def get_transaction_insights():
    """Get AI-powered insights for all transactions."""
    try:
        # Get transactions from the last 90 days
        start_date = (datetime.now() - timedelta(days=90)).date()
        transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date
        ).all()

        if not transactions:
            return jsonify({'message': 'No transactions to analyze'}), 200

        transaction_data = [t.to_dict() for t in transactions]
        analyzer = TransactionAnalyzer()
        insights = analyzer.analyze_spending_patterns(transaction_data)
        logger.debug(f"AI Response: {insights}")

        categories = analyzer._group_by_category(transaction_data)
        predictions = analyzer._generate_predictions(transaction_data)
        
        response = {
            'insights': insights,
            'categories': categories,
            'predictions': predictions
        }
        logger.debug(f"Sending response: {response}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting transaction insights: {e}", exc_info=True)
        return jsonify({'error': 'Failed to get insights'}), 500
    
@transaction_bp.route('/budget/recommendations', methods=['GET'])
@login_required
def get_budget_recommendations():
    """Get AI-powered budget recommendations."""
    try:
        # Get monthly income
        income = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.amount > 0
        ).with_entities(func.sum(Transaction.amount)).scalar() or 0

        # Get spending history
        transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.amount < 0
        ).all()

        recommendations = TransactionAnalyzer.get_smart_budget_recommendations(
            [t.to_dict() for t in transactions],
            income
        )

        return jsonify(recommendations), 200
    except Exception as e:
        logger.error(f"Error getting budget recommendations: {e}")
        return jsonify({'error': 'Failed to get budget recommendations'}), 500