export type InsightType = 'prediction' | 'alert' | 'tip' | 'analysis';
export type InsightImpact = 'positive' | 'negative' | 'neutral';

export interface InsightData {
  analysis: string;
  spending_data: Record<string, number>;
  predictions: {
    next_month_prediction: number;
    confidence: number;
    trend: string;
  };
  anomalies: any[];
}

export interface DashboardData {
  insights: InsightData;
  categories: Record<string, number>;
  predictions: {
    next_month_prediction: number;
    confidence: number;
    trend: string;
  };
}

export interface AIInsightCardProps {
  insights?: string;
  loading?: boolean;
}