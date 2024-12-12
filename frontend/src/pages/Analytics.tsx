import React from 'react';
import { LineChart, BarChart } from 'lucide-react';

export default function Analytics() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Financial Analytics</h1>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center mb-4">
            <LineChart className="h-6 w-6 text-indigo-600 mr-2" />
            <h2 className="text-lg font-medium">Spending Trends</h2>
          </div>
          <div className="h-64 bg-gray-50 rounded flex items-center justify-center">
            <p className="text-gray-500">Chart will be implemented here</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center mb-4">
            <BarChart className="h-6 w-6 text-indigo-600 mr-2" />
            <h2 className="text-lg font-medium">Category Breakdown</h2>
          </div>
          <div className="h-64 bg-gray-50 rounded flex items-center justify-center">
            <p className="text-gray-500">Chart will be implemented here</p>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-medium mb-4">AI Insights</h2>
        <div className="space-y-4">
          <p className="text-gray-600">
            AI-powered insights about your spending patterns and financial health will appear here.
          </p>
        </div>
      </div>
    </div>
  );
}