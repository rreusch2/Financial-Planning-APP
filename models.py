from datetime import datetime, date, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from custom_categories import categorize_transaction
from flask_login import UserMixin
from extensions import db
import logging
from custom_categories import categorize_transaction, CUSTOM_CATEGORY_MAP

logger = logging.getLogger(__name__)

# Create UTC timezone object
UTC = timezone.utc

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    access_token = db.Column(db.String(256), nullable=True)
    plaid_access_token = db.Column(db.String(256), nullable=True)
    plaid_item_id = db.Column(db.String(256), nullable=True)
    last_plaid_sync = db.Column(db.DateTime, nullable=True)
    has_plaid_connection = db.Column(db.Boolean, default=False)  # Ensure this field is present
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    custom_incomes = db.relationship('CustomIncome', backref='user', lazy=True, cascade='all, delete-orphan')
    user_incomes = db.relationship('UserIncome', backref='user', lazy=True, cascade='all, delete-orphan')
    preferences = db.relationship('UserCategoryPreference', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hashes and sets the password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifies the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def update_plaid_tokens(self, access_token, item_id):
        """Update Plaid access token and item ID."""
        try:
            self.plaid_access_token = access_token
            self.plaid_item_id = item_id
            self.has_plaid_connection = True
            self.last_plaid_sync = datetime.now(timezone.utc)
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating Plaid tokens: {e}")
            db.session.rollback()
            return False

    def to_dict(self):
        """Serialize user details."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'has_plaid_connection': self.has_plaid_connection,
            'last_sync': self.last_plaid_sync.isoformat() if self.last_plaid_sync else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
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
    plaid_category_id = db.Column(db.String(100), nullable=True)
    merchant_name = db.Column(db.String(200), nullable=True)
    pending = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    confidence_score = db.Column(db.Float, nullable=True)  # Confidence level of categorization

    def set_category_from_name(self):
        """Set transaction category based on merchant name using CUSTOM_CATEGORY_MAP."""
        try:
            category_tuple = CUSTOM_CATEGORY_MAP.get(self.name, None)
            if category_tuple:
                self.category = f"{category_tuple[0]}:{category_tuple[1]}"
            else:
                self.category = "Uncategorized:Other"
        except Exception as e:
            logger.error(f"Error categorizing transaction: {e}")
            self.category = "Uncategorized:Other"

    def __init__(self, user_id, transaction_id, date, name, amount, category=None, 
                 plaid_category_id=None, merchant_name=None, pending=False):
        self.user_id = user_id
        self.transaction_id = transaction_id
        
        # Handle date conversion
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
        self.plaid_category_id = plaid_category_id
        self.merchant_name = merchant_name
        self.pending = pending
        
        # Set category
        if category:
            self.category = category
        else:
            self.set_category_from_name()

    def to_dict(self):
        """Serialize transaction details."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'transaction_id': self.transaction_id,
            'date': self.date.strftime('%Y-%m-%d'),
            'name': self.name,
            'amount': self.amount,
            'category': self.category,
            'merchant_name': self.merchant_name,
            'pending': self.pending,
            'plaid_category_id': self.plaid_category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserIncome(db.Model):
    __tablename__ = 'user_income'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    income_type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)           # Added for income tracking
    end_date = db.Column(db.DateTime, nullable=True)            # Added for income tracking
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
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
            'user_id': self.user_id,
            'source_name': self.source_name,
            'amount': self.amount,
            'frequency': self.frequency,
            'type': self.type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None
        }

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