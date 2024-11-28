from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timezone
from models import Transaction, db
import logging

logger = logging.getLogger(__name__)

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/income', methods=['GET'])
@login_required
def get_income():
    """Get user's income transactions."""
    try:
        transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.amount > 0
        ).all()

        total_income = sum(t.amount for t in transactions)
        logger.info(f"Fetched {len(transactions)} income transactions for user {current_user.id}")

        return jsonify({
            'total_income': total_income,
            'transactions': [t.to_dict() for t in transactions],
            'status': 'success'
        }), 200
    except Exception as e:
        logger.error("Error fetching income transactions: %s", e, exc_info=True)
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/expenses_summary', methods=['GET'])
@login_required
def get_expenses_summary():
    """Get summary of user's expenses."""
    try:
        period = request.args.get('period', 'monthly')
        today = datetime.now(timezone.utc)

        if period == 'monthly':
            start_date = datetime(today.year, today.month, 1, tzinfo=timezone.utc)
        elif period == 'yearly':
            start_date = datetime(today.year, 1, 1, tzinfo=timezone.utc)
        else:
            return jsonify({'error': 'Invalid period'}), 400

        expenses = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.amount < 0,
            Transaction.date >= start_date
        ).all()

        expenses_by_category = {}
        for expense in expenses:
            category = expense.category or 'Uncategorized'
            if category not in expenses_by_category:
                expenses_by_category[category] = 0
            expenses_by_category[category] += abs(expense.amount)

        logger.info(f"Fetched {len(expenses)} expenses for user {current_user.id}")

        return jsonify({
            'total_expenses': sum(abs(e.amount) for e in expenses),
            'expenses_by_category': expenses_by_category,
            'period': period
        }), 200
    except Exception as e:
        logger.error("Error fetching expenses summary: %s", e, exc_info=True)
        return jsonify({'error': str(e)}), 500

# Modify categorization logic in transaction_routes.py
@transaction_bp.route('/transactions', methods=['GET'])
@login_required
def get_transactions():
    print("GET /api/transactions route hit")
    
    try:
        transactions = Transaction.query.filter_by(user_id=current_user.id).all()

        for transaction in transactions:
            if transaction.amount < 0:
                transaction.type = "Expense"
            else:
                transaction.type = "Income"

        db.session.commit()

        return jsonify({
            'transactions': [t.to_dict() for t in transactions]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

