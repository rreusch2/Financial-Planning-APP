from transformers import BertTokenizer, BertForSequenceClassification
import pandas as pd
from models import Transaction, db
from app import app

# Load FinBERT model
tokenizer = BertTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = BertForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")

def categorize_transaction(description):
    """Categorize transaction using FinBERT."""
    inputs = tokenizer(description, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    sentiment = outputs.logits.argmax(-1).item()
    labels = {0: "Negative", 1: "Neutral", 2: "Positive"}
    return labels[sentiment]

def update_transaction_categories():
    """Fetch transactions, categorize them, and update the database."""
    with app.app_context():
        transactions = Transaction.query.filter_by(category=None).all()
        for t in transactions:
            try:
                t.category = categorize_transaction(t.name)
                db.session.add(t)
            except Exception as e:
                print(f"Error processing transaction {t.id}: {e}")
        db.session.commit()

if __name__ == "__main__":
    update_transaction_categories()
