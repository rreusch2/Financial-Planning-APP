import React from 'react';
import { RefreshCw } from 'lucide-react';

interface DashboardHeaderProps {
  lastUpdated?: string;
  onRefresh: () => void;
}

export function DashboardHeader({ lastUpdated, onRefresh }: DashboardHeaderProps) {
  return (
    <div className="flex justify-between items-center">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Financial Dashboard</h1>
        <p className="text-sm text-gray-500">
          Last updated: {lastUpdated || 'Just now'}
        </p>
      </div>
      <button
        onClick={onRefresh}
        className="p-2 hover:bg-gray-100 rounded-full transition-colors"
        aria-label="Refresh dashboard"
      >
        <RefreshCw className="h-5 w-5 text-gray-600" />
      </button>
    </div>
  );
} 