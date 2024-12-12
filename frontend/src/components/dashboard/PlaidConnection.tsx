import React from 'react';
import { Building2, ArrowRight } from 'lucide-react';
import PlaidLink from '../PlaidLink';

interface PlaidConnectionProps {
  onSuccess: () => void;
}

export function PlaidConnection({ onSuccess }: PlaidConnectionProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="p-8">
        <div className="flex items-center justify-center w-16 h-16 bg-indigo-100 rounded-full mx-auto">
          <Building2 className="w-8 h-8 text-indigo-600" />
        </div>

        <h2 className="mt-6 text-2xl font-bold text-center text-gray-900">
          Connect Your Bank Account
        </h2>

        <p className="mt-4 text-center text-gray-600 max-w-md mx-auto">
          Link your bank account to get personalized financial insights, track your spending, and receive AI-powered recommendations.
        </p>

        <div className="mt-8 space-y-4">
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <ArrowRight className="w-5 h-5 text-indigo-600 flex-shrink-0" />
            <span>Securely connect your accounts with bank-level encryption</span>
          </div>

          <div className="flex items-center gap-4 text-sm text-gray-600">
            <ArrowRight className="w-5 h-5 text-indigo-600 flex-shrink-0" />
            <span>Get real-time transaction updates and spending insights</span>
          </div>

          <div className="flex items-center gap-4 text-sm text-gray-600">
            <ArrowRight className="w-5 h-5 text-indigo-600 flex-shrink-0" />
            <span>Receive personalized AI-powered financial advice</span>
          </div>
        </div>

        <div className="mt-8 flex justify-center">
          <PlaidLink onSuccess={onSuccess} />
        </div>
      </div>
    </div>
  );
}