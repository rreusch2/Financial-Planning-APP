import os
import toml
import logging
import time
from functools import wraps
from typing import Optional, List

import plaid
from plaid.api import plaid_api
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
# Remove this import since 'Environment' is not available
# from plaid import Environment
# Updated imports for models
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_response import TransactionsSyncResponse
from plaid.exceptions import ApiException
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
import pandas as pd
from datetime import datetime, date

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load credentials from secrets.toml
config = toml.load("secrets.toml")

# **Initialize Plaid API client with host URL directly**
configuration = Configuration(
    host="https://sandbox.plaid.com",  # Use the appropriate environment URL
    api_key={
        'clientId': config["plaid"]["client_id"],
        'secret': config["plaid"]["secret"],
    }
)

api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ApiException as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {e}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator

@retry_on_error()
def create_link_token(user_id: str) -> str:
    """Create a link token for Plaid Link initialization."""
    try:
        request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=str(user_id)),
            client_name="FinanceTracker",
            products=[Products("transactions")],
            country_codes=[CountryCode('US')],
            language='en'
        )
        response = client.link_token_create(request)
        return response.link_token
    except ApiException as e:
        logger.error(f"Error creating link token: {e}")
        raise

@retry_on_error()
def exchange_public_token(public_token: str) -> Optional[str]:
    """Exchange a public token for an access token."""
    try:
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response.access_token
        if not access_token:
            logger.error("Invalid response from Plaid token exchange")
            return None
        logger.info("Successfully exchanged public token for access token")
        return access_token
    except ApiException as e:
        logger.error(f"Plaid API error exchanging public token: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error exchanging public token: {str(e)}")
        raise

from datetime import datetime, date

@retry_on_error()
def fetch_transactions(access_token: str, start_date: str, end_date: str) -> List[dict]:
    """Fetch transactions from Plaid."""
    try:
        # Convert string dates to date objects
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

        options = TransactionsGetRequestOptions(count=500, offset=0)  # Adjust as needed
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date_obj,
            end_date=end_date_obj,
            options=options
        )
        response = client.transactions_get(request)
        transactions = response.transactions

        # Handle pagination if necessary
        total_transactions = response.total_transactions
        while len(transactions) < total_transactions:
            options.offset = len(transactions)
            request.options = options
            response = client.transactions_get(request)
            transactions.extend(response.transactions)

        return [t.to_dict() for t in transactions]
    except ApiException as e:
        logger.error(f"Error fetching transactions: {e}")
        raise

def fetch_and_preprocess_transactions(access_token: str) -> pd.DataFrame:
    """Fetch and preprocess transactions for analysis."""
    try:
        transactions = fetch_transactions(access_token)
        if not transactions:
            logger.info("No transactions found.")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])

        # Additional preprocessing as needed
        # ...

        return df

    except Exception as e:
        logger.error(f"Error in transaction processing: {e}")
        raise




