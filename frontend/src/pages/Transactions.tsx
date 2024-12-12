import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import {
  Search,
  Calendar,
  ArrowUpDown,
  AlertCircle,
  Loader2,
  Brain
} from 'lucide-react';
import { transactions, aiServices } from '../lib/api';
import { cn } from '../lib/utils';


interface Transaction {
  id: number;
  date: string;
  name: string;
  amount: number;
  category: string;
  merchant_name: string;
  ai_category?: string;
  ai_insights?: string;
  sentiment?: string;
}

export default function Transactions() {
  const [loading, setLoading] = useState(true);
  const [transactionList, setTransactionList] = useState<Transaction[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    fetchTransactions();
  }, [page, sortOrder]);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const response = await transactions.getAll({
        page,
        per_page: 10,
      });
      setTransactionList(response.data.transactions);
      setTotalPages(response.data.total_pages);
    } catch (error) {
      console.error('Error fetching transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAIInsights = async (transaction: Transaction) => {
    try {
      setAiLoading(true);
      setSelectedTransaction(transaction);
      const response = await aiServices.getTransactionInsights(transaction.id.toString());

      const updatedTransactions = transactionList.map(t =>
        t.id === transaction.id
          ? { ...t, ai_insights: response.data.insights }
          : t
      );
      setTransactionList(updatedTransactions);
    } catch (error) {
      console.error('Error getting AI insights:', error);
    } finally {
      setAiLoading(false);
    }
  };

  const filteredTransactions = transactionList
    .filter(transaction =>
      transaction.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      transaction.merchant_name?.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .filter(transaction =>
      selectedCategory === 'all' || transaction.category === selectedCategory
    );

  const categories = Array.from(
    new Set(transactionList.map(t => t.category))
  ).filter(Boolean);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Transactions</h1>
        <button
          onClick={() => transactions.sync()}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
        >
          Sync Transactions
        </button>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="p-6 space-y-4">
          {/* Filters */}
          <div className="flex gap-4 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search transactions..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>
            </div>

            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="all">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>

            <button
              onClick={() => setSortOrder(current => current === 'asc' ? 'desc' : 'asc')}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <ArrowUpDown className="mr-2 h-4 w-4" />
              {sortOrder === 'asc' ? 'Oldest First' : 'Newest First'}
            </button>
          </div>

          {/* Transactions List */}
          {loading ? (
            <div className="flex justify-center items-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
            </div>
          ) : filteredTransactions.length === 0 ? (
            <div className="text-center py-8">
              <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No transactions found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Try adjusting your search or filters to find what you're looking for.
              </p>
            </div>
          ) : (
            <div className="mt-4">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Description
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Category
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredTransactions.map((transaction) => (
                      <tr
                        key={transaction.id}
                        className={cn(
                          "hover:bg-gray-50",
                          selectedTransaction?.id === transaction.id && "bg-indigo-50"
                        )}
                      >
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {format(new Date(transaction.date), 'MMM d, yyyy')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {transaction.merchant_name || transaction.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {transaction.category}
                        </td>
                        <td className={cn(
                          "px-6 py-4 whitespace-nowrap text-sm font-medium",
                          transaction.amount < 0 ? "text-red-600" : "text-green-600"
                        )}>
                          ${Math.abs(transaction.amount).toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <button
                            onClick={() => getAIInsights(transaction)}
                            className="inline-flex items-center px-2 py-1 border border-transparent text-xs font-medium rounded text-indigo-700 bg-indigo-100 hover:bg-indigo-200"
                          >
                            {aiLoading && selectedTransaction?.id === transaction.id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Brain className="h-4 w-4" />
                            )}
                            <span className="ml-1">AI Insights</span>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="flex items-center justify-between px-4 py-3 bg-white border-t border-gray-200 sm:px-6">
                <div className="flex justify-between flex-1">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* AI Insights Panel */}
      {selectedTransaction?.ai_insights && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">AI Insights</h2>
          <div className="prose prose-indigo">
            {selectedTransaction.ai_insights}
          </div>
        </div>
      )}
    </div>
  );
}