import React from 'react';
import { Card, Tag, Space } from 'antd';
import { Brain, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';

interface Insight {
  type: 'positive' | 'negative' | 'warning' | 'suggestion';
  title: string;
  message: string;
  impact?: number;
}

interface AIInsightCardProps {
  insights: Insight[];
}

export const AIInsightCard: React.FC<AIInsightCardProps> = ({ insights = [] }) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'positive':
        return <TrendingUp className="h-5 w-5 text-green-500" />;
      case 'negative':
        return <TrendingDown className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      default:
        return <Brain className="h-5 w-5 text-blue-500" />;
    }
  };

  const getTagColor = (type: string) => {
    switch (type) {
      case 'positive':
        return 'success';
      case 'negative':
        return 'error';
      case 'warning':
        return 'warning';
      default:
        return 'processing';
    }
  };

  return (
    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
      {insights.map((insight, index) => (
        <Card key={index} size="small" className="w-full">
          <div className="flex items-start gap-3">
            {getIcon(insight.type)}
            <div className="flex-1">
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-base font-medium m-0">{insight.title}</h4>
                <Tag color={getTagColor(insight.type)}>{insight.type}</Tag>
              </div>
              <p className="text-gray-600 m-0">{insight.message}</p>
              {insight.impact && (
                <div className="mt-2">
                  <Tag color={insight.impact > 0 ? 'green' : 'red'}>
                    Impact: {insight.impact > 0 ? '+' : ''}{insight.impact}%
                  </Tag>
                </div>
              )}
            </div>
          </div>
        </Card>
      ))}
    </Space>
  );
}; 