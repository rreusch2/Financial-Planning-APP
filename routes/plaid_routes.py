"""
This module defines routes for Plaid integration.
"""

import os
import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid import exceptions as plaid_exceptions
from models import db, Transaction
from datetime import datetime, timedelta
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
import time

logger = logging.getLogger(__name__)
plaid_bp = Blueprint('plaid', __name__)

# Initialize Plaid client
host = os.getenv('PLAID_ENV', 'https://sandbox.plaid.com')
configuration = Configuration(
    host=host,
    api_key={
        'clientId': os.getenv('PLAID_CLIENT_ID'),
        'secret': os.getenv('PLAID_SECRET')
    }
)

api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

def create_plaid_client():
    """Create and return a Plaid client instance."""
    configuration = Configuration(
        host=os.getenv('PLAID_ENV', 'https://sandbox.plaid.com'),
        api_key={
            'clientId': os.getenv('PLAID_CLIENT_ID'),
            'secret': os.getenv('PLAID_SECRET')
        }
    )
    api_client = ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)

@plaid_bp.route('/create_link_token', methods=['GET'])
@login_required
def create_link_token():
    """Create a link token for Plaid integration."""
    try:
        logger.info("Creating link token for user %s", current_user.id)
        request_data = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(
                client_user_id=str(current_user.id)
            ),
            client_name="WealthAI",
            products=[Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
            webhook="http://localhost:5000/api/plaid/webhook"
        )
        
        response = client.link_token_create(request_data)
        logger.info("Link token created successfully")
        return jsonify({"link_token": response.link_token}), 200
    except plaid_exceptions.ApiException as e:
        logger.error("Error creating link token: %s", e)
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error("Unexpected error creating link token: %s", e)
        return jsonify({"error": "Failed to create link token"}), 500

@plaid_bp.route('/exchange_public_token', methods=['POST'])
@login_required
def exchange_public_token():
    try:
        public_token = request.json.get('public_token')
        if not public_token:
            return jsonify({'error': 'Missing public token'}), 400

        # Exchange public token for access token
        client = create_plaid_client()
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        exchange_response = client.item_public_token_exchange(exchange_request)
        
        # Save access token and item ID
        current_user.plaid_access_token = exchange_response.access_token
        current_user.plaid_item_id = exchange_response.item_id
        current_user.has_plaid_connection = True
        db.session.commit()

        logger.info(f"Successfully exchanged public token for user {current_user.id}")

        # Wait a moment for Plaid to process the connection
        time.sleep(2)

        # Immediately sync transactions
        try:
            # Get transactions from last 30 days
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()
            
            transactions_request = TransactionsGetRequest(
                access_token=current_user.plaid_access_token,
                start_date=start_date.date(),
                end_date=end_date.date(),
                options={
                    "include_personal_finance_category": True,
                    "count": 100
                }
            )
            
            transactions_response = client.transactions_get(transactions_request)
            transactions = transactions_response.transactions

            for transaction in transactions:
                # Check if transaction already exists
                existing = Transaction.query.filter_by(
                    transaction_id=transaction.transaction_id
                ).first()

                if not existing:
                    new_transaction = Transaction(
                        user_id=current_user.id,
                        transaction_id=transaction.transaction_id,
                        account_id=transaction.account_id,
                        date=transaction.date,  # Already a datetime.date object
                        name=transaction.name,
                        amount=float(transaction.amount),
                        category=transaction.category[0] if transaction.category else None,
                        merchant_name=transaction.merchant_name,
                        pending=transaction.pending
                    )
                    db.session.add(new_transaction)

            db.session.commit()
            logger.info(f"Initial sync completed with {len(transactions)} transactions")

        except plaid_exceptions.ApiException as e:
            logger.error(f"Plaid API error in initial transaction sync: {e.body}")
        except Exception as e:
            logger.error(f"Error in initial transaction sync: {e}")
            # Don't rollback here - we still want to save the Plaid connection

        return jsonify({'success': True}), 200

    except Exception as e:
        logger.error(f"Error exchanging public token: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to exchange token'}), 500

@plaid_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Plaid webhooks."""
    try:
        webhook_data = request.get_json()
        webhook_type = webhook_data.get('webhook_type')
        webhook_code = webhook_data.get('webhook_code')
        
        logger.info("Received webhook: type=%s, code=%s", webhook_type, webhook_code)
        
        if webhook_type == 'TRANSACTIONS':
            # Handle transaction updates
            item_id = webhook_data.get('item_id')
            if webhook_code == 'TRANSACTIONS_REMOVED':
                # Handle removed transactions
                removed_transactions = webhook_data.get('removed_transactions', [])
                logger.info("Removing %d transactions", len(removed_transactions))
                # Add logic to remove transactions
                
            elif webhook_code in ['INITIAL_UPDATE', 'HISTORICAL_UPDATE', 'DEFAULT_UPDATE']:
                # Trigger transaction sync
                logger.info("New transactions available for item_id: %s", item_id)
                # Add logic to sync new transactions
                
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error("Error processing webhook: %s", e)
        return jsonify({"error": str(e)}), 500

@plaid_bp.route('/test_config', methods=['GET'])
@login_required
def test_plaid_config():
    """Test Plaid configuration."""
    try:
        return jsonify({
            "status": "configured",
            "environment": host,
            "client_id_set": bool(os.getenv('PLAID_CLIENT_ID')),
            "secret_set": bool(os.getenv('PLAID_SECRET'))
        }), 200
    except Exception as e:
        logger.error("Error testing Plaid config: %s", e)
        return jsonify({"error": str(e)}), 500

@plaid_bp.route('/sync_transactions', methods=['POST'])
@login_required
def sync_transactions():
    """Sync transactions for the current user."""
    try:
        if not current_user.plaid_access_token:
            return jsonify({'error': 'No bank account connected'}), 400

        logger.info(f"Starting transaction sync for user {current_user.id}")
        
        # Get transactions from Plaid
        client = create_plaid_client()
        
        # Get transactions from last 30 days
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        transactions_request = TransactionsGetRequest(
            access_token=current_user.plaid_access_token,
            start_date=start_date.date(),
            end_date=end_date.date(),
            options={
                "include_personal_finance_category": True,
                "count": 100
            }
        )
        
        transactions_response = client.transactions_get(transactions_request)
        transactions = transactions_response.transactions
        logger.info(f"Received {len(transactions)} transactions from Plaid")

        # Process transactions
        new_transactions_count = 0
        for transaction in transactions:
            # Check if transaction already exists
            existing = Transaction.query.filter_by(
                transaction_id=transaction.transaction_id
            ).first()

            if not existing:
                # Create new transaction
                new_transaction = Transaction(
                    user_id=current_user.id,
                    transaction_id=transaction.transaction_id,
                    account_id=transaction.account_id,
                    date=transaction.date,  # Already a datetime.date object
                    name=transaction.name,
                    amount=float(transaction.amount),
                    category=transaction.category[0] if transaction.category else None,
                    merchant_name=transaction.merchant_name,
                    pending=transaction.pending
                )
                db.session.add(new_transaction)
                new_transactions_count += 1
                logger.debug(f"Added new transaction: {transaction.name} - {transaction.amount}")

        db.session.commit()
        logger.info(f"Successfully synced {new_transactions_count} new transactions")
        
        return jsonify({
            'added': new_transactions_count,
            'total': len(transactions)
        }), 200

    except Exception as e:
        logger.error(f"Error syncing transactions: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to sync transactions'}), 500