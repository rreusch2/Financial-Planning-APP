import pandas as pd
import matplotlib.pyplot as plt
from models import Transaction
from app import app


def analyze_transactions():
    """Analyze transaction data."""
    with app.app_context():
        # Fetch transactions
        transactions = Transaction.query.all()
        data = [t.to_dict() for t in transactions]

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Split category into main and subcategory
        df[['main_category', 'sub_category']] = df['category'].str.split(':', expand=True)

        # Analyze income and expenses
        total_income = df[df['amount'] > 0]['amount'].sum()
        total_expenses = df[df['amount'] < 0]['amount'].sum()
        by_category = df.groupby('main_category')['amount'].sum()
        by_subcategory = df.groupby('sub_category')['amount'].sum()

        print(f"Total Income: ${total_income:,.2f}")
        print(f"Total Expenses: ${abs(total_expenses):,.2f}")
        print("\nExpenses by Main Category:")
        print(by_category)
        print("\nExpenses by Subcategory:")
        print(by_subcategory)

        return df  # Return DataFrame for further use


def plot_category_spending(df):
    """Plot spending by main category."""
    by_category = df.groupby('main_category')['amount'].sum()
    by_category.plot(kind='bar', title='Spending by Main Category', figsize=(10, 6))
    plt.ylabel('Amount ($)')
    plt.tight_layout()
    plt.show()


def plot_subcategory_spending(df):
    """Plot spending by subcategory."""
    by_subcategory = df.groupby('sub_category')['amount'].sum().sort_values()
    by_subcategory.plot(kind='barh', title='Spending by Subcategory', figsize=(10, 6))
    plt.xlabel('Amount ($)')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Analyze transactions and retrieve the DataFrame
    df = analyze_transactions()

    # Generate visualizations
    plot_category_spending(df)
    plot_subcategory_spending(df)
