import React from 'react';
import { Card, Typography, List, Divider, Progress, Tooltip } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip as RechartsTooltip } from 'recharts';

const { Title, Text } = Typography;

interface Insight {
  type: string;
  message: string;
  details: string[];
}

interface SpendingPattern {
  trend: number;
  categories: {
    [key: string]: {
      average: number;
      std_dev: number;
      volatility: number;
    };
  };
  predictions: {
    month: string;
    amount: number;
    confidence: number;
  }[];
  monthly_analysis: {
    [key: string]: {
      total: number;
      categories: {
        [key: string]: number;
      };
    };
  };
  spending_velocity: number;
}

interface Props {
  insights: any[];
  spendingPatterns: {
    trend: number;
    categories: Record<string, {
      average: number;
      std_dev: number;
      volatility: number;
    }>;
    monthly_analysis: Record<string, {
      total: number;
      categories: Record<string, number>;
    }>;
  };
}

const FinancialInsightHub: React.FC<Props> = ({ insights = [], spendingPatterns = { trend: 0, categories: {}, monthly_analysis: {} } }) => {
  const monthlyData = React.useMemo(() => {
    if (!spendingPatterns?.monthly_analysis) return [];
    
    return Object.entries(spendingPatterns.monthly_analysis)
      .map(([month, data]) => ({
        month,
        amount: data?.total || 0
      }))
      .sort((a, b) => a.month.localeCompare(b.month));
  }, [spendingPatterns?.monthly_analysis]);

  const categoryData = React.useMemo(() => {
    if (!spendingPatterns?.categories) return [];
    
    return Object.entries(spendingPatterns.categories)
      .map(([category, data]) => ({
        category,
        average: data?.average || 0,
        volatility: data?.volatility || 0
      }));
  }, [spendingPatterns?.categories]);

  return (
    <div className="grid grid-cols-2 gap-6">
      <Card className="shadow-sm">
        <Title level={4}>Financial Insights</Title>
        
        {/* Financial Summary */}
        <div className="mb-6">
          <Title level={5}>Financial Summary</Title>
          {insights?.find(i => i.type === 'summary')?.details?.map((detail: string, index: number) => (
            <Text key={index} className="block text-gray-600">{detail}</Text>
          ))}
        </div>

        {/* Top Spending Categories */}
        <div className="mb-6">
          <Title level={5}>Top Spending Categories:</Title>
          {insights?.find(i => i.type === 'categories')?.details?.map((detail: string, index: number) => (
            <Text key={index} className="block text-gray-600">{detail}</Text>
          ))}
        </div>

        {/* Recent Large Transactions */}
        <div className="mb-6">
          <Title level={5}>Recent Large Transactions:</Title>
          {insights?.find(i => i.type === 'large_transactions')?.details?.map((detail: string, index: number) => (
            <Text key={index} className="block text-gray-600">{detail}</Text>
          ))}
        </div>

        {/* Financial Recommendations */}
        <div>
          <Title level={5}>Financial Recommendations:</Title>
          {insights?.find(i => i.type === 'recommendations')?.details?.map((detail: string, index: number) => (
            <Text key={index} className="block text-gray-600">{detail}</Text>
          ))}
        </div>
      </Card>

      <Card className="shadow-sm">
        <Title level={4}>Spending Analysis</Title>
        <div className="mb-4">
          <Text>Overall Trend: </Text>
          {(spendingPatterns?.trend || 0) > 0 ? (
            <Text type="danger">
              <ArrowUpOutlined /> {((spendingPatterns?.trend || 0) * 100).toFixed(1)}%
            </Text>
          ) : (
            <Text type="success">
              <ArrowDownOutlined /> {((spendingPatterns?.trend || 0) * 100).toFixed(1)}%
            </Text>
          )}
        </div>

        {/* Spending Chart */}
        <div className="h-64 mb-6">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <RechartsTooltip />
              <Area 
                type="monotone" 
                dataKey="amount" 
                stroke="#1890ff"
                fill="#1890ff"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Category Analysis */}
        <div>
          <Title level={5}>Category Analysis</Title>
          {categoryData.map(({ category, average, volatility }) => (
            <div key={category} className="mb-4">
              <div className="flex justify-between mb-1">
                <Text>{category}</Text>
                <Text>${average.toFixed(2)}</Text>
              </div>
              <Progress 
                percent={Math.min(volatility * 100, 100)} 
                size="small"
                status={volatility > 0.5 ? "exception" : "active"}
                showInfo={false}
              />
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default FinancialInsightHub;