from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Transaction, db
from ai_services.transaction_analyzer import TransactionAnalyzer
from datetime import datetime
import logging

transaction_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')
logger = logging.getLogger(__name__)

@transaction_bp.route('', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get all transactions for the current user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'User not found'}), 404

    transactions = Transaction.query.filter_by(user_id=user_id).all()
    transaction_list = [t.to_dict() for t in transactions]

    return jsonify(transactions=transaction_list), 200

@transaction_bp.route('', methods=['POST'])
@jwt_required()
def add_transaction():
    """Add a new transaction for the current user."""
    data = request.get_json()
    user_id = get_jwt_identity()

    try:
        new_transaction = Transaction(
            user_id=user_id,
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            description=data['description'],
            amount=data['amount'],
            category=data['category']
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify(msg="Transaction added successfully"), 201
    except Exception as e:
        logger.error(f"Error adding transaction: {e}")
        return jsonify(msg="Error adding transaction"), 500


@transaction_bp.route('/insights', methods=['GET'])
@jwt_required()
def get_transaction_insights():
    """Get insights on the user's transactions."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'User not found'}), 404

    transactions = Transaction.query.filter_by(user_id=user_id).all()
    transaction_data = [t.to_dict() for t in transactions]

    if not transaction_data:
      return jsonify(message="No transactions to analyze"), 404

    try:
        analyzer = TransactionAnalyzer()
        current_month = datetime.now().strftime("%Y-%m") # Add current month
        insights = analyzer.analyze_spending_patterns(transaction_data, current_month)
        if insights is None:
           return jsonify(message="Could not generate insights"), 500

        insights = eval(insights)

        return jsonify(insights=insights), 200
    except Exception as e:
         logger.error(f"Error getting transaction insights: {e}")
         return jsonify(message=f"Error getting transaction insights: {e}"), 500