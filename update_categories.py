from models import db, Transaction
from app import app

def update_transaction_categories():
    """Update categories for all transactions."""
    with app.app_context():
        transactions = Transaction.query.all()
        for t in transactions:
            t.set_category_from_name()
        db.session.commit()

if __name__ == "__main__":
    update_transaction_categories()
    print("Transaction categories updated.")
