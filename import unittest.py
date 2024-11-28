import unittest
from unittest.mock import patch, MagicMock
from ai_integration import AIFinancialAdvisor

class TestAIFinancialAdvisor(unittest.TestCase):

    @patch('ai_integration.openai.Chat.create')
    def test_analyze_spending_patterns_success(self, mock_create):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message={'content': "This is financial advice."})]
        mock_create.return_value = mock_response

        advisor = AIFinancialAdvisor(api_key="test_key")
        transactions = [{'amount': -50, 'category': 'Food'}]
        result = advisor.analyze_spending_patterns(transactions)
        self.assertEqual(result['advice'], "This is financial advice.")

    @patch('ai_integration.openai.Chat.create')
    def test_generate_savings_plan_success(self, mock_create):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message={'content': "This is a savings plan."})]
        mock_create.return_value = mock_response

        advisor = AIFinancialAdvisor(api_key="test_key")
        result = advisor.generate_savings_plan(5000, 3000, 10000, 12)
        self.assertEqual(result['plan'], "This is a savings plan.")

if __name__ == '__main__':
    unittest.main()
