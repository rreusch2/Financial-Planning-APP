import React from 'react';
import { Brain, Sparkles, TrendingUp, AlertTriangle } from 'lucide-react';
import { cn } from '../../lib/utils';
import { InsightType, InsightImpact } from '../dashboard/AIInsightCard/types';
import { iconMap, impactColors } from '../dashboard/AIInsightCard/constants';

interface AIInsightCardProps {
  insights?: string;
  loading?: boolean;
}

function isValidJSON(str: string) {
  try {
    JSON.parse(str);
  } catch (e) {
    return false;
  }
  return true;
}

export function AIInsightCard({
  insights,
  loading,
}: AIInsightCardProps) {
  if (loading) {
    return <div>Loading...</div>;
  }

  if (!insights) {
    return <div>No insights available</div>;
  }

  if (!isValidJSON(insights)) {
    return <div>Invalid insights data</div>;
  }

  const parsedInsights = JSON.parse(insights);

  return (
    <div className="space-y-4">
      {parsedInsights.map((insight: any, index: number) => {
        const Icon = iconMap[insight.type as InsightType];
        const impactColor = impactColors[insight.impact as InsightImpact];

        return (
          <div
            key={index}
            className={cn(
              "p-4 rounded-lg border transition-all hover:shadow-md",
              impactColor
            )}
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-full bg-white/80">
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="font-semibold">{insight.title}</h3>
              {insight.confidence && (
                <span className="text-sm opacity-75">
                  {insight.confidence}% confidence
                </span>
              )}
            </div>
            <p className="text-sm">{insight.content}</p>
          </div>
        );
      })}
    </div>
  );
}

export default AIInsightCard;