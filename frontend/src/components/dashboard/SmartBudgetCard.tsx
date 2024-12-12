import React from 'react';
import { PiggyBank, Sparkles } from 'lucide-react';
import { cn } from '../../lib/utils'; // Ensure this import is present

interface SmartBudgetCardProps {
  category: string;
  spent: number;
  budget: number;
  aiSuggestion?: number;
}

export function SmartBudgetCard({ category, spent, budget, aiSuggestion }: SmartBudgetCardProps) {
  const percentSpent = (spent / budget) * 100;
  const isOverBudget = spent > budget;

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm">
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-medium text-gray-900">{category}</h3>
        <PiggyBank className={cn(
          "h-5 w-5",
          isOverBudget ? "text-red-500" : "text-green-500"
        )} />
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Spent</span>
          <span className="font-medium">${spent.toFixed(2)}</span>
        </div>

        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Budget</span>
          <span className="font-medium">${budget.toFixed(2)}</span>
        </div>

        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={cn(
              "h-full transition-all",
              percentSpent > 100 ? "bg-red-500" : "bg-green-500"
            )}
            style={{ width: `${Math.min(percentSpent, 100)}%` }}
          />
        </div>

        {aiSuggestion && (
          <div className="flex items-center gap-2 mt-3 p-2 bg-indigo-50 rounded text-sm">
            <Sparkles className="h-4 w-4 text-indigo-600" />
            <span className="text-indigo-700">
              AI suggests: ${aiSuggestion.toFixed(2)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}