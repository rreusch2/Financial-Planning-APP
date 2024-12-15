import React from 'react';
import { Route, Routes } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import Transactions from '../pages/Transactions';
import Analytics from '../pages/Analytics';
import Goals from '../pages/Goals';
import AIAdvisor from '../pages/AIAdvisor';
import Settings from '../pages/Settings';
import Layout from '../components/Layout';

const AppRoutes: React.FC = () => {
  return (
    <Layout>
      <Routes>
        <Route path="/app/dashboard" element={<Dashboard />} />
        <Route path="/app/transactions" element={<Transactions />} />
        <Route path="/app/analytics" element={<Analytics />} />
        <Route path="/app/goals" element={<Goals />} />
        <Route path="/app/advisor" element={<AIAdvisor />} />
        <Route path="/app/settings" element={<Settings />} />
        <Route path="*" element={<Dashboard />} />
      </Routes>
    </Layout>
  );
};

export default AppRoutes; 