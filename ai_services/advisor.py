from .base import BaseAIService

class AIFinancialAdvisor(BaseAIService):
    def get_financial_advice(self, user_data):
        messages = [
            {
                "role": "system",
                "content": "You are a professional financial advisor with expertise in personal finance, budgeting, and investment strategies."
            },
            {
                "role": "user",
                "content": f"Based on this user data: {user_data}, provide personalized financial advice."
            }
        ]
        
        advice = self._create_completion(messages, model="gpt-4")
        return advice or "Sorry, I'm unable to provide advice at the moment."