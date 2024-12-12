from .base import BaseAIService
from typing import Dict, List
from collections import defaultdict
import numpy as np
from datetime import datetime

class TransactionAnalyzer(BaseAIService):
    def analyze_transaction(self, transaction_data):
        messages = [
            {
                "role": "system",
                "content": "You are a financial analyst specializing in personal spending patterns and budget optimization."
            },
            {
                "role": "user",
                "content": f"Analyze this transaction: {transaction_data}"
            }
        ]
        
        analysis = self._create_completion(messages)
        return analysis or "Unable to analyze transaction at this time."
    
    def analyze_spending_patterns(self, transactions: List[Dict]) -> Dict:
        spending_data = self._calculate_spending(transactions)
        trends = self._analyze_trends(transactions)
        unusual = self._identify_unusual_transactions(transactions)
        recurring = self._identify_recurring_expenses(transactions)
        
        total_spending = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)
        
        prompt = f"""
        Analyze the following financial data and provide detailed insights:

        Spending Categories: {spending_data}
        Total Monthly Spending: ${total_spending}
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
        
        analysis = self._create_completion([{
            "role": "system",
            "content": "You are a sophisticated financial advisor providing specific, actionable insights."
        }, {
            "role": "user",
            "content": prompt
        }], model="gpt-4")
        
        return {
            'analysis': analysis,
            'spending_data': spending_data,
            'trends': trends,
            'unusual_transactions': unusual,
            'recurring_expenses': recurring,
            'total_spending': total_spending,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_spending(self, transactions: List[Dict]) -> Dict:
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
    
    def _analyze_trends(self, transactions: List[Dict]) -> Dict:
        monthly_spending = defaultdict(float)
        
        for transaction in transactions:
            if transaction['amount'] < 0:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                monthly_spending[month_key] += abs(transaction['amount'])
        
        return self._calculate_month_over_month_changes(monthly_spending)
    
    def _calculate_month_over_month_changes(self, monthly_spending: Dict) -> Dict:
        months = sorted(monthly_spending.keys())
        trends = {}
        
        for i in range(1, len(months)):
            current = months[i]
            previous = months[i-1]
            change = ((monthly_spending[current] - monthly_spending[previous]) 
                     / monthly_spending[previous] * 100)
            trends[current] = {
                'change_percentage': round(change, 2),
                'current_spending': round(monthly_spending[current], 2),
                'previous_spending': round(monthly_spending[previous], 2)
            }
        
        return trends
    
    def _identify_unusual_transactions(self, transactions: List[Dict]) -> List[Dict]:
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