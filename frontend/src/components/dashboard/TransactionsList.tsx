import React from 'react';
import { format } from 'date-fns';
import { cn } from '../../lib/utils';

interface Transaction {
  id: string;
  name: string;
  date: string;
  amount: number;
  category?: string;
}

interface TransactionsListProps {
  transactions: Transaction[];
}

export function TransactionsList({ transactions }: TransactionsListProps) {
  if (!transactions.length) {
    return <p className="text-gray-500">No recent transactions</p>;
  }

  return (
    <div className="space-y-4">
      {transactions.map((transaction) => (
        <div key={transaction.id} className="flex justify-between items-center">
          <div>
            <p className="font-medium">{transaction.name}</p>
            <div className="flex items-center gap-2">
              <p className="text-sm text-gray-500">
                {format(new Date(transaction.date), 'MMM d, yyyy')}
              </p>
              {transaction.category && (
                <>
                  <span className="text-gray-300">•</span>
                  <span className="text-sm text-gray-500">{transaction.category}</span>
                </>
              )}
            </div>
          </div>
          <span className={cn(
            "font-medium",
            transaction.amount < 0 ? "text-red-600" : "text-green-600"
          )}>
            ${Math.abs(transaction.amount).toFixed(2)}
          </span>
        </div>
      ))}
    </div>
  );
}