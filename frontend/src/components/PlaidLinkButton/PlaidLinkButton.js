import React, { useEffect, useState, useCallback } from 'react';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

const PlaidLinkButton = ({ onSuccess }) => {
  const [linkToken, setLinkToken] = useState(null);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);

  // Initialize Plaid Link
  const initializePlaidLink = useCallback((token) => {
    // Load Plaid Link script if it hasn't been loaded yet
    if (!window.Plaid) {
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/plaid-link/2.0.0/link-initialize.js';
      script.async = true;
      script.onload = () => {
        createPlaidLink(token);
      };
      document.body.appendChild(script);
    } else {
      createPlaidLink(token);
    }
  }, []);

  // Create Plaid Link instance
  const createPlaidLink = useCallback((token) => {
    const plaidConfig = {
      token,
      onSuccess: async (publicToken, metadata) => {
        try {
          setStatus('connecting');
          const response = await fetch('/api/exchange_public_token', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ 
              public_token: publicToken,
              institution: metadata.institution,
              accounts: metadata.accounts
            }),
          });

          if (!response.ok) {
            throw new Error('Failed to exchange token');
          }

          setStatus('success');
          if (onSuccess) {
            onSuccess(metadata);
          }
        } catch (err) {
          console.error('Error in Plaid flow:', err);
          setError(err.message);
          setStatus('error');
        }
      },
      onExit: (err) => {
        if (err) {
          setError(err.message);
          setStatus('error');
        }
      },
    };

    const handler = window.Plaid.create(plaidConfig);
    return handler;
  }, [onSuccess]);

  // Fetch link token from your server
  const fetchLinkToken = useCallback(async () => {
    try {
      setStatus('loading');
      setError(null);
      
      const response = await fetch('/api/create_link_token', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      if (!data.link_token) {
        throw new Error('No link token received');
      }

      setLinkToken(data.link_token);
      setStatus('ready');
      initializePlaidLink(data.link_token);
    } catch (err) {
      console.error('Error fetching link token:', err);
      setError(err.message);
      setStatus('error');
    }
  }, [initializePlaidLink]);

  useEffect(() => {
    fetchLinkToken();
  }, [fetchLinkToken]);

  const handleClick = useCallback(() => {
    if (window.Plaid) {
      const handler = createPlaidLink(linkToken);
      handler.open();
    }
  }, [linkToken, createPlaidLink]);

  const renderButton = () => {
    if (status === 'loading') {
      return (
        <button disabled className="px-4 py-2 bg-gray-400 text-white rounded-md flex items-center">
          <div className="animate-spin mr-2">⟳</div>
          Loading...
        </button>
      );
    }

    if (status === 'error') {
      return (
        <div className="flex flex-col items-start">
          <button
            onClick={fetchLinkToken}
            className="px-4 py-2 bg-red-600 text-white rounded-md flex items-center"
          >
            <AlertCircle className="w-4 h-4 mr-2" />
            Retry Connection
          </button>
          {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
        </div>
      );
    }

    if (status === 'success') {
      return (
        <button disabled className="px-4 py-2 bg-green-600 text-white rounded-md flex items-center">
          <CheckCircle2 className="w-4 h-4 mr-2" />
          Connected
        </button>
      );
    }

    return (
      <button
        onClick={handleClick}
        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Connect Bank Account
      </button>
    );
  };

  return (
    <div className="plaid-link-wrapper">
      {renderButton()}
    </div>
  );
};

export default PlaidLinkButton;