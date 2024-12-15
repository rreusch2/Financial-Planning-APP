import React, { useEffect, useState } from 'react';
import { Spin, Alert } from 'antd';
import FinancialInsightHub from '../components/dashboard/FinancialInsightHub';
import TransactionAnalytics from '../components/dashboard/TransactionAnalytics';
import { useAuth } from '../contexts/AuthContext';
import { fetchDashboardData } from '../api/dashboard';
import { Navigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const { user, loading: authLoading } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dashboardData, setDashboardData] = useState<any>(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      if (!user) return;
      
      try {
        setLoading(true);
        setError(null);
        const data = await fetchDashboardData();
        setDashboardData(data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load dashboard data';
        setError(errorMessage);
        console.error('Dashboard error:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [user]);

  if (authLoading) {
    return <Spin size="large" />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <Alert message={error} type="error" />
      </div>
    );
  }

  return (
    <div className="grid gap-6">
      {dashboardData && (
        <>
          <FinancialInsightHub 
            insights={dashboardData.insights?.predictions || []}
            spendingPatterns={dashboardData.spending_patterns || {}}
          />
          <TransactionAnalytics 
            transactions={dashboardData.recent_transactions || []}
          />
        </>
      )}
    </div>
  );
};

export default Dashboard;