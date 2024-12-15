import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Progress, Timeline, Alert, Button, Tooltip, Spin } from 'antd';
import { TrendingUp, TrendingDown, Brain, Target, AlertTriangle, RefreshCw } from 'lucide-react';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip as RechartsTooltip } from 'recharts';
import { Navigate } from 'react-router-dom';
import { DashboardHeader } from '../components/dashboard/DashboardHeader';
import { AIInsightCard } from '../components/dashboard/AIInsightCard';
import { SpendingTrends } from '../components/dashboard/SpendingTrends';
import { BudgetProgress } from '../components/dashboard/BudgetProgress';
import { ConnectBankCard } from '../components/onboarding/ConnectBankCard';
import { useAuth } from '../contexts/AuthContext';
import { fetchDashboardData, generateAIInsights } from '../api/dashboard';
import { getHealthScoreStatus } from '../utils/dashboard';

const Dashboard: React.FC = () => {
  const { user, loading: authLoading } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [lastUpdated, setLastUpdated] = useState<string>(new Date().toISOString());

  const loadDashboardData = async () => {
    if (!user || !user.has_plaid_connection) return;
    
    try {
      setLoading(true);
      setError(null);
      const data = await fetchDashboardData();
      setDashboardData(data);
      setLastUpdated(new Date().toISOString());
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load dashboard data';
      setError(errorMessage);
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [user]);

  if (authLoading) {
    return <Spin size="large" />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!user.has_plaid_connection) {
    return <ConnectBankCard onSuccess={() => window.location.reload()} />;
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
    <div className="p-6">
      <div className="space-y-6">
        <DashboardHeader 
          lastUpdated={lastUpdated}
          onRefresh={loadDashboardData}
        />

        {/* Financial Health Score */}
        <Row gutter={16}>
          <Col span={8}>
            <Card className="shadow-sm">
              <Statistic
                title="Financial Health Score"
                value={dashboardData?.health_score || 0}
                suffix="/100"
                prefix={<Brain className="h-5 w-5 text-indigo-600" />}
              />
              <Progress 
                percent={dashboardData?.health_score || 0} 
                status={getHealthScoreStatus(dashboardData?.health_score)}
                className="mt-4"
              />
            </Card>
          </Col>

          {/* Monthly Overview */}
          <Col span={8}>
            <Card className="shadow-sm">
              <Statistic
                title="Monthly Net Flow"
                value={dashboardData?.monthly_net || 0}
                precision={2}
                prefix="$"
                valueStyle={{ color: dashboardData?.monthly_net > 0 ? '#3f8600' : '#cf1322' }}
              />
              <div className="flex items-center mt-4">
                <TrendingUp className="h-5 w-5 text-green-500 mr-2" />
                <span>Income: ${dashboardData?.monthly_income || 0}</span>
              </div>
              <div className="flex items-center mt-2">
                <TrendingDown className="h-5 w-5 text-red-500 mr-2" />
                <span>Expenses: ${dashboardData?.monthly_expenses || 0}</span>
              </div>
            </Card>
          </Col>

          {/* Savings Goals */}
          <Col span={8}>
            <Card className="shadow-sm">
              <Statistic
                title="Progress to Savings Goal"
                value={dashboardData?.savings_progress || 0}
                suffix="%"
                prefix={<Target className="h-5 w-5 text-indigo-600" />}
              />
              <Progress 
                percent={dashboardData?.savings_progress || 0}
                status="active"
                className="mt-4"
              />
            </Card>
          </Col>
        </Row>

        {/* AI Insights and Recommendations */}
        <Row gutter={16}>
          <Col span={16}>
            <Card 
              title="AI Financial Insights" 
              extra={
                <Tooltip title="Generate new insights">
                  <Button 
                    icon={<RefreshCw className="h-4 w-4" />}
                    onClick={() => generateAIInsights()}
                  />
                </Tooltip>
              }
              className="shadow-sm"
            >
              <AIInsightCard insights={dashboardData?.ai_insights} />
            </Card>
          </Col>
          <Col span={8}>
            <Card title="Smart Alerts" className="shadow-sm">
              <Timeline
                items={dashboardData?.alerts?.map(alert => ({
                  color: alert.severity === 'high' ? 'red' : 'blue',
                  dot: <AlertTriangle className="h-4 w-4" />,
                  children: alert.message
                }))}
              />
            </Card>
          </Col>
        </Row>

        {/* Spending Analysis */}
        <Row gutter={16}>
          <Col span={12}>
            <Card title="Spending Trends" className="shadow-sm">
              <SpendingTrends data={dashboardData?.spending_trends} />
            </Card>
          </Col>
          <Col span={12}>
            <Card title="Budget Progress" className="shadow-sm">
              <BudgetProgress categories={dashboardData?.budget_progress} />
            </Card>
          </Col>
        </Row>

        {/* Transaction Analysis */}
        <Row gutter={16}>
          <Col span={24}>
            <Card title="Smart Transaction Analysis" className="shadow-sm">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h4 className="text-lg font-semibold mb-4">Category Distribution</h4>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={dashboardData?.category_distribution}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="category" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="amount" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-4">Spending Over Time</h4>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={dashboardData?.spending_over_time}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Area type="monotone" dataKey="amount" stroke="#8884d8" fill="#8884d8" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default Dashboard;