from ai_services.base import BaseAIService


class TransactionAnalyzer(BaseAIService):
    def __init__(self):
        super().__init__()

    def analyze_spending_patterns(self, user_data, current_month):
            """Analyzes spending patterns to identify potential areas for savings and better budgeting"""

            prompt = f"""
            You are an expert AI financial advisor tasked with analyzing a user's spending habits.
            User Data: {user_data}
            Current Month: {current_month}

             Based on the user's spending history, identify any spending patterns or trends.
              Provide your analysis in a summary, and also provide specific and concrete recommendations to the user.

             Provide your recommendations in JSON format:
            {{
            "analysis_summary" : "Summary of the analysis",
            "spending_insights" : [
                 {{
                  "pattern": "Specific pattern 1",
                  "recommendation": "What can be done"
                 }},
                {{
                  "pattern": "Specific pattern 2",
                  "recommendation": "What can be done"
                 }}
                ]
            }}

           """
            response = self.generate_text(prompt)
            return response

    def analyze_category_spending(self, user_data, category, current_month):
          """Analyzes spending in a specific category, and provides concrete suggestions."""
          prompt = f"""
          You are an expert AI financial advisor tasked with analyzing a user's spending habits.

           User Data: {user_data}
           Current Month: {current_month}
           Category: {category}

           Analyze the spending in the specific category, and based on the user's spending habits, suggest a concrete way they can optimize this category. Provide concrete examples.

            Be concise, and return your analysis in JSON format:
           {{
             "analysis_summary": "Short summary of your analysis",
             "recommendation": "Specific recommendation to optimize this category",
             "reasoning": "The reason behind this recommendation",
            }}
           """
          response = self.generate_text(prompt)
          return response