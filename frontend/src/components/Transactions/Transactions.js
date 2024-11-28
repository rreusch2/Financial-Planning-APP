import React, { useState } from "react";
import { ChevronDown, ChevronUp, Search } from "lucide-react";

const Transactions = ({ transactions = [] }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortConfig, setSortConfig] = useState({
    key: "date",
    direction: "desc",
  });

  const handleSort = (key) => {
    setSortConfig((prevSort) => ({
      key,
      direction:
        prevSort.key === key && prevSort.direction === "asc" ? "desc" : "asc",
    }));
  };

  const sortedTransactions = Array.isArray(transactions)
    ? [...transactions].sort((a, b) => {
        const direction = sortConfig.direction === "asc" ? 1 : -1;
        if (sortConfig.key === "date") {
          return direction * (new Date(a.date) - new Date(b.date));
        } else if (sortConfig.key === "amount") {
          return direction * (a.amount - b.amount);
        }
        const valueA = (a[sortConfig.key] || "").toLowerCase();
        const valueB = (b[sortConfig.key] || "").toLowerCase();
        return direction * valueA.localeCompare(valueB);
      })
    : [];

  const filteredTransactions = sortedTransactions.filter((transaction) => {
    const lowerSearch = searchTerm.toLowerCase();
    return (
      transaction.name.toLowerCase().includes(lowerSearch) ||
      transaction.category?.toLowerCase().includes(lowerSearch) ||
      transaction.amount.toString().includes(lowerSearch)
    );
  });

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Recent Transactions</h2>
        <div className="relative">
          <input
            type="text"
            placeholder="Search transactions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                onClick={() => handleSort("date")}
              >
                Date <ChevronDown />
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                onClick={() => handleSort("name")}
              >
                Description <ChevronDown />
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                onClick={() => handleSort("category")}
              >
                Category <ChevronDown />
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                onClick={() => handleSort("amount")}
              >
                Amount <ChevronDown />
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredTransactions.length === 0 ? (
              <tr>
                <td colSpan="4" className="px-6 py-4 text-center text-gray-500">
                  No transactions found.
                </td>
              </tr>
            ) : (
              filteredTransactions.map((transaction) => (
                <tr key={transaction.id}>
                  <td>{new Date(transaction.date).toLocaleDateString()}</td>
                  <td>{transaction.name}</td>
                  <td>{transaction.category || "Uncategorized"}</td>
                  <td
                    className={
                      transaction.amount < 0 ? "text-red-600" : "text-green-600"
                    }
                  >
                    ${Math.abs(transaction.amount).toFixed(2)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
export default Transactions;
