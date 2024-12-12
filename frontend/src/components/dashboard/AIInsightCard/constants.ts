import { Brain, Sparkles, TrendingUp, AlertTriangle } from 'lucide-react';
import { InsightType, InsightImpact } from './types';

export const iconMap = {
  prediction: TrendingUp,
  alert: AlertTriangle,
  tip: Sparkles,
  analysis: Brain,
};

export const impactColors: Record<InsightImpact, string> = {
  positive: 'bg-green-50 border-green-200 text-green-700',
  negative: 'bg-red-50 border-red-200 text-red-700',
  neutral: 'bg-blue-50 border-blue-200 text-blue-700',
};