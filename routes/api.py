# routes/api.py
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Transaction, User

# Create blueprint
api = Blueprint('api', __name__)

@api.route('/income', methods=['GET'])
@login_required
def get_income():
    try:
        transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.amount > 0
        ).all()
        
        total_income = sum(t.amount for t in transactions)
        return jsonify({
            "total_income": total_income,
            "transactions": [t.to_dict() for t in transactions]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add more routes here...