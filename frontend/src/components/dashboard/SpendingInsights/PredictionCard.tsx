import React from 'react';

interface PredictionCardProps {
  predictedSpending: number;
}

export function PredictionCard({ predictedSpending }: PredictionCardProps) {
  return (
    <div className="mt-4 p-4 bg-indigo-50 rounded-lg">
      <h4 className="font-medium text-indigo-900">AI Prediction</h4>
      <p className="text-sm text-indigo-700">
        Based on your spending patterns, you're projected to spend ${predictedSpending.toFixed(2)} next month.
      </p>
    </div>
  );
}