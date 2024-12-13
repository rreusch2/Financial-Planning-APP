import React from 'react';
import { Target, TrendingUp, CheckCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface Goal {
  id: string;
  title: string;
  target: number;
  current: number;
  deadline: string;
  aiSuggestions: string[];
}

export function SmartGoalsTracker() {
  const goals: Goal[] = [
    {
      id: '1',
      title: 'Emergency Fund',
      target: 10000,
      current: 6500,
      deadline: '2024-06-30',
      aiSuggestions: [
        'Redirect streaming service savings',
        'Consider high-yield savings account'
      ]
    }
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">Smart Goals</h3>
          <p className="text-sm text-gray-500">AI-optimized financial targets</p>
        </div>
        <Target className="h-6 w-6 text-indigo-600" />
      </div>

      {goals.map(goal => (
        <motion.div
          key={goal.id}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          <div className="flex justify-between items-center">
            <h4 className="font-medium">{goal.title}</h4>
            <span className="text-sm text-gray-500">
              ${goal.current.toLocaleString()} / ${goal.target.toLocaleString()}
            </span>
          </div>

          <div className="relative pt-1">
            <div className="overflow-hidden h-2 text-xs flex rounded bg-indigo-100">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(goal.current / goal.target) * 100}%` }}
                className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-600"
              />
            </div>
          </div>

          <div className="bg-indigo-50 rounded-lg p-4">
            <h5 className="text-sm font-medium text-indigo-900 mb-2">
              AI Suggestions
            </h5>
            <ul className="space-y-2">
              {goal.aiSuggestions.map((suggestion, index) => (
                <li key={index} className="flex items-center text-sm text-indigo-700">
                  <CheckCircle className="h-4 w-4 mr-2" />
                  {suggestion}
                </li>
              ))}
            </ul>
          </div>
        </motion.div>
      ))}
    </div>
  );
}