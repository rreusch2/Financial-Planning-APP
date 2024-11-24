import openai
from typing import List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AIFinancialAdvisor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key

    async def analyze_spending_patterns(self, transactions: List[Dict]) -> Dict:
        """Analyze transaction patterns and provide insights"""
        try:
            # Prepare transaction data for analysis
            spending_by_category = {}
            total_spending = 0
            
            for transaction in transactions:
                if transaction['amount'] < 0:  # Only analyze expenses
                    category = transaction.get('category', 'Uncategorized')
                    amount = abs(transaction['amount'])
                    spending_by_category[category] = spending_by_category.get(category, 0) + amount
                    total_spending += amount

            # Create prompt for OpenAI
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
            """

            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional financial advisor focused on practical, actionable advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            # Process and structure the response
            advice = response.choices[0].message.content

            return {
                'summary': {
                    'total_spending': total_spending,
                    'top_categories': sorted(spending_by_category.items(), key=lambda x: x[1], reverse=True)[:3]
                },
                'advice': advice,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            raise

    async def generate_savings_plan(self, 
                                  monthly_income: float,
                                  monthly_expenses: float,
                                  savings_goal: float,
                                  timeframe_months: int) -> Dict:
        """Generate a personalized savings plan"""
        try:
            monthly_savings_needed = savings_goal / timeframe_months
            current_savings_capacity = monthly_income - monthly_expenses

            prompt = f"""
            Create a detailed savings plan with these parameters:
            Monthly Income: ${monthly_income:.2f}
            Monthly Expenses: ${monthly_expenses:.2f}
            Savings Goal: ${savings_goal:.2f}
            Timeframe: {timeframe_months} months
            Required Monthly Savings: ${monthly_savings_needed:.2f}
            Current Savings Capacity: ${current_savings_capacity:.2f}

            Provide:
            1. Specific steps to reach the savings goal
            2. Areas where expenses could be reduced
            3. Additional income opportunities if needed
            4. Monthly milestones and checkpoints
            5. Risk factors and mitigation strategies
            """

            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial planning expert focused on achievable savings goals."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return {
                'plan': response.choices[0].message.content,
                'monthly_target': monthly_savings_needed,
                'feasibility_score': min(1.0, current_savings_capacity / monthly_savings_needed),
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating savings plan: {str(e)}")
            raise