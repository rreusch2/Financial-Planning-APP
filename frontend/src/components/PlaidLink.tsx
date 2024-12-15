import React from 'react';
import { usePlaidLink } from 'react-plaid-link';

interface PlaidLinkProps {
  onSuccess: () => void;
}

export default function PlaidLink({ onSuccess }: PlaidLinkProps) {
  const [linkToken, setLinkToken] = React.useState<string | null>(null);

  React.useEffect(() => {
    const getLinkToken = async () => {
      try {
        const response = await fetch('/api/plaid/create_link_token', {
          credentials: 'include'
        });
        const { link_token } = await response.json();
        setLinkToken(link_token);
      } catch (err) {
        console.error('Error getting link token:', err);
      }
    };
    getLinkToken();
  }, []);

  const { open, ready } = usePlaidLink({
    token: linkToken,
    onSuccess: async (public_token) => {
      try {
        // Exchange public token
        const exchangeResponse = await fetch('/api/plaid/exchange_public_token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ public_token })
        });
        
        if (exchangeResponse.ok) {
          // Sync transactions after successful connection
          const syncResponse = await fetch('/api/plaid/sync_transactions', {
            method: 'POST',
            credentials: 'include'
          });

          if (syncResponse.ok) {
            console.log('Transactions synced successfully');
            onSuccess();
          } else {
            console.error('Failed to sync transactions');
          }
        }
      } catch (err) {
        console.error('Error in Plaid flow:', err);
      }
    },
  });

  return (
    <button
      onClick={() => open()}
      disabled={!ready || !linkToken}
      className="w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      Connect Bank Account
    </button>
  );
}