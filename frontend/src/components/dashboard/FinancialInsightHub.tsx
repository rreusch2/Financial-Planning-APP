import React from 'react';
import { Card, Typography, List, Divider, Progress, Tooltip } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';

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
  insights: Insight[];
  spendingPatterns: SpendingPattern;
}

const FinancialInsightHub: React.FC<Props> = ({ insights, spendingPatterns }) => {
  const renderTrendIndicator = (trend: number) => {
    if (trend > 0) {
      return <ArrowUpOutlined style={{ color: trend > 0.1 ? 'red' : 'orange' }} />;
    }
    return <ArrowDownOutlined style={{ color: 'green' }} />;
  };

  const renderSpendingTrends = () => {
    const monthlyData = Object.entries(spendingPatterns.monthly_analysis)
      .map(([month, data]) => ({
        month,
        amount: data.total
      }))
      .sort((a, b) => a.month.localeCompare(b.month));

    return (
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={monthlyData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Area 
            type="monotone" 
            dataKey="amount" 
            stroke="#1890ff"
            fill="#1890ff"
            fillOpacity={0.3}
          />
        </AreaChart>
      </ResponsiveContainer>
    );
  };

  const renderPredictions = () => {
    return (
      <div>
        <Title level={4}>Spending Predictions</Title>
        {spendingPatterns.predictions.map((prediction, index) => (
          <div key={index}>
            <Text>{prediction.month}: </Text>
            <Text strong>${prediction.amount.toFixed(2)}</Text>
            <Tooltip title="Prediction confidence">
              <Progress percent={prediction.confidence * 100} size="small" />
            </Tooltip>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="financial-insight-hub">
      <Card className="main-insights">
        <Title level={3}>Financial Insights</Title>
        {insights.map((insight, index) => (
          <div key={index} className="insight-section">
            <Title level={4}>{insight.message}</Title>
            <List
              dataSource={insight.details}
              renderItem={item => (
                <List.Item>
                  <Text>{item}</Text>
                </List.Item>
              )}
            />
            <Divider />
          </div>
        ))}
      </Card>

      <Card className="spending-patterns">
        <Title level={3}>Spending Analysis</Title>
        <div className="trend-overview">
          <Text>Overall Trend: </Text>
          {renderTrendIndicator(spendingPatterns.trend)}
          <Text> ({(spendingPatterns.trend * 100).toFixed(1)}%)</Text>
        </div>
        
        <div className="spending-chart">
          {renderSpendingTrends()}
        </div>

        <div className="category-analysis">
          <Title level={4}>Category Analysis</Title>
          {Object.entries(spendingPatterns.categories).map(([category, data]) => (
            <div key={category} className="category-item">
              <Text strong>{category}</Text>
              <Text>Average: ${data.average.toFixed(2)}</Text>
              <Tooltip title="Spending volatility">
                <Progress 
                  percent={data.volatility * 100} 
                  size="small"
                  status={data.volatility > 0.5 ? "exception" : "active"}
                />
              </Tooltip>
            </div>
          ))}
        </div>

        {spendingPatterns.predictions.length > 0 && renderPredictions()}
      </Card>

      <style jsx>{`
        .financial-insight-hub {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          padding: 20px;
        }

        .main-insights, .spending-patterns {
          height: 100%;
        }

        .insight-section {
          margin-bottom: 20px;
        }

        .trend-overview {
          margin-bottom: 20px;
        }

        .spending-chart {
          height: 300px;
          margin: 20px 0;
        }

        .category-item {
          margin: 10px 0;
        }

        @media (max-width: 768px) {
          .financial-insight-hub {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default FinancialInsightHub;