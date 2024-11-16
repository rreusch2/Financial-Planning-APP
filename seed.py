# seed.py

from app import app
from extensions import db
from models import User, Transaction, CustomIncome, UserIncome, UserCategoryPreference

with app.app_context():
    # Example: Add a default user
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('adminpassword')
        db.session.add(admin)
        db.session.commit()
    
    # Add other initial data as needed
