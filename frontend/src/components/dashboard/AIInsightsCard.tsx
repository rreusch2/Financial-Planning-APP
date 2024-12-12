import { cn } from '../../lib/utils';
import { AlertTriangle, Brain, Sparkles, TrendingUp } from 'lucide-react';

interface AIInsightCardProps {
  type: 'prediction' | 'alert' | 'tip' | 'analysis';
  title: string;
  content: string;
  confidence?: number;
  impact?: 'positive' | 'negative' | 'neutral';
}

const iconMap = {
  prediction: TrendingUp,
  alert: AlertTriangle,
  tip: Sparkles,
  analysis: Brain,
};

const impactColors = {
  positive: 'bg-green-50 border-green-200 text-green-700',
  negative: 'bg-red-50 border-red-200 text-red-700',
  neutral: 'bg-blue-50 border-blue-200 text-blue-700',
};

export function AIInsightCard({ type, title, content, confidence, impact = 'neutral' }: AIInsightCardProps) {
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