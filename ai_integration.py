from typing import List, Dict
import openai
import logging
import os
from datetime import datetime, timedelta
from pydantic import BaseModel
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

class TransactionAnalysis(BaseModel):
    category: str
    confidence: float
    insights: str
    budget_impact: str

class AIFinancialAdvisor:
    def __init__(self, api_key: str = None):
        self.client = openai.OpenAI(api_key=api_key or os.environ.get('OPENAI_API_KEY'))
        
    def analyze_spending_patterns(self, transactions: List[Dict]) -> Dict:
        """Analyze spending patterns and provide detailed insights."""
        try:
            # Calculate basic spending metrics
            spending_by_category = self._calculate_spending(transactions)
            spending_trends = self._analyze_spending_trends(transactions)
            unusual_transactions = self._identify_unusual_transactions(transactions)
            recurring_expenses = self._identify_recurring_expenses(transactions)
            
            # Calculate total spending correctly
            total_spending = sum(cat_data['total'] for cat_data in spending_by_category.values())
            
            prompt = """
            Analyze the following financial data and provide detailed insights:

            Spending Categories: {categories}
            Total Monthly Spending: ${total}
            Month-over-Month Trends: {trends}
            Unusual Transactions: {unusual}
            Recurring Expenses: {recurring}

            Please provide:
            1. Key Insights:
               - Identify major spending patterns
               - Highlight significant changes in spending
               - Point out potential areas of concern

            2. Savings Recommendations:
               - Specific actionable suggestions for reducing expenses
               - Potential monthly savings amounts
               - Priority areas for cost reduction

            3. Risk Assessment:
               - Evaluate spending sustainability
               - Identify potential financial risks
               - Suggest preventive measures

            4. Budget Optimization:
               - Recommend category-specific budget adjustments
               - Suggest optimal spending allocation
               - Provide specific steps for implementation

            5. Future Projections:
               - Project next month's expenses
               - Identify seasonal spending patterns
               - Suggest proactive financial planning steps
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are a sophisticated financial advisor. Provide specific, actionable insights based on spending data."
                },
                {
                    "role": "user",
                    "content": prompt.format(
                        categories=dict(spending_by_category),
                        total=total_spending,
                        trends=spending_trends,
                        unusual=unusual_transactions,
                        recurring=recurring_expenses
                    )
                }]
            )
            
            return {
                'analysis': response.choices[0].message.content,
                'spending_data': dict(spending_by_category),
                'trends': spending_trends,
                'unusual_transactions': unusual_transactions,
                'recurring_expenses': recurring_expenses,
                'total_spending': total_spending,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in spending analysis: {str(e)}")
            return {
                'error': str(e),
                'spending_data': {},
                'trends': {},
                'unusual_transactions': [],
                'recurring_expenses': [],
                'total_spending': 0,
                'timestamp': datetime.now().isoformat()
            }

    def _calculate_spending(self, transactions: List[Dict]) -> Dict:
        """Calculate spending by category with additional metrics."""
        spending = defaultdict(lambda: {
            'total': 0,
            'count': 0,
            'average': 0,
            'max': 0,
            'min': float('inf')
        })
        
        for transaction in transactions:
            if transaction['amount'] < 0:
                category = transaction.get('category', 'Uncategorized')
                amount = abs(transaction['amount'])
                
                cat_data = spending[category]
                cat_data['total'] += amount
                cat_data['count'] += 1
                cat_data['max'] = max(cat_data['max'], amount)
                cat_data['min'] = min(cat_data['min'], amount)
                cat_data['average'] = cat_data['total'] / cat_data['count']
        
        return dict(spending)

    def _analyze_spending_trends(self, transactions: List[Dict]) -> Dict:
        """Analyze month-over-month spending trends."""
        monthly_spending = defaultdict(float)
        
        for transaction in transactions:
            if transaction['amount'] < 0:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                monthly_spending[month_key] += abs(transaction['amount'])
        
        # Calculate month-over-month changes
        months = sorted(monthly_spending.keys())
        trends = {}
        
        for i in range(1, len(months)):
            current_month = months[i]
            prev_month = months[i-1]
            change = ((monthly_spending[current_month] - monthly_spending[prev_month]) 
                     / monthly_spending[prev_month] * 100)
            trends[current_month] = {
                'change_percentage': round(change, 2),
                'current_spending': round(monthly_spending[current_month], 2),
                'previous_spending': round(monthly_spending[prev_month], 2)
            }
        
        return trends

    def _identify_unusual_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Identify statistically unusual transactions."""
        category_stats = defaultdict(list)
        unusual_transactions = []
        
        # Calculate category statistics
        for transaction in transactions:
            if transaction['amount'] < 0:
                category = transaction.get('category', 'Uncategorized')
                category_stats[category].append(abs(transaction['amount']))
        
        # Identify outliers using Z-score
        for transaction in transactions:
            if transaction['amount'] < 0:
                category = transaction.get('category', 'Uncategorized')
                amount = abs(transaction['amount'])
                amounts = category_stats[category]
                
                if len(amounts) > 0:
                    mean = np.mean(amounts)
                    std = np.std(amounts)
                    z_score = (amount - mean) / std if std > 0 else 0
                    
                    if abs(z_score) > 2:  # More than 2 standard deviations
                        unusual_transactions.append({
                            'transaction': transaction,
                            'z_score': z_score,
                            'average_for_category': mean
                        })
        
        return unusual_transactions

    def _identify_recurring_expenses(self, transactions: List[Dict]) -> List[Dict]:
        """Identify recurring expenses and subscriptions."""
        merchant_transactions = defaultdict(list)
        recurring_expenses = []
        
        # Group transactions by merchant
        for transaction in transactions:
            if transaction['amount'] < 0:
                merchant = transaction.get('merchant_name', transaction.get('name', ''))
                merchant_transactions[merchant].append({
                    'amount': abs(transaction['amount']),
                    'date': datetime.strptime(transaction['date'], '%Y-%m-%d')
                })
        
        # Identify recurring patterns
        for merchant, trans in merchant_transactions.items():
            if len(trans) >= 2:
                amounts = [t['amount'] for t in trans]
                dates = [t['date'] for t in trans]
                
                # Check for consistent amounts and regular intervals
                amount_std = np.std(amounts)
                if amount_std < 1:  # Very consistent amounts
                    date_diffs = [(dates[i] - dates[i-1]).days 
                                for i in range(1, len(dates))]
                    mean_interval = np.mean(date_diffs)
                    interval_std = np.std(date_diffs)
                    
                    if interval_std < 5:  # Consistent intervals
                        recurring_expenses.append({
                            'merchant': merchant,
                            'amount': np.mean(amounts),
                            'interval_days': mean_interval,
                            'confidence': 'high' if interval_std < 2 else 'medium'
                        })
        
        return recurring_expenses

    def enhance_transaction_categorization(
        self, 
        transaction: str,
        xgb_category: str
    ) -> TransactionAnalysis:
        """Enhance transaction categorization with AI insights."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "user",
                    "content": self._create_categorization_prompt(transaction, xgb_category)
                }]
            )
            
            return TransactionAnalysis.parse_raw(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error in transaction enhancement: {str(e)}")
            return None

    def _create_categorization_prompt(self, transaction: str, category: str) -> str:
        """Create detailed prompt for transaction categorization."""
        return f"""
        Analyze this transaction and provide:
        1. Verified or corrected category (from: {category})
        2. Confidence score (0-1)
        3. Transaction purpose insights
        4. Budget impact assessment
        5. Potential savings opportunities

        Transaction: {transaction}
        Initial Category: {category}
        """