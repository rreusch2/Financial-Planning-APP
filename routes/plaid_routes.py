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
from models import db

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
    """Exchange a public token for an access token."""
    try:
        public_token = request.json.get('public_token')
        if not public_token:
            logger.warning("Missing public token in request")
            return jsonify({"error": "Missing public token"}), 400

        logger.info("Exchanging public token for user %s", current_user.id)
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        exchange_response = client.item_public_token_exchange(exchange_request)
        
        access_token = exchange_response.access_token
        item_id = exchange_response.item_id

        # Save to user record
        current_user.plaid_access_token = access_token
        current_user.plaid_item_id = item_id
        current_user.has_plaid_connection = True
        db.session.commit()

        logger.info("Successfully saved Plaid credentials for user %s", current_user.id)

        return jsonify({"success": True}), 200
    except Exception as e:
        logger.error("Unexpected error exchanging public token: %s", e)
        db.session.rollback()
        return jsonify({"error": "Failed to exchange token"}), 500

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