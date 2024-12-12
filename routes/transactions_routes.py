from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta
from models import Transaction, db
import logging

logger = logging.getLogger(__name__)
transaction_bp = Blueprint('transactions', __name__)

@transaction_bp.route('/summary', methods=['GET'])
@login_required
def get_transaction_summary():
    """Get transaction summary for dashboard."""
    try:
        # Get transactions from the last 30 days
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Get all transactions for the period
        transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= thirty_days_ago
        ).all()

        # Calculate totals
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = abs(sum(t.amount for t in transactions if t.amount < 0))
        net_balance = total_income - total_expenses

        # Get recent transactions
        recent_transactions = sorted(
            transactions, 
            key=lambda x: x.date, 
            reverse=True
        )[:10]

        logger.info(f"Generated summary for user {current_user.id}")

        return jsonify({
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'net_balance': float(net_balance),
            'recent_transactions': [t.to_dict() for t in recent_transactions],
            'ai_insights': None  # Will be implemented later
        }), 200

    except Exception as e:
        logger.error(f"Error getting transaction summary: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get transaction summary'}), 500