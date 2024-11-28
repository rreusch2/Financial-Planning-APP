import React from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import {
  LayoutDashboard,
  LineChart,
  PieChart,
  Settings,
  CreditCard,
  LogOut,
  User,
} from "lucide-react";

const Layout = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  const navItems = [
    { path: "/", icon: LayoutDashboard, label: "Dashboard" },
    { path: "/investments", icon: LineChart, label: "Investments" },
    { path: "/budgets", icon: PieChart, label: "Budgets" },
    { path: "/credit-score", icon: CreditCard, label: "Credit Score" },
    { path: "/settings", icon: Settings, label: "Settings" },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation Bar */}
      <nav className="bg-white shadow-sm fixed w-full z-10">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center">
              <span className="text-xl font-bold text-blue-600">
                FinanceTracker
              </span>
            </div>

            {/* Navigation Items */}
            <div className="hidden md:flex items-center space-x-4">
              {navItems.map((item) => (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className="flex items-center px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100"
                >
                  <item.icon className="w-5 h-5 mr-2" />
                  {item.label}
                </button>
              ))}
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-700">
                <User className="w-5 h-5 inline-block mr-2" />
                {user?.username}
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center px-3 py-2 text-red-600 hover:bg-red-50 rounded-md"
              >
                <LogOut className="w-5 h-5 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="pt-16 pb-12">
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
