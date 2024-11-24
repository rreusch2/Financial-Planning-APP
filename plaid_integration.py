import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.exceptions import ApiException
from flask import current_app

logger = logging.getLogger(__name__)

# Add to plaid_integration.py

class PlaidError(Exception):
    """Custom exception for Plaid API errors"""
    def __init__(self, message, plaid_error=None):
        self.message = message
        self.plaid_error = plaid_error
        super().__init__(self.message)

def handle_plaid_error(func):
    """Decorator to handle Plaid API errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ApiException as e:
            logger.error("Plaid API error: %s", e)
            raise PlaidError(str(e), e)
        except Exception as e:
            logger.error("Unexpected error: %s", e)
            raise PlaidError("An unexpected error occurred")
    return wrapper

def create_link_token(user_id: str) -> str:
    """Create a link token for Plaid Link initialization"""
    try:
        client = current_app.plaid_client
        request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=str(user_id)),
            client_name="FinanceTracker",
            products=[Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en"
        )
        response = client.link_token_create(request)
        return response.link_token
    except Exception as e:
        logger.error(f"Error creating link token: {e}")
        raise

def fetch_transactions(access_token: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
    """Fetch transactions from Plaid"""
    try:
        client = current_app.plaid_client
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        options = TransactionsGetRequestOptions(
            include_personal_finance_category=True
        )
        
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=options
        )
        
        response = client.transactions_get(request)
        transactions = response.transactions
        
        # Process transactions into a more usable format
        processed_transactions = []
        for transaction in transactions:
            processed_transaction = {
                'transaction_id': transaction.transaction_id,
                'date': transaction.date,
                'name': transaction.merchant_name or transaction.name,
                'amount': float(transaction.amount),
                'category': transaction.personal_finance_category.primary if transaction.personal_finance_category else 'Uncategorized'
            }
            processed_transactions.append(processed_transaction)
            
        return processed_transactions

    except ApiException as e:
        logger.error(f"Plaid API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error fetching transactions: {e}")
        raise

def exchange_public_token(public_token: str) -> str:
    """Exchange public token for access token"""
    try:
        client = current_app.plaid_client
        response = client.item_public_token_exchange(public_token)
        return response.access_token
    except Exception as e:
        logger.error(f"Error exchanging public token: {e}")
        raise