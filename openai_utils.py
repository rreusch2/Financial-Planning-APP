from dotenv import load_dotenv
import os
from openai import OpenAI

# Load the environment variables from the .env file
load_dotenv()

# Initialize OpenAI client with the API key from the environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_financial_advice(user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial assistant providing helpful financial advice."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=150,
            temperature=0.7
        )
        # Extract and return the response content
        advice = response.choices[0].message.content.strip()
        return advice

    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while generating financial advice."
