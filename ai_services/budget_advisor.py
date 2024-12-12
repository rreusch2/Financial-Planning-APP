from .base import BaseAIService

class BudgetAdvisor(BaseAIService):
    def get_budget_recommendations(self, spending_history):
        messages = [
            {
                "role": "system",
                "content": "You are a budgeting expert who provides practical and actionable advice."
            },
            {
                "role": "user",
                "content": f"Based on this spending history, provide budget recommendations: {spending_history}"
            }
        ]
        
        recommendations = self._create_completion(messages)
        return recommendations or "Unable to provide budget recommendations at this time."