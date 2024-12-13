from ai_services.base import BaseAIService


class BudgetAdvisor(BaseAIService):
    def __init__(self):
        super().__init__()

    def generate_budget_recommendation(self, user_data, current_month):
          """Generates budget recommendations based on user data and current month."""
          prompt = f"""
            You are an expert AI financial advisor.

            User Data: {user_data}
            Current Month: {current_month}

            Based on the user's data, and current month, provide detailed and specific budget recommendations.
            Provide a detailed breakdown of the budget categories and amounts.

             Suggest specific amounts for each category based on the user's spending habits.
             Explain your reasoning for why you are choosing those specific amounts.

            Provide your recommendations using the following JSON format:

           {{
              "budget_recommendation_summary" : "Short Summary of budget recommendation",
              "budget_categories": [
              {{
                  "category": "Category 1 Name",
                  "recommended_amount": "Recommended spending amount",
                  "reasoning": "Why you are choosing this amount"
               }},
               {{
                  "category": "Category 2 Name",
                  "recommended_amount": "Recommended spending amount",
                  "reasoning": "Why you are choosing this amount"
               }}
             ]
           }}
            """
          response = self.generate_text(prompt)
          return response

    def analyze_budget_spending(self, user_data, budget_data, current_month):
            """Analyzes budget and spending data for current month to find if a user is overspending or underspending in a particular category."""

            prompt = f"""
            You are an expert AI financial advisor tasked with analyzing a user's budget.

            User Data: {user_data}
            Budget Data: {budget_data}
            Current Month: {current_month}

            Based on this data, analyze their spending based on their budget.
            Provide a summary of what you found, and provide specific recommendations based on your analysis.

            Be sure to include the specific categories that they are overspending or underspending on.
            Provide your recommendations using the following JSON format:
           {{
             "analysis_summary": "Short summary of the spending analysis",
             "recommendations": [
               {{
                 "category": "Category 1 Name",
                 "status": "overspending or underspending",
                 "reason": "Why they are overspending or underspending"
               }},
               {{
                 "category": "Category 2 Name",
                 "status": "overspending or underspending",
                 "reason": "Why they are overspending or underspending"
                }}
             ]
           }}
            """
            response = self.generate_text(prompt)
            return response