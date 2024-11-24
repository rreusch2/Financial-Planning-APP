// src/components/Dashboard/Dashboard.js

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  LineChart,
  PieChart,
  Settings,
  CreditCard,
  RefreshCw
} from 'lucide-react';
import ErrorBoundary from '../common/ErrorBoundary';
import LoadingSpinner from '../common/LoadingSpinner';
import AccountSummary from '../AccountSummary/AccountSummary';
import Transactions from '../Transactions/Transactions';
import ExpenseAnalysis from '../ExpenseAnalysis/ExpenseAnalysis';
import AIAdvice from '../AIAdvice/AIAdvice';
import IncomeSources from '../IncomeSources/IncomeSources';
import PlaidLinkButton from '../PlaidLinkButton/PlaidLinkButton';

function Dashboard() {
  // State variables
  const [totalIncome, setTotalIncome] = useState(0);
  const [totalExpenses, setTotalExpenses] = useState(0);
  const [netBalance, setNetBalance] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastSynced, setLastSynced] = useState(null);
  const [syncError, setSyncError] = useState(null); // Added syncError state

  const navigate = useNavigate();

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/dashboard', {
        credentials: 'include',
      });
      const data = await response.json();
      console.log('Dashboard Data:', data); // Log the API response here
  
      if (data.error) {
        console.error('Error fetching dashboard data:', data.error);
        setError(data.error);
      } else {
        setTotalIncome(data.total_income || 0);
        setTotalExpenses(data.total_expenses || 0);
        setNetBalance(data.net_balance || 0);
        setTransactions(data.transactions || []);
        setError(null);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to fetch dashboard data.');
    }
  };
  

  const handleBankSync = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/sync-bank', {
        method: 'POST', // Correct HTTP method
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies
      });
  
      if (!response.ok) {
        throw new Error('Failed to sync bank data');
      }
  
      await fetchDashboardData(); // Refresh dashboard data after syncing
      setLastSynced(new Date());
      setSyncError(null); // Clear any previous sync errors
    } catch (err) {
      setSyncError(err.message); // Set the sync-specific error
    } finally {
      setLoading(false);
    }
  };
  
  // Conditional Rendering
  if (loading) return <LoadingSpinner />;

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div>
          <p className="text-red-500">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <nav className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold text-blue-600">FinanceTracker</span>
            </div>

            <div className="hidden md:flex space-x-4">
              <button
                onClick={() => navigate('/')}
                className="flex items-center px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100"
              >
                <LayoutDashboard className="w-5 h-5 mr-2" />
                Dashboard
              </button>
              <button
                onClick={() => navigate('/investments')}
                className="flex items-center px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100"
              >
                <LineChart className="w-5 h-5 mr-2" />
                Investments
              </button>
              <button
                onClick={() => navigate('/budgets')}
                className="flex items-center px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100"
              >
                <PieChart className="w-5 h-5 mr-2" />
                Budgets
              </button>
              <button
                onClick={() => navigate('/credit-score')}
                className="flex items-center px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100"
              >
                <CreditCard className="w-5 h-5 mr-2" />
                Credit Score
              </button>
              <button
                onClick={() => navigate('/settings')}
                className="flex items-center px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100"
              >
                <Settings className="w-5 h-5 mr-2" />
                Settings
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <ErrorBoundary>
          <div className="grid gap-6 md:grid-cols-2">
            <AccountSummary
              totalIncome={totalIncome}
              totalExpenses={totalExpenses}
              netBalance={netBalance}
            />
            <IncomeSources totalIncome={totalIncome} />
          </div>

          <div className="mt-6">
            <Transactions transactions={transactions} />
          </div>

          <div className="grid gap-6 md:grid-cols-2 mt-6">
            <ExpenseAnalysis />
            <AIAdvice />
          </div>

          {/* Bank Connection Status */}
          <div className="mt-6 p-4 bg-white rounded-lg shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">Bank Connection</h3>
                <p className="text-sm text-gray-600">
                  Last synced: {lastSynced ? lastSynced.toLocaleString() : 'Never'}
                </p>
                {syncError && <p className="text-sm text-red-500 mt-1">{syncError}</p>} {/* Updated to syncError */}
              </div>
              <div className="flex items-center space-x-4">
                <PlaidLinkButton
                  onSuccess={() => {
                    fetchDashboardData();
                    setLastSynced(new Date());
                  }}
                />
                <button
                  onClick={handleBankSync}
                  disabled={loading}
                  className={`px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 
                    flex items-center ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Syncing...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Sync Now
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </ErrorBoundary>
      </div>
    </div>
  );
}

export default Dashboard;
