from .base import BaseAIService
from typing import Dict, List, Tuple
from datetime import datetime
import numpy as np
from collections import defaultdict

class TransactionAnalyzer(BaseAIService):
    def categorize_transaction(self, description: str, amount: float) -> Dict[str, any]:
        """Use AI to categorize a transaction and determine if it's income or expense."""
        prompt = f"""
        Analyze this transaction:
        Description: {description}
        Amount: ${amount}

        Provide the following in your analysis:
        1. Category (e.g., Dining, Shopping, Salary, Investment)
        2. Type (income or expense)
        3. Confidence score (0-100)
        4. Sub-category (more specific classification)
        5. Tags (relevant keywords)
        """

        response = self._create_completion([{
            "role": "system",
            "content": "You are a financial transaction analyzer specializing in categorization and pattern recognition."
        }, {
            "role": "user",
            "content": prompt
        }])

        # Parse the AI response and structure it
        # (You'll need to implement proper response parsing based on your AI model's output format)
        return {
            'category': 'parsed_category',
            'type': 'income' if amount > 0 else 'expense',
            'confidence': 85,
            'sub_category': 'parsed_sub_category',
            'tags': ['parsed', 'tags']
        }

    def analyze_spending_patterns(self, transactions: List[Dict]) -> Dict:
        """Analyze spending patterns and provide insights."""
        
        total_spending = sum(t['amount'] for t in transactions if t['amount'] < 0)
        categories = self._group_by_category(transactions)
    
        prompt = f"""
        Analyze these spending patterns:
        Total Spending: ${abs(total_spending)}
        Categories: {categories}

        Provide:
        1. Key spending insights
        2. Unusual patterns
        3. Recommendations for savings
        4. Predicted spending trends
        5. Budget suggestions by category
        """

        analysis = self._create_completion([{
            "role": "system",
            "content": "You are a financial analyst specializing in personal spending patterns and budget optimization."
        }, {
            "role": "user",
            "content": prompt
        }], model="gpt-3.5-turbo")

    # Shorten the analysis to be more concise
        shortened_analysis = self._shorten_analysis(analysis)

        return {
            'analysis': shortened_analysis,
            'spending_data': categories,
            'predictions': self._generate_predictions(transactions),
            'anomalies': self._detect_anomalies(transactions)
        }

    def _shorten_analysis(self, analysis: str) -> str:
        """Shorten the AI analysis to be more concise and user-friendly."""
        lines = analysis.split('\n')
        shortened_lines = []
        for line in lines:
            if len(line) > 100:
                shortened_lines.append(line[:97] + '...')
            else:
                shortened_lines.append(line)
        return '\n'.join(shortened_lines)

    def _group_by_category(self, transactions: List[Dict]) -> Dict[str, float]:
        """Group transactions by category and calculate totals."""
        categories = defaultdict(float)
        for t in transactions:
            categories[t.get('category', 'Other')] += abs(t['amount'])
        return dict(categories)

    def _generate_predictions(self, transactions: List[Dict]) -> Dict:
        """Generate spending predictions using historical data."""
        # Implement time series analysis and prediction logic
        return {
            'next_month_prediction': 0,
            'confidence': 0,
            'trend': 'stable'
        }

    def _detect_anomalies(self, transactions: List[Dict]) -> List[Dict]:
        """Detect unusual spending patterns."""
        # Implement anomaly detection logic
        return []

    def get_smart_budget_recommendations(self, 
        spending_history: List[Dict],
        income: float
    ) -> Dict[str, Dict]:
        """Generate AI-powered budget recommendations."""
        categories = self._group_by_category(spending_history)
        
        prompt = f"""
        Based on:
        Monthly Income: ${income}
        Current Spending by Category: {categories}

        Provide:
        1. Recommended budget allocation by category
        2. Potential savings opportunities
        3. Specific action items to optimize spending
        4. Risk areas in current spending patterns
        """

        recommendations = self._create_completion([{
            "role": "system",
            "content": "You are a budgeting expert providing practical and actionable advice."
        }, {
            "role": "user",
            "content": prompt
        }])

        return {
            'recommendations': recommendations,
            'budget_allocation': self._calculate_budget_allocation(income, categories),
            'savings_potential': self._calculate_savings_potential(categories)
        }