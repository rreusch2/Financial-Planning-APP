import React from 'react';
import { Card, Typography, Table, Tag } from 'antd';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from 'recharts';

const { Title, Text } = Typography;

interface Transaction {
  id: string;
  date: string;
  name: string;
  amount: number;
  category: string;
  merchant_name: string;
  pending: boolean;
}

interface Props {
  transactions: Transaction[];
}

const TransactionAnalytics: React.FC<Props> = ({ transactions }) => {
  const columns = [
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      sorter: (a: Transaction, b: Transaction) => 
        new Date(a.date).getTime() - new Date(b.date).getTime()
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Amount',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount: number) => (
        <Text type={amount > 0 ? 'danger' : 'success'}>
          ${Math.abs(amount).toFixed(2)}
        </Text>
      ),
      sorter: (a: Transaction, b: Transaction) => a.amount - b.amount
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      render: (category: string) => (
        <Tag color="blue">{category || 'Uncategorized'}</Tag>
      )
    },
    {
      title: 'Status',
      key: 'status',
      render: (record: Transaction) => (
        <Tag color={record.pending ? 'orange' : 'green'}>
          {record.pending ? 'Pending' : 'Completed'}
        </Tag>
      )
    }
  ];

  const categoryData = Object.entries(
    transactions.reduce((acc, t) => {
      const category = t.category || 'Uncategorized';
      acc[category] = (acc[category] || 0) + (t.amount > 0 ? t.amount : 0);
      return acc;
    }, {} as Record<string, number>)
  ).map(([category, total]) => ({ category, total }));

  return (
    <div className="mt-6 space-y-6">
      <Card className="shadow-sm">
        <Title level={4}>Category Breakdown</Title>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={categoryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="total" fill="#1890ff" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card className="shadow-sm">
        <Title level={4}>Recent Transactions</Title>
        <Table 
          dataSource={transactions}
          columns={columns}
          rowKey="id"
          pagination={{ pageSize: 10 }}
          className="mt-4"
        />
      </Card>
    </div>
  );
};

export default TransactionAnalytics; 