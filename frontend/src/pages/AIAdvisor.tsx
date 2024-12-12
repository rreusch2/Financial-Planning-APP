import React from 'react';
import { Brain, MessageSquare, TrendingUp } from 'lucide-react';

export default function AIAdvisor() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">AI Financial Advisor</h1>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Brain className="h-6 w-6 text-indigo-600 mr-2" />
          <h2 className="text-lg font-medium">Personalized Insights</h2>
        </div>
        <div className="prose max-w-none">
          <p>
            Your AI financial advisor is analyzing your spending patterns and financial behavior...
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center mb-4">
            <MessageSquare className="h-6 w-6 text-indigo-600 mr-2" />
            <h2 className="text-lg font-medium">Ask AI Advisor</h2>
          </div>
          <div className="space-y-4">
            <textarea
              rows={4}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              placeholder="Ask me anything about your finances..."
            />
            <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
              Get Advice
            </button>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center mb-4">
            <TrendingUp className="h-6 w-6 text-indigo-600 mr-2" />
            <h2 className="text-lg font-medium">Financial Health Score</h2>
          </div>
          <div className="text-center">
            <div className="text-5xl font-bold text-indigo-600">85</div>
            <p className="mt-2 text-sm text-gray-500">Your financial health score</p>
          </div>
        </div>
      </div>
    </div>
  );
}