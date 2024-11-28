import React, { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Dialog } from "@headlessui/react";
import { Loader, Search, X, RefreshCw } from "lucide-react";

function AIAdvice() {
  const [advice, setAdvice] = useState("");
  const [isLoadingAdvice, setIsLoadingAdvice] = useState(false);
  const [adviceError, setAdviceError] = useState(null);

  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("");
  const [timeFrame, setTimeFrame] = useState("monthly");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedExpense, setSelectedExpense] = useState(null);
  const [sortBy, setSortBy] = useState({ field: "date", direction: "desc" });

  const fetchAIAdvice = async () => {
    setIsLoadingAdvice(true);
    setAdviceError(null);
    try {
      const response = await fetch("/api/ai_advice");
      if (!response.ok) {
        throw new Error("Failed to fetch AI advice");
      }
      const data = await response.json();
      setAdvice(data.advice || "No advice available at this time.");
    } catch (err) {
      setAdviceError(
        err.message || "An error occurred while fetching AI advice."
      );
      console.error("Error fetching AI advice:", err);
    } finally {
      setIsLoadingAdvice(false);
    }
  };

  const fetchExpenseData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/transactions");
      if (!response.ok) {
        throw new Error("Failed to fetch expense data");
      }
      const data = await response.json();
      if (Array.isArray(data.transactions)) {
        setExpenses(data.transactions);
      } else {
        throw new Error("Invalid format for transactions data.");
      }
    } catch (err) {
      setError(err.message || "An error occurred while fetching expenses.");
      console.error("Error fetching expense data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAIAdvice();
    fetchExpenseData();
  }, []);

  const handleExpenseClick = (expense) => {
    setSelectedExpense(expense);
    setIsDialogOpen(true);
  };

  const sortedAndFilteredExpenses = Array.isArray(expenses)
    ? expenses
        .filter(
          (expense) =>
            filter === "" ||
            expense.name.toLowerCase().includes(filter.toLowerCase()) ||
            expense.category.toLowerCase().includes(filter.toLowerCase())
        )
        .sort((a, b) => {
          const modifier = sortBy.direction === "asc" ? 1 : -1;
          return a[sortBy.field] > b[sortBy.field] ? modifier : -modifier;
        })
    : [];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader className="animate-spin h-8 w-8 text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">AI Financial Insights</h2>
          <button
            onClick={fetchAIAdvice}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            disabled={isLoadingAdvice}
          >
            <RefreshCw
              className={`h-4 w-4 ${isLoadingAdvice ? "animate-spin" : ""}`}
            />
            Refresh Advice
          </button>
        </div>

        {isLoadingAdvice ? (
          <div className="flex justify-center py-4">
            <Loader className="animate-spin h-6 w-6 text-blue-500" />
          </div>
        ) : adviceError ? (
          <div className="text-red-500">{adviceError}</div>
        ) : (
          <div className="prose">
            <p className="text-gray-700">{advice}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default AIAdvice;
