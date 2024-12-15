import { Bell, Brain, User } from 'lucide-react';
import React from 'react';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white shadow-sm">
          <div className="px-6 py-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-2">
                <Brain className="h-6 w-6 text-indigo-600" />
                <h2 className="text-xl font-semibold text-gray-800">WealthAI</h2>
              </div>
              <div className="flex items-center space-x-4">
                <button className="p-1 rounded-full hover:bg-gray-100">
                  <Bell className="h-6 w-6 text-gray-500" />
                </button>
                <button className="p-1 rounded-full hover:bg-gray-100">
                  <User className="h-6 w-6 text-gray-500" />
                </button>
              </div>
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}