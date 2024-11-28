from typing import List, Dict
import openai
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class AIFinancialAdvisor:
    def __init__(self, api_key: str = None):
        if api_key:
            openai.api_key = api_key
        else:
            # Set the API key from environment variable
            openai.api_key = os.environ.get('OPENAI_API_KEY')

    def analyze_spending_patterns(self, transactions: List[Dict]) -> Dict:
        logger.debug("Starting spending analysis.")
        try:
            logger.debug(f"Transactions received: {transactions}")

            # Prepare transaction data
            spending_by_category = {}
            total_spending = 0
            for transaction in transactions:
                if transaction['amount'] < 0:  # Only analyze expenses
                    category = transaction.get('category', 'Uncategorized')
                    amount = abs(transaction['amount'])
                    spending_by_category[category] = spending_by_category.get(category, 0) + amount
                    total_spending += amount
            logger.debug(f"Spending by category: {spending_by_category}")
            logger.debug(f"Total spending calculated: {total_spending}")

            # Create prompt
            prompt = f"""
            Analyze these spending patterns and provide personalized financial advice:
            Total Spending: ${total_spending:.2f}
            Spending by Category:
            {spending_by_category}

            Provide:
            1. Main insights about spending patterns
            2. Specific recommendations for savings
            3. Areas of concern
            4. Positive financial habits
            5. Action items for improvement

            Note from website creator: Please make this a somewhat condensed response that would be easy fo a user to understand and implement and that would look good on my website dashboard page.
            """
            logger.debug(f"Generated prompt for OpenAI: {prompt}")

            # Make OpenAI API call
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial advisor providing actionable advice."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    },
                ],
                temperature=0.7,
                max_tokens=500,
            )
            logger.debug(f"OpenAI response: {response}")

            advice = response['choices'][0]['message']['content']
            logger.info("AI advice generated successfully.")
            return {
                'summary': {
                    'total_spending': total_spending,
                    'spending_by_category': spending_by_category,
                },
                'advice': advice,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error in spending analysis: {str(e)}", exc_info=True)
            return {'error': str(e)}

    def generate_savings_plan(
        self,
        monthly_income: float,
        monthly_expenses: float,
        savings_goal: float,
        timeframe_months: int,
    ) -> Dict:
        """Generate a personalized savings plan."""
        try:
            monthly_savings_needed = savings_goal / timeframe_months
            current_savings_capacity = monthly_income - monthly_expenses

            prompt = f"""
            Create a savings plan with:
            Monthly Income: ${monthly_income:.2f}
            Monthly Expenses: ${monthly_expenses:.2f}
            Savings Goal: ${savings_goal:.2f}
            Timeframe: {timeframe_months} months
            Required Monthly Savings: ${monthly_savings_needed:.2f}
            Current Savings Capacity: ${current_savings_capacity:.2f}

            Provide:
            1. Steps to reach the goal
            2. Areas to reduce expenses
            3. Additional income opportunities
            4. Monthly milestones
            5. Risk factors and mitigation strategies

            Note from website creator: Please make this a somewhat condensed response that would be easy fo a user to understand and implement and that would look good on my website dashboard page.
            """

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial planner providing actionable savings plans."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    },
                ],
                temperature=0.7,
                max_tokens=500,
            )

            plan = response['choices'][0]['message']['content']

            return {
                'plan': plan,
                'monthly_target': monthly_savings_needed,
                'feasibility_score': min(1.0, current_savings_capacity / monthly_savings_needed)
                if monthly_savings_needed else 0.0,
                'generated_at': datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error generating savings plan: {str(e)}")
            return {'error': str(e)}