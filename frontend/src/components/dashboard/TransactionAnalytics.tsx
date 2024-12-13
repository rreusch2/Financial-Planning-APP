import React from 'react';
import { BarChart, DollarSign, TrendingUp, TrendingDown } from 'lucide-react';
import { motion } from 'framer-motion';
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

interface TransactionAnalyticsProps {
  transactions?: Array<{
    id: string;
    date: string;
    name: string;
    amount: number;
    category: string;
  }>;
  patterns?: {
    trend: number;
    categories: Record<string, number>;
    predictions: Array<{ date: string; amount: number }>;
  };
}

export function TransactionAnalytics({ transactions, patterns }: TransactionAnalyticsProps) {
  if (!transactions?.length) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="text-center text-gray-500">
          {patterns ? 'No transactions found' : 'Loading transactions...'}
        </div>
      </div>
    );
  }

  const categoryData = patterns?.categories ? 
    Object.entries(patterns.categories).map(([name, value]) => ({
      name,
      value
    })) : [];

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">Transaction Analytics</h3>
          <p className="text-sm text-gray-500">Your spending patterns</p>
        </div>
        <BarChart className="h-6 w-6 text-indigo-600" />
      </div>

      <div className="space-y-6">
        {/* Spending Trend */}
        {patterns && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-gradient-to-br from-indigo-50 to-white rounded-lg p-4"
          >
            <h4 className="font-medium text-gray-900 mb-2">Spending Trend</h4>
            <div className="flex items-center gap-2">
              {patterns.trend > 0 ? (
                <TrendingUp className="h-5 w-5 text-red-600" />
              ) : (
                <TrendingDown className="h-5 w-5 text-green-600" />
              )}
              <span className="text-sm text-gray-600">
                {Math.abs(patterns.trend)}% {patterns.trend > 0 ? 'increase' : 'decrease'} from last month
              </span>
            </div>
          </motion.div>
        )}

        {/* Category Breakdown */}
        <div className="h-64">
          <h4 className="font-medium text-gray-900 mb-4">Category Breakdown</h4>
          <ResponsiveContainer width="100%" height="100%">
            <RechartsBarChart data={categoryData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#4F46E5" />
            </RechartsBarChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Transactions */}
        <div>
          <h4 className="font-medium text-gray-900 mb-4">Recent Transactions</h4>
          <div className="space-y-2">
            {transactions?.slice(0, 5).map((tx) => (
              <motion.div
                key={tx.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex justify-between items-center p-3 rounded-lg hover:bg-gray-50"
              >
                <div>
                  <p className="font-medium text-gray-900">{tx.name}</p>
                  <p className="text-sm text-gray-500">{tx.category}</p>
                </div>
                <span className={`font-medium ${tx.amount < 0 ? 'text-red-600' : 'text-green-600'}`}>
                  ${Math.abs(tx.amount).toFixed(2)}
                </span>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 