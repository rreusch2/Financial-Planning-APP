import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { Dialog } from '@headlessui/react';
import { Loader, Search, X, RefreshCw } from 'lucide-react'; // Added RefreshCw icon

function AIAdvice() {
  // State for AI Advice
  const [advice, setAdvice] = useState('');
  const [isLoadingAdvice, setIsLoadingAdvice] = useState(false);
  const [adviceError, setAdviceError] = useState(null);

  // State for Expenses
  const [expenses, setExpenses] = useState([]); // Default to an empty array
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('');
  const [timeFrame, setTimeFrame] = useState('monthly');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedExpense, setSelectedExpense] = useState(null);
  const [sortBy, setSortBy] = useState({ field: 'date', direction: 'desc' });

  // Fetch AI Advice
  const fetchAIAdvice = async () => {
    setIsLoadingAdvice(true);
    setAdviceError(null);
    try {
      const response = await fetch('/api/ai_advice');
      if (!response.ok) throw new Error('Failed to fetch AI advice');
      const data = await response.json();
      setAdvice(data.response || 'No advice available at this time.');
    } catch (err) {
      setAdviceError(err.message || 'An error occurred while fetching AI advice.');
      console.error('Error fetching AI advice:', err);
    } finally {
      setIsLoadingAdvice(false);
    }
  };

  // Fetch Expense Data
  const fetchExpenseData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/transactions');
      if (!response.ok) throw new Error('Failed to fetch expense data');
      const data = await response.json();
      setExpenses(data.transactions || []); // Default to empty array if no transactions
    } catch (err) {
      setError(err.message || 'An error occurred while fetching expenses.');
      console.error('Error fetching expense data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAIAdvice();
    fetchExpenseData();
  }, []);

  const handleExpenseClick = (expense) => {
    setSelectedExpense(expense);
    setIsDialogOpen(true);
  };

  const sortedAndFilteredExpenses = (expenses || []) // Ensure expenses is always an array
    .filter((expense) =>
      filter === '' ||
      expense.name.toLowerCase().includes(filter.toLowerCase()) ||
      expense.category.toLowerCase().includes(filter.toLowerCase())
    )
    .sort((a, b) => {
      const modifier = sortBy.direction === 'asc' ? 1 : -1;
      return a[sortBy.field] > b[sortBy.field] ? modifier : -modifier;
    });

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader className="animate-spin h-8 w-8 text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4">
      {/* AI Advice Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">AI Financial Insights</h2>
          <button
            onClick={fetchAIAdvice}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            disabled={isLoadingAdvice}
          >
            <RefreshCw className={`h-4 w-4 ${isLoadingAdvice ? 'animate-spin' : ''}`} />
            Refresh Advice
          </button>
        </div>

        {isLoadingAdvice ? (
          <div className="flex justify-center py-4">
            <Loader className="animate-spin h-6 w-6 text-blue-500" />
          </div>
        ) : adviceError ? (
          <div className="text-red-500">{adviceError}</div>
        ) : (
          <div className="prose">
            <p className="text-gray-700">{advice}</p>
          </div>
        )}
      </div>

      {/* Expense Tracking Section */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4">
          <h2 className="text-xl font-semibold mb-4">Expense Overview</h2>

          <div className="flex flex-wrap gap-4 mb-4">
            <select
              value={timeFrame}
              onChange={(e) => setTimeFrame(e.target.value)}
              className="border rounded p-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="yearly">Yearly</option>
            </select>

            <div className="relative flex-1">
              <input
                type="text"
                placeholder="Search expenses..."
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded focus:ring-2 focus:ring-blue-500"
              />
              <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
            </div>
          </div>

          <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {sortedAndFilteredExpenses.map((expense) => (
              <div
                key={expense.transaction_id}
                className="p-4 border rounded-lg shadow cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => handleExpenseClick(expense)}
              >
                <h3 className="font-bold">{expense.name}</h3>
                <p className={`text-${expense.amount < 0 ? 'red' : 'green'}-600`}>
                  ${Math.abs(expense.amount).toFixed(2)}
                </p>
                <p className="text-sm text-gray-500">{expense.date}</p>
                <span className="inline-block px-2 py-1 mt-2 text-xs bg-gray-100 rounded">
                  {expense.category}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AIAdvice;
