from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)
UTC = timezone.utc

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    plaid_access_token = db.Column(db.String(200))
    plaid_item_id = db.Column(db.String(200))
    has_plaid_connection = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'has_plaid_connection': self.has_plaid_connection
        }

class Transaction(db.Model):
    __tablename__ = 'transaction'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    account_id = db.Column(db.String(100), nullable=True)
    date = db.Column(db.DateTime, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    merchant_name = db.Column(db.String(200), nullable=True)
    pending = db.Column(db.Boolean, server_default='false')
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        """Convert transaction to dictionary with error handling."""
        try:
            return {
                'id': self.transaction_id,
                'account_id': str(self.account_id) if self.account_id else '',
                'date': self.date.strftime('%Y-%m-%d') if self.date else '',
                'name': str(self.name) if self.name else '',
                'amount': float(self.amount) if self.amount is not None else 0.0,
                'category': str(self.category) if self.category else 'Uncategorized',
                'merchant_name': str(self.merchant_name) if self.merchant_name else '',
                'pending': bool(self.pending) if self.pending is not None else False
            }
        except Exception as e:
            logger.error(f"Error in to_dict for transaction {self.id}: {e}")
            # Return a safe default dictionary
            return {
                'id': str(self.id),
                'account_id': '',
                'date': '',
                'name': 'Error processing transaction',
                'amount': 0.0,
                'category': 'Uncategorized',
                'merchant_name': '',
                'pending': False
            }

class UserIncome(db.Model):
    __tablename__ = 'user_income'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    income_type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    def to_dict(self):
        return {
            'id': self.id,
            'income_type': self.income_type,
            'amount': self.amount,
            'frequency': self.frequency,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None
        }

class CustomIncome(db.Model):
    __tablename__ = 'custom_income'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    source_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    def to_dict(self):
        return {
            'id': self.id,
            'source_name': self.source_name,
            'amount': self.amount,
            'frequency': self.frequency,
            'type': self.type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None
        }

# Add these classes after your existing CustomIncome class

class SavingsGoal(db.Model):
    __tablename__ = 'savings_goal'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal_name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'goal_name': self.goal_name,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Budget(db.Model):
    __tablename__ = 'budget'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    budget_limit = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'budget_limit': self.budget_limit,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserCategoryPreference(db.Model):
    __tablename__ = 'user_category_preference'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    preference_score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'preference_score': self.preference_score,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }