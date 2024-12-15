import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface SpendingTrendsProps {
  data: Array<{
    date: string;
    amount: number;
  }>;
}

export const SpendingTrends: React.FC<SpendingTrendsProps> = ({ data = [] }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Area 
          type="monotone" 
          dataKey="amount" 
          stroke="#8884d8" 
          fill="#8884d8" 
          fillOpacity={0.3} 
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}; 