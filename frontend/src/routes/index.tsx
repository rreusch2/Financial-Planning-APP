import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import Login from '../pages/Login';
import Register from '../pages/Register';
import Layout from '../components/Layout';
import Analytics from '../pages/Analytics';
import Goals from '../pages/Goals';
import AIAdvisor from '../pages/AIAdvisor';
import Settings from '../pages/Settings';
import PrivateRoute from '../components/PrivateRoute';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      {/* Protected Routes */}
      <Route path="/app" element={<PrivateRoute><Layout /></PrivateRoute>}>
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="goals" element={<Goals />} />
        <Route path="advisor" element={<AIAdvisor />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      {/* Redirect root to app/dashboard */}
      <Route path="/" element={<Navigate to="/app/dashboard" replace />} />
      
      {/* Catch all route */}
      <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
    </Routes>
  );
};

export default AppRoutes; 