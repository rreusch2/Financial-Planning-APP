"""
This module contains utility functions for interacting with the OpenAI API.
"""
import os
from dotenv import load_dotenv  # cspell:ignore dotenv
from openai import OpenAI, OpenAIError, APIError, APIConnectionError

# Load the environment variables from the .env file
load_dotenv()  # cspell:ignore dotenv

# Initialize OpenAI client with the API key from the environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_financial_advice(user_input):
    """
    Generate financial advice based on user input using OpenAI's language model.
    
    Args:
        user_input (str): The user's input or question.
        
    Returns:
        str: The generated financial advice.
    """
    try:
        response = client.completions.create(
            model="text-davinci-002",
            prompt=f"You are a financial assistant providing helpful financial advice.\n"
                   f"User: {user_input}\nAssistant:",
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7
        )
        advice = response.choices[0].text.strip()
        return advice

    except (OpenAIError, APIError, APIConnectionError) as e:
        print(f"An OpenAI API error occurred: {e}")
        return "An error occurred while generating financial advice."

def generate_transaction_category(transaction_description):
    """
    Generate a transaction category based on the transaction description using OpenAI's language model.
    
    Args:
        transaction_description (str): The description of the transaction.
        
    Returns:
        str: The generated transaction category.
    """
    try:
        response = client.completions.create(
            model="text-davinci-002",
            prompt=f"Categorize the following transaction: {transaction_description}\nCategory:",
            max_tokens=10,
            n=1,
            stop=None,
            temperature=0.7
        )
        category = response.choices[0].text.strip()
        return category

    except (OpenAIError, APIError, APIConnectionError) as e:
        print(f"An OpenAI API error occurred: {e}")
        return "Uncategorized"  # cspell:ignore Uncategorized