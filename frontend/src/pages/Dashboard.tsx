import { CreditCard, PiggyBank, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import { AIInsights } from '../components/dashboard/AIInsights';
import { StatCard } from '../components/dashboard/StatCard';
import { ConnectBankCard } from '../components/onboarding/ConnectBankCard';
import { useAuth } from '../contexts/AuthContext';
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
      await refreshUser(); // Added parentheses to call the function
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
        <AIInsights insights={data?.ai_insights} loading={loading} />
      </div>
    </div>
  );
}