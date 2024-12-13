import React, { useCallback, useEffect } from 'react';
import { usePlaidLink } from 'react-plaid-link';
import { Loader2, AlertCircle } from 'lucide-react';
import { plaidApi } from '../lib/plaid';

interface PlaidLinkProps {
  onSuccess: () => void;
  onExit?: () => void;
}

export default function PlaidLink({ onSuccess, onExit }: PlaidLinkProps) {
  const [linkToken, setLinkToken] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  const generateToken = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await plaidApi.getLinkToken();
      if (response?.link_token) {
        setLinkToken(response.link_token);
      } else {
        throw new Error('Invalid link token response');
      }
    } catch (err) {
      console.error('Error creating link token:', err);
      setError(err instanceof Error ? err.message : 'Failed to initialize Plaid');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    generateToken();
  }, [generateToken]);

  const handlePlaidSuccess = async (publicToken: string) => {
    try {
      setLoading(true);
      await plaidApi.exchangePublicToken(publicToken);
      const syncResponse = await plaidApi.syncTransactions();
      console.log('Transactions synced:', syncResponse);
      onSuccess();
    } catch (err) {
      console.error('Error in Plaid flow:', err);
      setError(err instanceof Error ? err.message : 'Failed to connect bank account');
    } finally {
      setLoading(false);
    }
  };

  const config = {
    token: linkToken ?? '',
    onSuccess: handlePlaidSuccess,
    onExit: () => {
      setError(null);
      onExit?.();
    }
  };

  const { open, ready } = usePlaidLink(config);

  if (loading) {
    return (
      <button disabled className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 opacity-50">
        <Loader2 className="animate-spin mr-2 h-5 w-5" />
        Connecting to Plaid...
      </button>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center gap-3">
        <div className="text-red-600 text-sm flex items-center gap-2">
          <AlertCircle className="h-5 w-5" />
          {error}
        </div>
        <button
          onClick={generateToken}
          className="text-sm text-indigo-600 hover:text-indigo-500 font-medium"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={() => {
        if (ready && linkToken) {
          open();
        }
      }}
      disabled={!ready || !linkToken}
      className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
    >
      Connect Your Bank Account
    </button>
  );
}