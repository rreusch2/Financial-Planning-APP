import { useState, useEffect } from 'react';
import { plaidApi } from '../lib/plaid';

interface DashboardData {
  insights: {
    predictions: Array<{
      title: string;
      content: string;
      confidence: number;
      type: 'prediction' | 'alert' | 'opportunity';
    }>;
    analysis: string;
  };
  recent_transactions: Array<{
    id: string;
    date: string;
    name: string;
    amount: number;
    category: string;
  }>;
  spending_patterns: {
    trend: number;
    categories: Record<string, number>;
    predictions: Array<{ date: string; amount: number }>;
  };
}

export function useDashboardData() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await plaidApi.getDashboardData();
      setData(response);
      setError(null);
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard data error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return {
    data,
    loading,
    error,
    refetch: fetchData
  };
} 