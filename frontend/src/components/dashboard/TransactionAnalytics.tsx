import React from 'react';
import { Card, Typography, Table, Tag, Tooltip } from 'antd';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';

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
  const getCategoryData = () => {
    const categoryTotals = transactions.reduce((acc, transaction) => {
      const category = transaction.category || 'Uncategorized';
      acc[category] = (acc[category] || 0) + transaction.amount;
      return acc;
    }, {} as { [key: string]: number });

    return Object.entries(categoryTotals).map(([category, total]) => ({
      category,
      total
    }));
  };

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

  const config = getCategoryData();

  return (
    <div className="transaction-analytics">
      <Card className="spending-by-category">
        <Title level={3}>Spending by Category</Title>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={config}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" />
            <YAxis />
            <Tooltip />
            <Bar 
              dataKey="total" 
              fill="#1890ff"
              name="Total Spending"
            />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <Card className="transaction-list">
        <Title level={3}>Recent Transactions</Title>
        <Table 
          dataSource={transactions}
          columns={columns}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <style jsx>{`
        .transaction-analytics {
          display: grid;
          grid-template-rows: auto 1fr;
          gap: 20px;
          padding: 20px;
        }

        .spending-by-category {
          height: 400px;
        }

        .transaction-list {
          margin-top: 20px;
        }
      `}</style>
    </div>
  );
};

export default TransactionAnalytics; 