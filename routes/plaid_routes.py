"""
This module defines routes for Plaid integration.
"""

import os
import logging
from flask import Blueprint, jsonify, request as flask_request
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
        request_data = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(
                client_user_id=str(current_user.id)
            ),
            client_name="FinanceTracker",
            products=[Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en"
        )
        
        response = client.link_token_create(request_data)
        return jsonify({"link_token": response['link_token']}), 200
    except plaid_exceptions.ApiException as e:
        logger.error("Error creating link token: %s", e)
        return jsonify({"error": str(e)}), 500

@plaid_bp.route('/exchange_public_token', methods=['POST'])
@login_required
def exchange_public_token():
    """Exchange a public token for an access token."""
    try:
        public_token = flask_request.json.get('public_token')
        if not public_token:
            return jsonify({"error": "Missing public token"}), 400

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        exchange_response = client.item_public_token_exchange(exchange_request)
        
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']

        # Save to user record
        current_user.plaid_access_token = access_token
        current_user.plaid_item_id = item_id
        current_user.has_plaid_connection = True
        db.session.commit()

        return jsonify({"success": True}), 200
    except plaid_exceptions.ApiException as e:
        logger.error("Error exchanging public token: %s", e)
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Add a test endpoint to verify Plaid configuration
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
    
@plaid_bp.route('/debug_config', methods=['GET'])
def debug_plaid_config():
    """Debug endpoint to test Plaid configuration without authentication."""
    try:
        # Test Plaid client initialization
        client_id = os.getenv('PLAID_CLIENT_ID')
        plaid_secret = os.getenv('PLAID_SECRET')
        plaid_env = os.getenv('PLAID_ENV')
        
        config_status = {
            "status": "configured" if all([client_id, plaid_secret, plaid_env]) else "missing_config",
            "environment": plaid_env,
            "client_id_set": bool(client_id),
            "client_id_preview": client_id[:4] + "..." if client_id else None,
            "secret_set": bool(plaid_secret),
            "host": host,
            "api_client_initialized": bool(api_client),
            "plaid_client_initialized": bool(client)
        }
        
        return jsonify(config_status), 200
    except Exception as e:
        logger.error(f"Error in debug config: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error",
            "trace": str(e.__traceback__)
        }), 500