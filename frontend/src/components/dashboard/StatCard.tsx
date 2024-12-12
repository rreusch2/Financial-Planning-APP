import React from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '../../lib/utils';

interface StatCardProps {
  title: string;
  value: number;
  icon: LucideIcon;
  type?: 'default' | 'income' | 'expense';
}

export function StatCard({ title, value, icon: Icon, type = 'default' }: StatCardProps) {
  const valueColor = type === 'income' ? 'text-green-600' :
    type === 'expense' ? 'text-red-600' :
      value >= 0 ? 'text-green-600' : 'text-red-600';

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <Icon className="h-6 w-6 text-indigo-600" />
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">
                {title}
              </dt>
              <dd className={cn("text-lg font-medium", valueColor)}>
                ${Math.abs(value).toFixed(2)}
              </dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}