import os
from dotenv import load_dotenv, find_dotenv

def check_keys():
    print("=== API Key Check ===")
    print(f"System ENV: {os.environ.get('OPENAI_API_KEY', 'Not set')[:10]}...")
    
    env_file = find_dotenv()
    print(f"Found .env at: {env_file}")
    
    load_dotenv(override=True)
    print(f"Loaded ENV: {os.getenv('OPENAI_API_KEY', 'Not set')[:10]}...")

if __name__ == "__main__":
    check_keys()