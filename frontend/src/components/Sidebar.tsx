import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  PiggyBank,
  LineChart,
  Target,
  Settings,
  MessageSquareText,
  Wallet
} from 'lucide-react';
import { cn } from '../lib/utils';

const navigation = [
  { name: 'Dashboard', icon: LayoutDashboard, href: '/app/dashboard' },
  { name: 'Transactions', icon: PiggyBank, href: '/app/transactions' },
  { name: 'Budget', icon: Wallet, href: '/app/budget' },
  { name: 'Analytics', icon: LineChart, href: '/app/analytics' },
  { name: 'Goals', icon: Target, href: '/app/goals' },
  { name: 'AI Advisor', icon: MessageSquareText, href: '/app/advisor' },
  { name: 'Settings', icon: Settings, href: '/app/settings' },
];

export default function Sidebar() {
  return (
    <div className="w-64 bg-white border-r border-gray-200 flex-shrink-0">
      <nav className="mt-8">
        <div className="px-2 space-y-1">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  'group flex items-center px-4 py-2 text-sm font-medium rounded-md',
                  isActive
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )
              }
            >
              <item.icon
                className={cn(
                  'mr-3 h-5 w-5 flex-shrink-0',
                  'text-gray-400 group-hover:text-gray-500'
                )}
                aria-hidden="true"
              />
              {item.name}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  );
}