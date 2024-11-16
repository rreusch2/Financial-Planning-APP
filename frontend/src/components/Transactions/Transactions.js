// src/components/Transactions/Transactions.js
import React from 'react';
import { useNavigate } from 'react-router-dom';

const Transactions = ({ transactions }) => {
  const navigate = useNavigate();

  // Display only the first 8 transactions
  const recentTransactions = transactions.slice(0, 8);

  if (!transactions || transactions.length === 0) {
    return <div className="p-4">No transactions available.</div>;
  }

  const handleViewMore = () => {
    navigate('/transactions'); // Navigate to full transactions page
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Recent Transactions</h2>
      </div>

      <div className="overflow-hidden">
        <div className="bg-white rounded-lg border">
          {recentTransactions.map((transaction, index) => (
            <div
              key={transaction.id}
              className={`flex items-center justify-between p-4 ${
                index !== recentTransactions.length - 1 ? 'border-b' : ''
              }`}
            >
              <div className="flex items-center space-x-4">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    transaction.amount < 0 ? 'bg-red-100' : 'bg-green-100'
                  }`}
                >
                  <span
                    className={`text-lg ${
                      transaction.amount < 0 ? 'text-red-600' : 'text-green-600'
                    }`}
                  >
                    {transaction.amount < 0 ? '-' : '+'}
                  </span>
                </div>
                <div>
                  <p className="font-semibold">{transaction.name}</p>
                  <p className="text-sm text-gray-500">{transaction.date}</p>
                </div>
              </div>
              <div>
                <p
                  className={`font-semibold ${
                    transaction.amount < 0 ? 'text-red-600' : 'text-green-600'
                  }`}
                >
                  ${Math.abs(transaction.amount).toFixed(2)}
                </p>
                <p className="text-sm text-gray-500">{transaction.category}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4 text-center">
        <button
          onClick={handleViewMore}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          View All Transactions
        </button>
      </div>
    </div>
  );
};

export default Transactions;
