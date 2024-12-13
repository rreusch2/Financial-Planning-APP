import React, { useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useDashboardData } from '../hooks/useDashboardData';
import { ConnectBankCard } from '../components/onboarding/ConnectBankCard';
import { DashboardHeader } from '../components/dashboard/DashboardHeader';
import { FinancialInsightHub } from '../components/dashboard/FinancialInsightHub';
import { SmartGoalsTracker } from '../components/dashboard/SmartGoalsTracker';
import { FinancialAssistant } from '../components/dashboard/FinancialAssistant';
import { TransactionAnalytics } from '../components/dashboard/TransactionAnalytics';
import { motion, AnimatePresence } from 'framer-motion';

interface DashboardData {
  lastUpdated?: string;
  insights?: {
    predictions: Array<{
      title: string;
      content: string;
      confidence: number;
      type: 'prediction' | 'alert' | 'opportunity';
    }>;
    analysis: string;
  };
  goals?: Array<{
    id: string;
    title: string;
    target: number;
    current: number;
    deadline: string;
    aiSuggestions: string[];
  }>;
  recent_transactions?: Array<{
    id: string;
    date: string;
    name: string;
    amount: number;
    category: string;
  }>;
  spending_patterns?: {
    trend: number;
    categories: Record<string, number>;
    predictions: Array<{ date: string; amount: number }>;
  };
  ai_insights?: {
    analysis: string;
    recommendations: string[];
    alerts: string[];
  };
}

export default function Dashboard() {
  const { user, refreshUser } = useAuth();
  const { data, loading, error, refetch } = useDashboardData();

  const handlePlaidSuccess = async () => {
    try {
      await refreshUser();
      await refetch();
    } catch (err) {
      console.error('Error after Plaid success:', err);
    }
  };

  useEffect(() => {
    if (user?.has_plaid_connection) {
      refetch();
    }
  }, [user?.has_plaid_connection]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  if (!user?.has_plaid_connection) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <ConnectBankCard onSuccess={handlePlaidSuccess} />
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center py-8"
      >
        <div className="text-red-600 mb-4">{error}</div>
        <button
          onClick={refetch}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          Try again
        </button>
      </motion.div>
    );
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
      >
        <div className="space-y-8">
          {/* Header Section */}
          <DashboardHeader lastUpdated={data?.lastUpdated} onRefresh={refetch} />

          {/* AI Insights Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <FinancialInsightHub insights={data?.insights} />
          </motion.div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
              className="space-y-8"
            >
              <SmartGoalsTracker goals={data?.goals} />
              <TransactionAnalytics
                transactions={data?.recent_transactions}
                patterns={data?.spending_patterns}
              />
            </motion.div>

            {/* Right Column */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 }}
            >
              <FinancialAssistant
                recentInsights={data?.ai_insights}
                transactionHistory={data?.recent_transactions}
              />
            </motion.div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}