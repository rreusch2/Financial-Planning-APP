import React, { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../utils/api";
import AccountSummary from "../AccountSummary/AccountSummary";
import AIAdvice from "../AIAdvice/AIAdvice";
import PlaidLinkButton from "../PlaidLink/PlaidLinkButton";
import { RefreshCw } from "lucide-react";

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState({
    totalIncome: 0,
    totalExpenses: 0,
    netBalance: 0,
  });
  const [syncStatus, setSyncStatus] = useState("idle");
  const [plaidConnected, setPlaidConnected] = useState(false);
  const navigate = useNavigate();

  const fetchDashboardData = useCallback(async () => {
    try {
      const data = await api.fetchAccountSummary();
      setDashboardData({
        totalIncome: data.total_income || 0,
        totalExpenses: data.total_expenses || 0,
        netBalance: data.net_balance || 0,
      });
      setPlaidConnected(!!data.has_plaid_connection);
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
    }
  }, []);

  useEffect(() => {
    const validateSession = async () => {
      try {
        const authResponse = await api.checkAuth();
        if (authResponse.authenticated) {
          fetchDashboardData();
        } else {
          navigate("/login");
        }
      } catch (error) {
        navigate("/login");
      }
    };

    validateSession();
  }, [navigate, fetchDashboardData]);

  const handleBankSync = async () => {
    if (!plaidConnected) return;

    setSyncStatus("syncing");
    try {
      await api.syncTransactions();
      await fetchDashboardData();
      setSyncStatus("success");
      setTimeout(() => setSyncStatus("idle"), 3000);
    } catch {
      setSyncStatus("error");
    }
  };

  const { totalIncome, totalExpenses, netBalance } = dashboardData;

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-gradient-to-r from-blue-600 to-blue-400 p-6 text-white">
        <h1 className="text-2xl font-semibold">Welcome, Reid!</h1>
        <p className="mt-1 text-lg">Take control of your financial future.</p>
      </header>

      <main className="max-w-6xl mx-auto p-4">
        {/* Bank Connection and Sync */}
        <div className="mb-6 flex items-center justify-between p-6 bg-white rounded-lg shadow-md">
          <div>
            <h3 className="text-lg font-medium">Bank Connection</h3>
            <p className="text-sm text-gray-500">
              {plaidConnected
                ? "Your bank account is connected."
                : "Connect your bank to start tracking your finances."}
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <PlaidLinkButton onSuccess={fetchDashboardData} />
            {plaidConnected && (
              <button
                onClick={handleBankSync}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <RefreshCw
                  className={`w-4 h-4 mr-2 ${
                    syncStatus === "syncing" ? "animate-spin" : ""
                  }`}
                />
                {syncStatus === "syncing" ? "Syncing..." : "Sync Now"}
              </button>
            )}
          </div>
        </div>

        {/* Account Summary and AI Insights */}
        <div className="grid gap-6 sm:grid-cols-2">
          <div className="p-6 bg-white rounded-lg shadow-md">
            <AccountSummary
              totalIncome={totalIncome}
              totalExpenses={totalExpenses}
              netBalance={netBalance}
            />
          </div>
          <div className="p-6 bg-white rounded-lg shadow-md">
            <AIAdvice />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
