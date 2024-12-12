import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { cn } from '../../../lib/utils';
import { SpendingChart } from './SpendingChart';
import { PredictionCard } from './PredictionCard';
import { SpendingData } from './types';

interface SpendingInsightsProps {
  data: SpendingData[];
  predictedSpending: number;
  spendingTrend: number;
}

export function SpendingInsights({
  data,
  predictedSpending,
  spendingTrend
}: SpendingInsightsProps) {
  const trendIsUp = spendingTrend > 0;

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Spending Insights</h3>
          <p className="text-sm text-gray-500">AI-powered spending analysis and predictions</p>
        </div>
        <div className={cn(
          "flex items-center px-3 py-1 rounded-full text-sm",
          trendIsUp ? "bg-red-50 text-red-700" : "bg-green-50 text-green-700"
        )}>
          {trendIsUp ? <ArrowUpRight className="h-4 w-4 mr-1" /> : <ArrowDownRight className="h-4 w-4 mr-1" />}
          {Math.abs(spendingTrend)}% vs last month
        </div>
      </div>

      <SpendingChart data={data} />
      <PredictionCard predictedSpending={predictedSpending} />
    </div>
  );
}