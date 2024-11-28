from models import db, Transaction
from app import app

with app.app_context():
    transactions = Transaction.query.limit(10).all()
    for t in transactions:
        print(t.to_dict())
