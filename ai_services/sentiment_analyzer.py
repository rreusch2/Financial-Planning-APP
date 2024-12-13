from ai_services.base import BaseAIService


class SentimentAnalyzer(BaseAIService):
    def __init__(self):
        super().__init__()

    def analyze_transaction_sentiment(self, transaction_description):
        """Analyzes the sentiment of a transaction description."""

        prompt = f"""
        You are an expert sentiment analyzer.

        Analyze the sentiment of the following description: {transaction_description}

        Based on this, determine what the overall sentiment is. Please provide a confidence score on how confident you are about this analysis from 0 to 1.
        
        Provide your analysis in JSON format:

         {{
          "sentiment": "positive, negative, or neutral",
          "confidence_score": "score from 0 to 1"
         }}
        """
        response = self.generate_text(prompt)
        return response