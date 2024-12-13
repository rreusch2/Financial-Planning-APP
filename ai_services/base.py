import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAIService:
    def __init__(self):
        GOOGLE_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_GEMINI_API_KEY not found in .env file.")
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_text(self, prompt):
        """Generates text using the Gemini model."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating text with Gemini: {e}")
            return None