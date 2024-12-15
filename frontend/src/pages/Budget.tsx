import React, { useState, useEffect } from 'react';
import { Card, Input, Button, Progress } from 'antd';
import Layout from '../components/Layout';
import { cn } from '../lib/utils';

interface Budget {
  category: string;
  limit: number;
}

function BudgetPage() {
  const [budgets, setBudgets] = useState<Budget[]>([
    { category: 'Food and Drink', limit: 500 },
    { category: 'Shopping', limit: 300 },
    { category: 'Transportation', limit: 200 },
    { category: 'Entertainment', limit: 150 }
  ]);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSuggestions = async () => {
      try {
        const response = await fetch('/api/budget/suggestions');
        if (!response.ok) {
          throw new Error('Failed to fetch suggestions');
        }
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      } catch (error) {
        console.error('Error fetching suggestions:', error);
        setError('Could not load suggestions');
      }
    };

    fetchSuggestions();
  }, [budgets]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/budget', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(budgets),
      });
      const data = await response.json();
      console.log(data.message);
    } catch (error) {
      console.error('Error saving budgets:', error);
    }
  };

  return (
    <Layout>
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-gray-900">Budget Management</h1>
          <p className="mt-2 text-sm text-gray-600">
            Set and manage your monthly spending limits by category
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Current Budget Overview */}
          <Card title="Current Budgets" className="shadow-sm">
            {budgets.map((budget, index) => (
              <div key={index} className="mb-4">
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">{budget.category}</span>
                  <span className="text-sm text-gray-600">${budget.limit}</span>
                </div>
                <Progress 
                  percent={0} 
                  status="active"
                  strokeColor={getColorForCategory(budget.category)}
                />
              </div>
            ))}
          </Card>

          {/* Budget Setting Form */}
          <Card title="Set New Budgets" className="shadow-sm">
            <form onSubmit={handleSubmit} className="space-y-4">
              {budgets.map((budget, index) => (
                <div key={index} className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">
                    {budget.category}
                  </label>
                  <Input
                    type="number"
                    value={budget.limit}
                    onChange={(e) => {
                      const newBudgets = [...budgets];
                      newBudgets[index].limit = Number(e.target.value);
                      setBudgets(newBudgets);
                    }}
                    className="w-full"
                    prefix="$"
                  />
                </div>
              ))}
              <Button 
                type="primary"
                htmlType="submit"
                className={cn(
                  "w-full bg-indigo-600 hover:bg-indigo-700",
                  "text-white font-medium py-2 px-4 rounded-md"
                )}
              >
                Save Budgets
              </Button>
            </form>
          </Card>
        </div>

        {/* AI Suggestions */}
        <div className="mt-6">
          <h2 className="text-lg font-semibold text-gray-900">AI Budget Suggestions</h2>
          {error ? (
            <p className="text-sm text-red-500">{error}</p>
          ) : (
            <ul className="list-disc pl-5 mt-2">
              {suggestions.map((suggestion, index) => (
                <li key={index} className="text-sm text-gray-700">
                  {suggestion.suggestion}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </Layout>
  );
}

// Helper function to get consistent colors
function getColorForCategory(category: string): string {
  const colors: Record<string, string> = {
    'Food and Drink': '#1890ff',
    'Shopping': '#52c41a',
    'Transportation': '#722ed1',
    'Entertainment': '#fa8c16'
  };
  return colors[category] || '#8c8c8c';
}

export default BudgetPage; 