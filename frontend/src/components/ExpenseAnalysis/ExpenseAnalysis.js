import React, { useState, useEffect } from "react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";

const COLORS = [
  "#0088FE",
  "#00C49F",
  "#FFBB28",
  "#FF8042",
  "#8884D8",
  "#82CA9D",
  "#A4DE6C",
  "#D0ED57",
  "#FAD000",
  "#F28A00",
];

const ExpenseAnalysis = () => {
  const [expenseData, setExpenseData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeframe, setTimeframe] = useState("monthly");

  const fetchExpenseData = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/expenses_summary?period=${timeframe}`,
        { credentials: "include" }
      );
      if (!response.ok) {
        throw new Error("Failed to fetch expense data.");
      }
      const data = await response.json();
      const formatted = Object.entries(data.expenses_by_category || {}).map(
        ([name, value]) => ({
          name,
          value: Math.abs(value),
        })
      );
      setExpenseData(formatted);
    } catch (err) {
      console.error(err);
      setError("Failed to load expense data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExpenseData();
  }, [timeframe]);

  return (
    <div className="bg-white p-6 shadow-lg rounded-lg">
      <div className="flex justify-between">
        <h2>Expense Analysis</h2>
        <select
          value={timeframe}
          onChange={(e) => setTimeframe(e.target.value)}
        >
          <option value="monthly">This Month</option>
          <option value="yearly">This Year</option>
        </select>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <PieChart>{/* Dynamic Pie Data */}</PieChart>
      )}
    </div>
  );
};
export default ExpenseAnalysis;
