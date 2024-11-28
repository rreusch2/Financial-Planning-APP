import numpy as np
from app import app, db  # Import your Flask app and db from app.py
from models import Transaction, User
import random
from datetime import datetime, timedelta
import uuid
from models import db, User, Transaction
from werkzeug.security import generate_password_hash

def clear_transactions():
    """Clear all existing transactions."""
    try:
        Transaction.query.delete()  # Deletes all records in the transactions table
        db.session.commit()
        print("Cleared existing transactions.")
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing transactions: {e}")


# Categories for transactions
categories = {
    'Food': ['Uber Eats', 'Subway', 'Walmart Grocery', 'Starbucks', 'McDonald\'s'],
    'Transport': ['Uber', 'Lyft', 'Shell Gas', 'BP Gas Station', 'Metro'],
    'Entertainment': ['Netflix', 'Spotify', 'AMC Theatres', 'Xbox Live', 'PlayStation Store'],
    'Utilities': ['Electric Company', 'Water Company', 'Internet Provider', 'Gas Company'],
    'Rent': ['Property Management', 'Landlord'],
    'Travel': ['Delta Airlines', 'Hilton Hotels', 'Airbnb', 'Booking.com', 'Amtrak'],
    'Shopping': ['Amazon', 'Walmart', 'Target', 'Apple Store', 'Best Buy'],
    'Medical': ['Pharmacy', 'Clinic Visit', 'Dental Office', 'Eye Care'],
    'Insurance': ['Geico', 'State Farm', 'Progressive', 'Allstate'],
    'Subscriptions': ['Netflix', 'Spotify', 'Hulu', 'Adobe', 'Microsoft 365']
}



def generate_mock_transactions(user_id):
    """Generate realistic mock transactions."""
    try:
        # Clear existing transactions
        Transaction.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        print("Cleared existing transactions.")

        categories = [
            "Food", "Transport", "Shopping", "Medical", "Utilities",
            "Entertainment", "Travel", "Insurance", "Subscriptions"
        ]
        merchants = [
            "Amazon", "Spotify", "Walmart", "Starbucks", "Uber", "Costco", "Netflix",
            "Hilton Hotels", "Progressive", "Pharmacy", "Gas Company", "Metro"
        ]

        transactions = []
        for _ in range(500):  # Generate 500 transactions
            transaction = Transaction(
                user_id=user_id,
                transaction_id=str(uuid.uuid4()),
                date=(datetime.now() - timedelta(days=random.randint(0, 365))),
                name=random.choice(merchants),
                amount=float(np.random.uniform(-500, 1000)),  # Convert to float
                category=str(random.choice(categories)),  # Convert to str
                merchant_name=random.choice(merchants),
                pending=random.choice([True, False])
            )
            transactions.append(transaction)

        db.session.bulk_save_objects(transactions)
        db.session.commit()
        print(f"Generated {len(transactions)} transactions for user {user_id}.")
    except Exception as e:
        db.session.rollback()
        print(f"Error generating transactions: {e}")




def seed_mock_data():
    with app.app_context():  # Add this line to set up the application context
        clear_transactions()  # Clear all existing transactions

        # Check if test user exists, create if not
        test_user = User.query.filter_by(username="testuser").first()
        if not test_user:
            test_user = User(
                username="testuser",
                email="testuser@example.com",
                password_hash=generate_password_hash("password123"),  # Securely hash password
                has_plaid_connection=True
            )
            db.session.add(test_user)
            db.session.commit()

        # Generate mock transactions for the test user
        generate_mock_transactions(test_user.id)


if __name__ == "__main__":
    seed_mock_data()
