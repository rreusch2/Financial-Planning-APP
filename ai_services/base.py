import os
from openai import OpenAI
from dotenv import load_dotenv

class BaseAIService:
    def __init__(self, api_key=None):
        load_dotenv()
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        
    def _create_completion(self, messages, model="gpt-3.5-turbo"):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in AI completion: {e}")
            return None