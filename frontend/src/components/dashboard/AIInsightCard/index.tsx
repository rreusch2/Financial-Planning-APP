import React from 'react';
import { Brain, Sparkles, TrendingUp, AlertTriangle } from 'lucide-react';
import { cn } from '../../../lib/utils';
import { InsightType, InsightImpact } from './types';
import { iconMap, impactColors } from './constants';

interface AIInsightCardProps {
  type: InsightType;
  title: string;
  content: string;
  confidence?: number;
  impact?: InsightImpact;
}

export function AIInsightCard({
  type,
  title,
  content,
  confidence,
  impact = 'neutral'
}: AIInsightCardProps) {
  const Icon = iconMap[type];

  return (
    <div className={cn(
      "p-4 rounded-lg border transition-all hover:shadow-md",
      impactColors[impact]
    )}>
      <div className="flex items-center gap-3 mb-2">
        <div className="p-2 rounded-full bg-white/80">
          <Icon className="h-5 w-5" />
        </div>
        <h3 className="font-semibold">{title}</h3>
        {confidence && (
          <span className="text-sm opacity-75">
            {confidence}% confidence
          </span>
        )}
      </div>
      <p className="text-sm">{content}</p>
    </div>
  );
}