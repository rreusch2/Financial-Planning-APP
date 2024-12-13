from ai_services.base import BaseAIService


class FinancialEducation(BaseAIService):
    def __init__(self):
        super().__init__()

    def generate_personalized_lesson(self, user_data):
      """Generates a personalized financial lesson based on user data."""
      prompt = f"""
        You are an expert AI financial educator.
        User Data: {user_data}

        Based on the user data, determine what financial concepts the user needs to learn about. Provide a short summary of the concepts they need to learn, and provide one specific actionable tip.

         Provide your recommendation in JSON format:
         {{
          "lesson_summary": "A summary of all key concepts you have identified",
          "lesson_tip": "Actionable tip for the user"
         }}
        """
      response = self.generate_text(prompt)
      return response