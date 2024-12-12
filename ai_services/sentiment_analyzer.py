from .base import BaseAIService

class SentimentAnalyzer(BaseAIService):
    def analyze_transaction_sentiment(self, description: str) -> dict:
        messages = [
            {
                "role": "system",
                "content": "You are a financial sentiment analyzer. Analyze the emotional and financial impact of transactions."
            },
            {
                "role": "user",
                "content": f"Analyze the sentiment and financial impact of this transaction: {description}"
            }
        ]
        
        analysis = self._create_completion(messages)
        return {
            'description': description,
            'analysis': analysis or "Unable to analyze sentiment at this time."
        }