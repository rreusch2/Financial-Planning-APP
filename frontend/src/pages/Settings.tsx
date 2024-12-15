import React, { useState } from 'react';
import { Settings as SettingsIcon, Bell, Lock, User, CreditCard } from 'lucide-react';

function BudgetSetup() {
  const [category, setCategory] = useState('');
  const [limit, setLimit] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch('/api/budget', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category, limit }),
    });
    const data = await response.json();
    console.log(data.message);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        placeholder="Category"
      />
      <input
        type="number"
        value={limit}
        onChange={(e) => setLimit(e.target.value)}
        placeholder="Limit"
      />
      <button type="submit">Set Budget</button>
    </form>
  );
}

export default function Settings() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Settings</h1>
      </div>

      <div className="bg-white shadow rounded-lg divide-y divide-gray-200">
        <div className="p-6">
          <div className="flex items-center">
            <User className="h-6 w-6 text-gray-400" />
            <h2 className="ml-3 text-lg font-medium text-gray-900">Profile Settings</h2>
          </div>
          <div className="mt-6 grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div className="sm:col-span-3">
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Username
              </label>
              <input
                type="text"
                name="username"
                id="username"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                type="email"
                name="email"
                id="email"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>
          </div>
        </div>

        <div className="p-6">
          <div className="flex items-center">
            <Lock className="h-6 w-6 text-gray-400" />
            <h2 className="ml-3 text-lg font-medium text-gray-900">Security</h2>
          </div>
          <div className="mt-6">
            <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
              Change Password
            </button>
          </div>
        </div>

        <div className="p-6">
          <div className="flex items-center">
            <Bell className="h-6 w-6 text-gray-400" />
            <h2 className="ml-3 text-lg font-medium text-gray-900">Notifications</h2>
          </div>
          <div className="mt-6">
            <div className="space-y-4">
              <div className="flex items-start">
                <div className="flex items-center h-5">
                  <input
                    id="email_notifications"
                    name="email_notifications"
                    type="checkbox"
                    className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                  />
                </div>
                <div className="ml-3 text-sm">
                  <label htmlFor="email_notifications" className="font-medium text-gray-700">
                    Email notifications
                  </label>
                  <p className="text-gray-500">Get notified about important updates and alerts.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="p-6">
          <div className="flex items-center">
            <CreditCard className="h-6 w-6 text-gray-400" />
            <h2 className="ml-3 text-lg font-medium text-gray-900">Connected Accounts</h2>
          </div>
          <div className="mt-6">
            <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
              Manage Connected Banks
            </button>
          </div>
        </div>
      </div>

      <BudgetSetup />
    </div>
  );
}