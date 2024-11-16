// src/pages/InvestmentsPage.js
import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Loader, RefreshCw, ChevronDown, ChevronUp } from 'lucide-react';

const InvestmentsPage = () => {
  const [investments, setInvestments] = useState([]);
  const [portfolioValue, setPortfolioValue] = useState(0);
  const [totalReturn, setTotalReturn] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState({ field: 'marketValue', direction: 'desc' });
  const [filter, setFilter] = useState('');

  useEffect(() => {
    fetchInvestmentData();
  }, [sortBy]);

  const fetchInvestmentData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`/api/investments?sort_by=${sortBy.field}&sort_direction=${sortBy.direction}`);
      if (!response.ok) throw new Error('Failed to fetch investment data');
      const data = await response.json();
      setInvestments(data.investments);
      setPortfolioValue(data.portfolioValue);
      setTotalReturn(data.totalReturn);
    } catch (error) {
      setError(error.message);
      console.error('Error fetching investment data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field) => {
    setSortBy(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const SortIcon = ({ field }) => {
    if (sortBy.field !== field) return null;
    return sortBy.direction === 'asc' ? 
      <ChevronUp className="inline w-4 h-4" /> : 
      <ChevronDown className="inline w-4 h-4" />;
  };

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <p className="text-red-700">Error: {error}</p>
          <button 
            onClick={fetchInvestmentData}
            className="mt-2 px-4 py-2 bg-red-100 text-red-800 rounded hover:bg-red-200"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Loader className="animate-spin h-8 w-8 text-blue-500" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Refresh Button */}
      <div className="flex justify-end mb-4">
        <button 
          onClick={fetchInvestmentData}
          className="flex items-center px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Search Filter */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search investments..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="w-full md:w-64 px-4 py-2 border rounded-lg"
        />
      </div>

      {/* Rest of your existing code... */}
      
      {/* Update table headers to include sort functionality */}
      <thead className="bg-gray-50">
        <tr>
          <th 
            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
            onClick={() => handleSort('symbol')}
          >
            Asset <SortIcon field="symbol" />
          </th>
          <th 
            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
            onClick={() => handleSort('quantity')}
          >
            Quantity <SortIcon field="quantity" />
          </th>
          <th 
            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
            onClick={() => handleSort('currentPrice')}
          >
            Current Price <SortIcon field="currentPrice" />
          </th>
          <th 
            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
            onClick={() => handleSort('marketValue')}
          >
            Market Value <SortIcon field="marketValue" />
          </th>
          <th 
            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
            onClick={() => handleSort('return')}
          >
            Return <SortIcon field="return" />
          </th>
        </tr>
      </thead>

      {/* Filter investments in the table body */}
      <tbody className="bg-white divide-y divide-gray-200">
        {investments
          .filter(investment => 
            filter === '' || 
            investment.symbol.toLowerCase().includes(filter.toLowerCase()) ||
            investment.name.toLowerCase().includes(filter.toLowerCase())
          )
          .map((investment) => (
            <tr key={investment.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{investment.symbol}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{investment.quantity}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{investment.currentPrice}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{investment.marketValue}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{investment.return}</td>
            </tr>
          ))}
      </tbody>
    </div>
  );
};

export default InvestmentsPage;