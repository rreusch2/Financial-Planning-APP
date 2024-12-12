import React from 'react';
import { Brain } from 'lucide-react';

interface AIInsightsProps {
  insights: string | null;
  loading?: boolean;
}

export function AIInsights({ insights, loading }: AIInsightsProps) {
  return (
    <div className="bg-white shadow rounded-lg">
      <div className="p-6">
        <div className="flex items-center mb-4">
          <Brain className="h-6 w-6 text-indigo-600 mr-2" />
          <h2 className="text-lg font-medium text-gray-900">AI Insights</h2>
        </div>
        <div className="prose max-w-none">
          {loading ? (
            <p className="text-gray-500">Analyzing your financial data...</p>
          ) : insights ? (
            <p className="text-gray-600">{insights}</p>
          ) : (
            <p className="text-gray-500">Connect your bank account to get AI-powered insights</p>
          )}
        </div>
      </div>
    </div>
  );
}