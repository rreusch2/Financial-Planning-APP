from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import SavingsGoal, db
from datetime import datetime

savings_bp = Blueprint('savings', __name__)

@savings_bp.route('/savings', methods=['GET'])
@login_required
def get_savings_goals():
    try:
        goals = SavingsGoal.query.filter_by(user_id=current_user.id).all()
        return jsonify([g.to_dict() for g in goals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@savings_bp.route('/savings', methods=['POST'])
@login_required
def create_savings_goal():
    try:
        data = request.json
        goal = SavingsGoal(
            user_id=current_user.id,
            goal_name=data['goal_name'],
            target_amount=data['target_amount'],
            current_amount=data.get('current_amount', 0),
            due_date=datetime.fromisoformat(data['due_date']) if 'due_date' in data else None
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify(goal.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@savings_bp.route('/savings/<int:goal_id>', methods=['PUT'])
@login_required
def update_savings_goal(goal_id):
    try:
        data = request.json
        goal = SavingsGoal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
        goal.current_amount = data.get('current_amount', goal.current_amount)
        goal.target_amount = data.get('target_amount', goal.target_amount)
        db.session.commit()
        return jsonify(goal.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@savings_bp.route('/savings/<int:goal_id>', methods=['DELETE'])
@login_required
def delete_savings_goal(goal_id):
    try:
        goal = SavingsGoal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
        db.session.delete(goal)
        db.session.commit()
        return jsonify({'message': 'Savings goal deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
