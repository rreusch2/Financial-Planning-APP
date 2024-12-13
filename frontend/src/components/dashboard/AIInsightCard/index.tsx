import React from 'react';
import { Brain, Sparkles, TrendingUp, AlertTriangle } from 'lucide-react';
import { cn } from '../../../lib/utils';
import { InsightType, InsightImpact } from '../../dashboard/AIInsightCard/types';
import { iconMap, impactColors } from '../../dashboard/AIInsightCard/constants';

interface AIInsightCardProps {
  insights?: string;
  loading?: boolean;
}

function isValidJSON(str: string) {
  try {
    JSON.parse(str);
    return true;
  } catch (e) {
    // If it's not valid JSON, we'll treat it as a plain string
    return false;
  }
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

  // Try to parse as JSON, if not, display as plain text
  const content = isValidJSON(insights) 
    ? JSON.parse(insights)
    : [{ 
        type: 'analysis',
        title: 'AI Analysis',
        content: insights,
        impact: 'neutral'
      }];

  return (
    <div className="space-y-4">
      {Array.isArray(content) ? content.map((insight: any, index: number) => {
        const Icon = iconMap[insight.type as InsightType] || Brain;
        const impactColor = impactColors[insight.impact as InsightImpact] || 'border-gray-200';

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
      }) : (
        <div className="p-4 rounded-lg border transition-all hover:shadow-md">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-full bg-white/80">
              <Brain className="h-5 w-5" />
            </div>
            <h3 className="font-semibold">AI Analysis</h3>
          </div>
          <p className="text-sm">{content}</p>
        </div>
      )}
    </div>
  );
}

export default AIInsightCard;