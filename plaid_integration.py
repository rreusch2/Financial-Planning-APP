from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

def create_plaid_client():
    """Create and configure Plaid client."""
    try:
        client_id = os.getenv('PLAID_CLIENT_ID')
        secret = os.getenv('PLAID_SECRET')
        if not client_id or not secret:
            raise ValueError("Missing PLAID_CLIENT_ID or PLAID_SECRET in environment variables.")

        configuration = Configuration(
            host=os.getenv('PLAID_ENV', 'https://sandbox.plaid.com'),
            api_key={
                'clientId': client_id,
                'secret': secret
            }
        )
        api_client = ApiClient(configuration)
        return plaid_api.PlaidApi(api_client)
    except Exception as e:
        logger.error("Error creating Plaid client: %s", e, exc_info=True)
        raise

def fetch_transactions(access_token, start_date=None, end_date=None):
    """Fetch transactions from Plaid."""
    try:
        client = create_plaid_client()
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).date()
        if not end_date:
            end_date = datetime.now().date()

        logger.info(f"Fetching transactions from {start_date} to {end_date} for access token.")

        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options={'include_personal_finance_category': True}
        )
        response = client.transactions_get(request)
        logger.info(f"Fetched {len(response.transactions)} transactions.")
        return response.transactions
    except Exception as e:
        logger.error("Error fetching transactions: %s", e, exc_info=True)
        raise

def preprocess_transactions(transactions):
    """Process raw Plaid transactions into a standardized format."""
    try:
        processed_transactions = []
        for transaction in transactions:
            amount = float(transaction.amount)
            transaction_type = 'Income' if amount > 0 else 'Expense'
            category = transaction.personal_finance_category.primary if transaction.personal_finance_category else 'Uncategorized'

            processed_transaction = {
                'transaction_id': transaction.transaction_id,
                'date': transaction.date.isoformat() if transaction.date else None,
                'name': transaction.name,
                'amount': abs(amount),  # Use absolute values for easier processing
                'category': category,
                'transaction_type': transaction_type,
                'plaid_category_id': transaction.category_id,
                'merchant_name': transaction.merchant_name,
                'pending': transaction.pending
            }
            logger.debug(f"Processed transaction: {processed_transaction}")
            processed_transactions.append(processed_transaction)
        return processed_transactions
    except Exception as e:
        logger.error("Error preprocessing transactions: %s", e, exc_info=True)
        raise

def fetch_and_preprocess_transactions(access_token, start_date=None, end_date=None):
    """Fetch and process transactions in one step."""
    try:
        raw_transactions = fetch_transactions(access_token, start_date, end_date)
        return preprocess_transactions(raw_transactions)
    except Exception as e:
        logger.error("Error in fetch and preprocess: %s", e, exc_info=True)
        raise

def exchange_public_token(public_token):
    """Exchange a public token for an access token."""
    try:
        client = create_plaid_client()
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        return exchange_response.access_token, exchange_response.item_id
    except Exception as e:
        logger.error("Error exchanging public token: %s", e, exc_info=True)
        raise
