import React from 'react';
import { Progress, Space } from 'antd';

interface CategoryBudget {
  category: string;
  spent: number;
  limit: number;
  color?: string;
}

interface BudgetProgressProps {
  categories: CategoryBudget[];
}

export const BudgetProgress: React.FC<BudgetProgressProps> = ({ categories = [] }) => {
  return (
    <Space direction="vertical" style={{ width: '100%' }} size="middle">
      {categories.map((cat) => {
        const percentage = (cat.spent / cat.limit) * 100;
        return (
          <div key={cat.category}>
            <div className="flex justify-between mb-1">
              <span>{cat.category}</span>
              <span>${cat.spent} / ${cat.limit}</span>
            </div>
            <Progress 
              percent={percentage} 
              status={percentage > 100 ? "exception" : "active"}
              strokeColor={cat.color}
            />
          </div>
        );
      })}
    </Space>
  );
}; 