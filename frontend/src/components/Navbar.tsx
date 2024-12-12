import React from 'react';
import { Link } from 'react-router-dom';
import { Wallet, Bell, LogOut } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="h-16 bg-white border-b border-gray-200">
      <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link to="/" className="flex items-center">
              <Wallet className="h-8 w-8 text-indigo-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">WealthAI</span>
            </Link>
          </div>

          <div className="flex items-center gap-4">
            <button className="p-2 rounded-full text-gray-500 hover:text-gray-700">
              <Bell className="h-6 w-6" />
            </button>
            {user && (
              <>
                <span className="text-sm text-gray-700">
                  {user.username}
                </span>
                <button
                  onClick={logout}
                  className="p-2 rounded-full text-gray-500 hover:text-gray-700"
                >
                  <LogOut className="h-6 w-6" />
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}