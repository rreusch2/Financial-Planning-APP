# routes/plaid.py
from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from models import User, Transaction, db
from plaid_integration import create_link_token, exchange_public_token, fetch_transactions, PlaidError
from routes import plaid_bp
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@plaid_bp.route('/create_link_token', methods=['GET'])
@login_required
def get_link_token():
    try:
        link_token = create_link_token(str(current_user.id))
        return jsonify({'link_token': link_token}), 200
    except PlaidError as e:
        logger.error(f"Plaid error creating link token: {e.message}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating link token: {str(e)}")
        return jsonify({'error': 'Failed to create link token'}), 500

@plaid_bp.route('/exchange_token', methods=['POST'])
@login_required
def handle_exchange_token():
    try:
        public_token = request.json.get('public_token')
        if not public_token:
            return jsonify({'error': 'Public token is required'}), 400

        access_token = exchange_public_token(public_token)
        current_user.plaid_access_token = access_token
        db.session.commit()

        # Immediately fetch initial transactions
        sync_transactions()

        return jsonify({'success': True}), 200
    except PlaidError as e:
        logger.error(f"Plaid error exchanging token: {e.message}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error exchanging token: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to exchange token'}), 500

@plaid_bp.route('/sync', methods=['POST'])
@login_required
def sync_transactions():
    try:
        if not current_user.plaid_access_token:
            return jsonify({'error': 'No bank account connected'}), 400

        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        transactions = fetch_transactions(
            current_user.plaid_access_token,
            start_date,
            end_date
        )

        new_count = 0
        for transaction in transactions:
            existing = Transaction.query.filter_by(
                transaction_id=transaction['transaction_id']
            ).first()
            
            if not existing:
                new_transaction = Transaction(
                    user_id=current_user.id,
                    transaction_id=transaction['transaction_id'],
                    date=datetime.strptime(transaction['date'], '%Y-%m-%d'),
                    name=transaction['name'],
                    amount=transaction['amount'],
                    category=transaction.get('category', 'Uncategorized')
                )
                db.session.add(new_transaction)
                new_count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Synced {new_count} new transactions',
            'new_transactions_count': new_count
        }), 200

    except PlaidError as e:
        logger.error(f"Plaid error syncing transactions: {e.message}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error syncing transactions: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to sync transactions'}), 500