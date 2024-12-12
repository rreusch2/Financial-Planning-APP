from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from datetime import datetime, timedelta
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def create_plaid_client():
    """Create and configure Plaid client."""
    try:
        client_id = os.getenv('PLAID_CLIENT_ID')
        secret = os.getenv('PLAID_SECRET')
        
        if not client_id or not secret:
            raise ValueError("Missing Plaid credentials")
            
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

def create_link_token(user_id: str) -> str:
    """Create a link token for Plaid Link."""
    try:
        client = create_plaid_client()
        
        request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="WealthAI",
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(
                client_user_id=str(user_id)
            )
        )
        
        response = client.link_token_create(request)
        return response.link_token
    except Exception as e:
        logger.error("Error creating link token: %s", e, exc_info=True)
        raise

def exchange_public_token(public_token: str) -> tuple[str, str]:
    """Exchange a public token for an access token."""
    try:
        client = create_plaid_client()
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        response = client.item_public_token_exchange(exchange_request)
        logger.info("Successfully exchanged public token for access token")
        return response.access_token, response.item_id
    except Exception as e:
        logger.error("Error exchanging public token: %s", e, exc_info=True)
        raise

def fetch_transactions(access_token: str, start_date=None, end_date=None) -> List[Dict[str, Any]]:
    """Fetch transactions from Plaid."""
    try:
        client = create_plaid_client()
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).date()
        if not end_date:
            end_date = datetime.now().date()

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
        logger.info(f"Successfully fetched {len(transactions)} transactions")
        
        return [process_transaction(tx) for tx in transactions]
    except Exception as e:
        logger.error("Error fetching transactions: %s", e, exc_info=True)
        raise

def process_transaction(transaction) -> Dict[str, Any]:
    """Process a single transaction."""
    try:
        return {
            'transaction_id': str(transaction.transaction_id),
            'date': transaction.date,
            'name': str(transaction.name),
            'amount': float(transaction.amount),
            'category': (transaction.personal_finance_category.primary 
                       if hasattr(transaction, 'personal_finance_category') 
                       else 'Uncategorized'),
            'merchant_name': str(transaction.merchant_name) if hasattr(transaction, 'merchant_name') else None,
            'pending': bool(transaction.pending)
        }
    except Exception as e:
        logger.error(f"Error processing transaction: {e}")
        raise