// src/components/IncomeSources/IncomeSources.js
import React, { useState, useEffect } from 'react';
import { PlusCircle, Edit2, Trash2 } from 'lucide-react';

const IncomeSources = () => {
  const [incomeSources, setIncomeSources] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    source_name: '',
    amount: '',
    frequency: 'monthly',
    type: 'salary'
  });
  const [editing, setEditing] = useState(null);
  const [error, setError] = useState(null); // New state for error handling

  useEffect(() => {
    fetchIncomeSources();
  }, []);

  const fetchIncomeSources = async () => {
    try {
      const response = await fetch('/api/income', {
        credentials: 'include', // Ensure session cookies are sent
      });
      const data = await response.json();

      if (response.ok) {
        if (Array.isArray(data)) {
          setIncomeSources(data);
          setError(null);
        } else {
          setError('Received unexpected data format from server.');
          setIncomeSources([]);
        }
      } else {
        setError(data.error || 'Failed to fetch income sources.');
        setIncomeSources([]);
      }
    } catch (error) {
      console.error('Error fetching income sources:', error);
      setError('An error occurred while fetching income sources.');
      setIncomeSources([]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editing 
        ? `/api/income/${editing}` 
        : '/api/income';
      
      const response = await fetch(url, {
        method: editing ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        fetchIncomeSources();
        setShowAddModal(false);
        setFormData({
          source_name: '',
          amount: '',
          frequency: 'monthly',
          type: 'salary'
        });
        setEditing(null);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to save income source.');
      }
    } catch (error) {
      console.error('Error saving income source:', error);
      setError('An error occurred while saving the income source.');
    }
  };

  const calculateMonthlyAmount = (amount, frequency) => {
    switch (frequency) {
      case 'weekly':
        return amount * 4;
      case 'bi-weekly':
        return amount * 2;
      case 'monthly':
        return amount;
      case 'yearly':
        return amount / 12;
      default:
        return amount;
    }
  };

  // Safely compute totalMonthlyIncome
  const totalMonthlyIncome = Array.isArray(incomeSources)
    ? incomeSources.reduce((total, source) => {
        return total + calculateMonthlyAmount(parseFloat(source.amount), source.frequency);
      }, 0)
    : 0;

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Income Sources</h2>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
        >
          <PlusCircle className="w-5 h-5" />
          Add Income Source
        </button>
      </div>

      {/* Display Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Income Sources List */}
      <div className="space-y-4">
        {Array.isArray(incomeSources) && incomeSources.map((source) => (
          <div 
            key={source.id}
            className="p-4 border rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold text-lg">{source.source_name}</h3>
                <p className="text-sm text-gray-600">
                  ${parseFloat(source.amount).toLocaleString()} • {source.frequency}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Monthly equivalent: ${calculateMonthlyAmount(parseFloat(source.amount), source.frequency).toLocaleString()}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setFormData(source);
                    setEditing(source.id);
                    setShowAddModal(true);
                  }}
                  className="p-2 text-blue-600 hover:bg-blue-50 rounded-full"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
                <button
                  onClick={async () => {
                    if (window.confirm('Are you sure you want to delete this income source?')) {
                      try {
                        const deleteResponse = await fetch(`/api/income/${source.id}`, { method: 'DELETE', credentials: 'include' });
                        if (deleteResponse.ok) {
                          fetchIncomeSources();
                        } else {
                          const deleteError = await deleteResponse.json();
                          setError(deleteError.error || 'Failed to delete income source.');
                        }
                      } catch (error) {
                        console.error('Error deleting income source:', error);
                        setError('An error occurred while deleting the income source.');
                      }
                    }
                  }}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-full"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}

        {Array.isArray(incomeSources) && incomeSources.length === 0 && (
          <p className="text-center text-gray-500 py-4">
            No income sources added yet. Click the button above to add one.
          </p>
        )}

        {Array.isArray(incomeSources) && incomeSources.length > 0 && (
          <div className="mt-6 p-4 bg-green-50 rounded-lg">
            <h3 className="font-semibold text-green-800">Total Monthly Income</h3>
            <p className="text-2xl font-bold text-green-600">
              ${totalMonthlyIncome.toLocaleString()}
            </p>
          </div>
        )}
      </div>

      {/* Add/Edit Income Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-xl font-bold mb-4">
              {editing ? 'Edit Income Source' : 'Add Income Source'}
            </h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Source Name
                </label>
                <input
                  type="text"
                  value={formData.source_name}
                  onChange={(e) => setFormData({
                    ...formData,
                    source_name: e.target.value
                  })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Amount
                </label>
                <input
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData({
                    ...formData,
                    amount: e.target.value
                  })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Frequency
                </label>
                <select
                  value={formData.frequency}
                  onChange={(e) => setFormData({
                    ...formData,
                    frequency: e.target.value
                  })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="weekly">Weekly</option>
                  <option value="bi-weekly">Bi-weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Type
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({
                    ...formData,
                    type: e.target.value
                  })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="salary">Salary</option>
                  <option value="hourly">Hourly Wage</option>
                  <option value="investment">Investment</option>
                  <option value="business">Business</option>
                  <option value="freelance">Freelance</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className="flex gap-2 justify-end mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowAddModal(false);
                    setFormData({
                      source_name: '',
                      amount: '',
                      frequency: 'monthly',
                      type: 'salary'
                    });
                    setEditing(null);
                    setError(null); // Clear any existing errors
                  }}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  {editing ? 'Save Changes' : 'Add Income'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default IncomeSources;
