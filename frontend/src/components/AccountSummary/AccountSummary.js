import React from "react";

function AccountSummary({
  totalIncome = 0,
  totalExpenses = 0,
  netBalance = 0,
}) {
  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">Account Summary</h2>
      <div className="flex justify-between">
        <div>
          <p className="text-sm text-gray-500">Total Income</p>
          <p className="text-lg font-bold text-green-600">
            ${totalIncome.toFixed(2)}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Total Expenses</p>
          <p className="text-lg font-bold text-red-600">
            ${totalExpenses.toFixed(2)}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Net Balance</p>
          <p className="text-lg font-bold text-blue-600">
            ${netBalance.toFixed(2)}
          </p>
        </div>
      </div>
    </div>
  );
}

export default AccountSummary;
