import requests
import json

BASE_URL = 'http://localhost:5028/api'

def test_plaid_config():
    """Test Plaid configuration endpoint."""
    try:
        response = requests.get(
            f'{BASE_URL}/test_config',
            cookies={'session': 'your-session-cookie'}  # You'll need to get an actual session cookie
        )
        print('Plaid Config Test Response:', response.json())
    except Exception as e:
        print(f'Error testing Plaid config: {e}')

def create_link_token():
    """Test create link token endpoint."""
    try:
        response = requests.get(
            f'{BASE_URL}/create_link_token',
            cookies={'session': 'your-session-cookie'}
        )
        print('Create Link Token Response:', response.json())
    except Exception as e:
        print(f'Error creating link token: {e}')

if __name__ == '__main__':
    print('Testing Plaid Configuration...')
    test_plaid_config()
    print('\nTesting Link Token Creation...')
    create_link_token()