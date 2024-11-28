import pandas as pd
from app import app
from models import Transaction
from sklearn.preprocessing import LabelEncoder
import numpy as np
import os


def export_transactions(output_dir="transactions_npy"):
    """Export transactions to .npy files for training."""
    with app.app_context():
        transactions = Transaction.query.all()
        data = [t.to_dict() for t in transactions]
        df = pd.DataFrame(data)

        # Split categories into main and subcategories
        df[['main_category', 'sub_category']] = df['category'].str.split(':', expand=True)

        # Clean up columns for DLRM
        df = df[['amount', 'main_category', 'sub_category', 'name']]
        df.columns = ['numerical_amount', 'category_main', 'category_sub', 'merchant_name']

        # Encode categorical features
        encoders = {}
        for col in ['category_main', 'category_sub', 'merchant_name']:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le  # Save encoders for future decoding if needed

        # Add a dummy label column if not present
        df['label'] = np.random.randint(0, 2, size=len(df))  # Binary labels for testing purposes

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Save dense (numerical) features
        np.save(f"{output_dir}/train_dense.npy", df[['numerical_amount']].values)

        # Save categorical features
        categorical_columns = ['category_main', 'category_sub', 'merchant_name']
        np.save(f"{output_dir}/train_categorical.npy", df[categorical_columns].values)

        # Save labels
        np.save(f"{output_dir}/train_labels.npy", df['label'].values)

        print(f"Data saved to {output_dir} in .npy format.")


def save_to_npy(input_file="transactions_processed.npy", output_dir="transactions_npy"):
    """Convert processed NumPy data to separate .npy files for DLRM."""
    df = pd.DataFrame(np.load(input_file), columns=['numerical_amount', 'category_main', 'category_sub', 'merchant_name'])

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save dense (numerical) features
    np.save(f"{output_dir}/train_dense.npy", df[['numerical_amount']].values)

    # Save categorical features
    categorical_columns = ['category_main', 'category_sub', 'merchant_name']
    categorical_data = df[categorical_columns].values
    np.save(f"{output_dir}/train_categorical.npy", categorical_data)

    print(f"Data saved to {output_dir} in .npy format.")

def save_sparse_data(input_csv="transactions_encoded.csv", output_dir="transactions_npy"):
    """Generate sparse data and save it."""
    # Read your existing encoded CSV
    df = pd.read_csv(input_csv)

    # Create sparse data (as a placeholder, this will generate dummy sparse data)
    sparse_data = df[['category_main', 'category_sub', 'merchant_name']].values

    # Save sparse data as .npy
    os.makedirs(output_dir, exist_ok=True)
    np.save(f"{output_dir}/train_sparse.npy", sparse_data)
    print(f"Sparse data saved to {output_dir}/train_sparse.npy")

if __name__ == "__main__":
    export_transactions()
    save_to_npy()
    save_sparse_data()