import React, { Suspense } from "react";
import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout/Layout";
import ErrorBoundary from "./components/common/ErrorBoundary";
import LoadingSpinner from "./components/common/LoadingSpinner";
import { AuthProvider } from "./context/AuthContext";
import NotFound from "./pages/NotFound";
import PrivateRoute from "./components/common/PrivateRoute";
import "./tailwind.css";

// Lazy load components for better performance
const Dashboard = React.lazy(() => import("./components/Dashboard/Dashboard"));
const TransactionsPage = React.lazy(() => import("./pages/TransactionsPage"));
const InvestmentsPage = React.lazy(() => import("./pages/InvestmentsPage"));
const BudgetsPage = React.lazy(() => import("./pages/BudgetsPage"));
const SettingsPage = React.lazy(() => import("./pages/SettingsPage"));
const LoginPage = React.lazy(() => import("./pages/LoginPage"));
const RegisterPage = React.lazy(() => import("./pages/RegisterPage"));

const App = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected Routes */}
            <Route
              element={
                <PrivateRoute>
                  <Layout />
                </PrivateRoute>
              }
            >
              <Route path="/" element={<Dashboard />} />
              <Route path="/transactions" element={<TransactionsPage />} />
              <Route path="/investments" element={<InvestmentsPage />} />
              <Route path="/budgets" element={<BudgetsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Route>

            {/* 404 Page */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
