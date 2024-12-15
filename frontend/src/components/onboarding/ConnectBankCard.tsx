import React from 'react';
import { Building2, ArrowRight } from 'lucide-react';
import PlaidLink from '../PlaidLink';

interface ConnectBankCardProps {
  onSuccess: () => void;
}

export function ConnectBankCard({ onSuccess }: ConnectBankCardProps) {
  return (
    <div className="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden">
      <div className="p-8">
        <div className="flex justify-center">
          <Building2 className="h-12 w-12 text-indigo-600" />
        </div>
        <div className="mt-4 text-center">
          <h3 className="text-xl font-semibold text-gray-900">
            Connect Your Bank Account
          </h3>
          <p className="mt-2 text-gray-600">
            Get started by securely connecting your accounts
          </p>
        </div>
        <div className="mt-6 space-y-4">
          <div className="flex items-center gap-3">
            <ArrowRight className="h-5 w-5 text-indigo-600 flex-shrink-0" />
            <span className="text-sm text-gray-600">Bank-level security</span>
          </div>
          <div className="flex items-center gap-3">
            <ArrowRight className="h-5 w-5 text-indigo-600 flex-shrink-0" />
            <span className="text-sm text-gray-600">Real-time updates</span>
          </div>
          <div className="flex items-center gap-3">
            <ArrowRight className="h-5 w-5 text-indigo-600 flex-shrink-0" />
            <span className="text-sm text-gray-600">AI-powered insights</span>
          </div>
        </div>
        <div className="mt-8">
          <PlaidLink onSuccess={onSuccess} />
        </div>
      </div>
    </div>
  );
}