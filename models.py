# models.py

from extensions import db  # Import db from extensions, don't redefine it
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from custom_categories import categorize_transaction
from flask_login import UserMixin

# Define your models here

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    access_token = db.Column(db.String(256), nullable=True)  # Ensure this line exists

    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    custom_incomes = db.relationship('CustomIncome', backref='user', lazy=True)
    user_incomes = db.relationship('UserIncome', backref='user', lazy=True)
    preferences = db.relationship('UserCategoryPreference', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'access_token': self.access_token
        }


class Transaction(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=True)

    def set_category_from_name(self):
        """Set transaction category based on merchant name matching"""
        category_tuple = categorize_transaction(self.name)
        self.category = f"{category_tuple[0]}:{category_tuple[1]}" if category_tuple else "Uncategorized:Other"

    def __init__(self, user_id, transaction_id, date, name, amount, category=None):
        self.user_id = user_id
        self.transaction_id = transaction_id
        # Ensure date is stored as datetime
        if isinstance(date, str):
            self.date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        elif isinstance(date, datetime):
            self.date = date
        elif isinstance(date, date):
            self.date = datetime.combine(date, datetime.min.time())
        else:
            raise ValueError("Invalid date format provided for Transaction.")
        self.name = name
        self.amount = amount
        # Try to categorize if no category provided
        if category:
            self.category = category
        else:
            self.set_category_from_name()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'transaction_id': self.transaction_id,
            'date': self.date.strftime('%Y-%m-%d'),
            'name': self.name,
            'amount': self.amount,
            'category': self.category
        }


class UserIncome(db.Model):
    __tablename__ = 'user_income'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    income_type = db.Column(db.String(100), nullable=False)  # e.g., "Salary", "Hourly", "Investment"
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # e.g., "monthly", "weekly", "yearly"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'income_type': self.income_type,
            'amount': self.amount,
            'frequency': self.frequency
        }


class CustomIncome(db.Model):
    __tablename__ = 'custom_income'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    source_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'source_name': self.source_name,
            'amount': self.amount,
            'frequency': self.frequency,
            'type': self.type
        }


class UserCategoryPreference(db.Model):
    __tablename__ = 'user_category_preference'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    preference_score = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'preference_score': self.preference_score
        }
