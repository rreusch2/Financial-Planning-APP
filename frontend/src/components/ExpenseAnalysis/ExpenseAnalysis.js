// src/components/ExpenseAnalysis/ExpenseAnalysis.js

import React, { useState, useEffect } from 'react';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import Typography from '@mui/material/Typography';
import { 
  ResponsiveContainer, 
  BarChart, 
  CartesianGrid, 
  XAxis, 
  YAxis, 
  Bar, 
  Tooltip, 
  Legend 
} from 'recharts';

// ExpenseSummary Component: Renders the BarChart for expenses
const ExpenseSummary = ({ expenses, handleExpenseClick }) => {
  return (
    <div className="w-full h-96">
      <ResponsiveContainer>
        <BarChart 
          data={expenses} 
          onClick={(data, index) => handleExpenseClick(data.activePayload[0].payload)}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="amount" fill="#8884d8" name="Expense Amount" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

// ExpenseAnalysis Component: Main component managing state and rendering ExpenseSummary and Dialog
const ExpenseAnalysis = () => {
  const [expenses, setExpenses] = useState([]);
  const [timeFrame, setTimeFrame] = useState('monthly');
  const [showSummary, setShowSummary] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedExpense, setSelectedExpense] = useState(null);

  // Fetch expense data whenever timeFrame changes
  useEffect(() => {
    let isMounted = true;

    const fetchExpenseData = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`/api/expenses_summary?period=${timeFrame}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (isMounted) {
          setExpenses(data);
          setShowSummary(true);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchExpenseData();

    return () => {
      isMounted = false;
    };
  }, [timeFrame]);

  // Handle clicking on an expense bar in the chart
  const handleExpenseClick = (expense) => {
    setSelectedExpense(expense);
    setIsDialogOpen(true);
  };

  // Render loading state
  if (loading) {
    return <div className="text-center p-4">Loading expense data...</div>;
  }

  // Render error state
  if (error) {
    return <div className="text-red-500 p-4">Error loading expenses: {error}</div>;
  }

  return (
    <div className="p-4">
      {/* Time Frame Selection */}
      <div className="mb-4">
        <select
          value={timeFrame}
          onChange={(e) => setTimeFrame(e.target.value)}
          className="border rounded p-2"
        >
          <option value="monthly">Monthly</option>
          <option value="quarterly">Quarterly</option>
          <option value="yearly">Yearly</option>
        </select>
      </div>

      {/* Expense Summary Chart */}
      {showSummary && expenses.length > 0 ? (
        <ExpenseSummary 
          expenses={expenses} 
          handleExpenseClick={handleExpenseClick} 
        />
      ) : (
        <div className="text-center p-4">No expense data available</div>
      )}

      {/* Dialog for Selected Expense Details */}
      <Dialog
        open={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        aria-labelledby="expense-dialog-title"
        aria-describedby="expense-dialog-description"
      >
        <DialogTitle id="expense-dialog-title">Expense Details</DialogTitle>
        <DialogContent>
          {selectedExpense ? (
            <div>
              <Typography variant="body1"><strong>Date:</strong> {selectedExpense.date}</Typography>
              <Typography variant="body1"><strong>Amount:</strong> ${selectedExpense.amount}</Typography>
              <Typography variant="body1"><strong>Category:</strong> {selectedExpense.category}</Typography>
            </div>
          ) : (
            <Typography variant="body1">No expense details available.</Typography>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ExpenseAnalysis;
