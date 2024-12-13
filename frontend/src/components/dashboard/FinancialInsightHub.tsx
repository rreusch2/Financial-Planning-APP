import React from 'react';
import { Brain, Sparkles, TrendingUp, Target, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface InsightCardProps {
  title: string;
  content: string;
  type: 'prediction' | 'alert' | 'opportunity';
  confidence: number;
}

const InsightCard = ({ title, content, type, confidence }: InsightCardProps) => {
  const getIcon = () => {
    switch (type) {
      case 'prediction':
        return <Brain className="h-6 w-6 text-indigo-600" />;
      case 'alert':
        return <AlertCircle className="h-6 w-6 text-amber-600" />;
      case 'opportunity':
        return <Target className="h-6 w-6 text-green-600" />;
    }
  };

  const getGradient = () => {
    switch (type) {
      case 'prediction':
        return 'from-indigo-50 to-white';
      case 'alert':
        return 'from-amber-50 to-white';
      case 'opportunity':
        return 'from-green-50 to-white';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-gradient-to-br ${getGradient()} rounded-xl shadow-sm p-6 hover:shadow-md transition-all duration-200`}
    >
      <div className="flex items-center gap-3 mb-4">
        {getIcon()}
        <div className="flex-1">
          <h3 className="font-semibold text-lg">{title}</h3>
          <div className="flex items-center gap-2">
            <div className="h-2 w-16 bg-gray-200 rounded-full">
              <div 
                className="h-full bg-indigo-600 rounded-full"
                style={{ width: `${confidence}%` }}
              />
            </div>
            <span className="text-sm text-gray-500">
              {confidence}% confidence
            </span>
          </div>
        </div>
      </div>
      <p className="text-gray-600">{content}</p>
    </motion.div>
  );
};

interface FinancialInsightHubProps {
  insights?: {
    predictions: Array<{
      title: string;
      content: string;
      confidence: number;
      type: 'prediction' | 'alert' | 'opportunity';
    }>;
    analysis: string;
  };
}

export function FinancialInsightHub({ insights }: FinancialInsightHubProps) {
  if (!insights?.predictions) {
    return (
      <div className="p-6 text-center">
        <p className="text-gray-500">Loading insights...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">AI Financial Insights</h2>
          <p className="text-gray-500">Powered by Google Gemini</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-indigo-600">
          <Sparkles className="h-4 w-4" />
          <span>Last updated: Just now</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.isArray(insights.predictions) && insights.predictions.map((insight, index) => (
          <InsightCard key={index} {...insight} />
        ))}
      </div>
    </div>
  );
}