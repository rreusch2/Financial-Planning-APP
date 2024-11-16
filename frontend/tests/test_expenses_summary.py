import unittest
from app import app
import json

class TestExpensesSummaryEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_get_expenses_summary(self):
        response = self.app.get('/api/expenses_summary?period=monthly')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn('category', data[0])
        self.assertIn('amount', data[0])