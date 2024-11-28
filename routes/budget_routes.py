from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Budget, db
from datetime import datetime

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budgets', methods=['GET'])
@login_required
def get_budgets():
    try:
        budgets = Budget.query.filter_by(user_id=current_user.id).all()
        return jsonify([b.to_dict() for b in budgets]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/budgets', methods=['POST'])
@login_required
def create_budget():
    try:
        data = request.json
        budget = Budget(
            user_id=current_user.id,
            category=data['category'],
            budget_limit=data['budget_limit'],
            created_at=datetime.now()
        )
        db.session.add(budget)
        db.session.commit()
        return jsonify(budget.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/budgets/<int:budget_id>', methods=['PUT'])
@login_required
def update_budget(budget_id):
    try:
        data = request.json
        budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()
        budget.budget_limit = data['budget_limit']
        db.session.commit()
        return jsonify(budget.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/budgets/<int:budget_id>', methods=['DELETE'])
@login_required
def delete_budget(budget_id):
    try:
        budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()
        db.session.delete(budget)
        db.session.commit()
        return jsonify({'message': 'Budget deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
