import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import AppRoutes from './routes';
import BudgetPage from './pages/Budget';

const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/app/budget" element={<BudgetPage />} />
          <Route path="/*" element={<AppRoutes />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
};

export default App;