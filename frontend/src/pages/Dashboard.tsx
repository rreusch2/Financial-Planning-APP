import React, { useState, useEffect } from 'react';
import { PiggyBank, TrendingUp, CreditCard } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { StatCard, AIInsightCard, SpendingInsights, SmartBudgetCard } from '../components/dashboard';
import { ConnectBankCard } from '../components/onboarding/ConnectBankCard';
import { plaidApi } from '../lib/plaid';

interface DashboardData {
  total_income: number;
  total_expenses: number;
  net_balance: number;
  recent_transactions: Array<{
    id: string;
    date: string;
    name: string;
    amount: number;
    category?: string;
    merchant_name?: string;
  }>;
  ai_insights: string | null;
}

export default function Dashboard() {
  const { user, refreshUser } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await plaidApi.getDashboardData();
      setData(response);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    console.log('User object:', user);
    if (user?.has_plaid_connection) {
      fetchDashboardData();
    } else {
      setLoading(false);
    }
  }, [user]);

  const handlePlaidSuccess = async () => {
    try {
      await refreshUser();
      await fetchDashboardData();
    } catch (err) {
      console.error('Error after Plaid success:', err);
      setError('Failed to sync transactions');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!user?.has_plaid_connection) {
    return <ConnectBankCard onSuccess={handlePlaidSuccess} />;
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-600 mb-4">{error}</div>
        <button
          onClick={fetchDashboardData}
          className="text-indigo-600 hover:text-indigo-500 font-medium"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="Total Income"
          value={data?.total_income ?? 0}
          icon={TrendingUp}
          type="income"
        />
        <StatCard
          title="Total Expenses"
          value={data?.total_expenses ?? 0}
          icon={PiggyBank}
          type="expense"
        />
        <StatCard
          title="Net Balance"
          value={data?.net_balance ?? 0}
          icon={CreditCard}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AIInsightCard
          type="prediction"
          title="Spending Forecast"
          content="Based on your patterns, you might exceed your dining budget next week."
          confidence={85}
          impact="negative"
        />
        <AIInsightCard
          type="tip"
          title="Savings Opportunity"
          content="Switching your streaming subscriptions to annual plans could save you $84/year."
          impact="positive"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <SpendingInsights
            data={data?.spending_history ?? []}
            predictedSpending={data?.predicted_spending ?? 0}
            spendingTrend={data?.spending_trend ?? 0}
          />
        </div>
        <div className="space-y-4">
          <SmartBudgetCard
            category="Dining"
            spent={450}
            budget={500}
            aiSuggestion={475}
          />
          <SmartBudgetCard
            category="Shopping"
            spent={850}
            budget={700}
            aiSuggestion={650}
          />
        </div>
      </div>
    </div>
  );
}