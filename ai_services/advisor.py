from ai_services.base import BaseAIService
from datetime import datetime
import requests
import os

class FinancialAdvisor(BaseAIService):
    def __init__(self):
        super().__init__()

    def generate_financial_advice(self, user_data, current_time, financial_goals):
            """Generates personalized financial advice based on spending, goals, and current time."""

            prompt = f"""
            You are an expert AI financial advisor, tasked with providing tailored advice to users. The current time is: {current_time}.

            User Data: {user_data}
            
            Financial Goals: {financial_goals}

            Based on this information, provide me with personalized, specific, and actionable financial advice for the user. Keep in mind all their financial goals, and tell them specific things they can do that they can take action on immediately.

            Be concise, and prioritize what they need to know first.

            Provide your advice in a structured format, using the following JSON format:

            {{
            "advice_summary": "A short summary of all of the advice that is given",
            "advice": [
            {{
            "title": "Title of Advice #1",
            "recommendation": "Description of advice #1",
            "actionable_item": "What action the user should take, and where to go"
            }},
            {{
            "title": "Title of Advice #2",
            "recommendation": "Description of advice #2",
            "actionable_item": "What action the user should take, and where to go"
            }}
              ]
            }}

             """

            response = self.generate_text(prompt)

            return response

    def create_goal_plan(self, user_data, financial_goal):
            """Creates a goal plan based on the user's current financial situation and goal."""

            prompt = f"""
                You are an expert AI financial advisor tasked with creating a personalized financial plan for users.

                User Data: {user_data}
                Financial Goal: {financial_goal}

                Based on the user's data and their financial goal, create a detailed financial plan for the user.
                The goal of this plan is for the user to successfully meet their financial goal in the most efficient way possible.

                Provide specific steps, actions, and strategies they can take. Be specific, and provide your plan in a structured format using the following JSON format:
                 {{
                 "plan_summary": "A short summary of the entire financial plan",
                 "plan_steps": [
                   {{
                    "step": "Detailed plan step #1",
                    "actionable_item": "What action the user should take, and where to go"
                   }},
                  {{
                    "step": "Detailed plan step #2",
                    "actionable_item": "What action the user should take, and where to go"
                   }}
                 ]
                }}
             """

            response = self.generate_text(prompt)

            return response

def get_gemini_insights(user_data):
    url = "https://api.google.com/gemini/insights"
    headers = {"Authorization": f"Bearer {os.getenv('GOOGLE_GEMINI_API_KEY')}"}
    payload = {"user_data": user_data}

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch insights from Google Gemini: {response.status_code} {response.text}")