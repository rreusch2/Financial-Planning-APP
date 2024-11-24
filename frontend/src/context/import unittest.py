import unittest
from unittest.mock import patch, MagicMock
from openai_utils import generate_financial_advice, generate_transaction_category

class TestOpenAIUtils(unittest.TestCase):

    @patch('openai_utils.client.completions.create')
    def test_generate_financial_advice_success(self, mock_create):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(text="This is financial advice.")]
        mock_create.return_value = mock_response

        result = generate_financial_advice("How should I invest my money?")
        self.assertEqual(result, "This is financial advice.")

    @patch('openai_utils.client.completions.create')
    def test_generate_financial_advice_api_error(self, mock_create):
        mock_create.side_effect = OpenAIError("API error")

        result = generate_financial_advice("How should I invest my money?")
        self.assertEqual(result, "An error occurred while generating financial advice.")

    @patch('openai_utils.client.completions.create')
    def test_generate_financial_advice_unexpected_error(self, mock_create):
        mock_create.side_effect = Exception("Unexpected error")

        result = generate_financial_advice("How should I invest my money?")
        self.assertEqual(result, "An unexpected error occurred while generating financial advice.")

    @patch('openai_utils.openai.Completion.create')
    def test_generate_transaction_category_success(self, mock_create):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(text="Groceries")]
        mock_create.return_value = mock_response

        result = generate_transaction_category("Bought vegetables and fruits")
        self.assertEqual(result, "Groceries")

    @patch('openai_utils.openai.Completion.create')
    def test_generate_transaction_category_api_error(self, mock_create):
        mock_create.side_effect = OpenAIError("API error")

        result = generate_transaction_category("Bought vegetables and fruits")
        self.assertEqual(result, "Uncategorized")

    @patch('openai_utils.openai.Completion.create')
    def test_generate_transaction_category_unexpected_error(self, mock_create):
        mock_create.side_effect = Exception("Unexpected error")

        result = generate_transaction_category("Bought vegetables and fruits")
        self.assertEqual(result, "Uncategorized")

if __name__ == '__main__':
    unittest.main()