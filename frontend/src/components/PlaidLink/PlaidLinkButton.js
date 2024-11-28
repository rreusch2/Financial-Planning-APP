import React, { useCallback, useEffect, useState } from "react";
import { usePlaidLink } from "react-plaid-link";
import { Loader, RefreshCw } from "lucide-react";

export const PlaidLinkButton = () => {
  const [linkToken, setLinkToken] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateLinkToken = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(
        "http://localhost:5028/api/create_link_token",
        {
          method: "GET",
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to generate link token");
      }

      const { link_token } = await response.json();
      setLinkToken(link_token);
    } catch (err) {
      console.error("Error generating link token:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    generateLinkToken();
  }, [generateLinkToken]);

  const onSuccess = useCallback(async (publicToken, metadata) => {
    try {
      setLoading(true);
      const response = await fetch(
        "http://localhost:5028/api/exchange_public_token",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({ public_token: publicToken }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to exchange token");
      }

      // Sync transactions after successful connection
      await syncTransactions();

      window.location.reload(); // Refresh to show new data
    } catch (err) {
      console.error("Error linking bank:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const syncTransactions = async () => {
    try {
      const response = await fetch(
        "http://localhost:5028/api/transactions/sync",
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to sync transactions");
      }
    } catch (err) {
      console.error("Error syncing transactions:", err);
      setError(err.message);
    }
  };

  const { open, ready } = usePlaidLink({
    token: linkToken,
    onSuccess,
    onExit: (err) => {
      if (err) setError(err.message);
    },
  });

  if (loading) {
    return (
      <button
        className="flex items-center px-4 py-2 bg-gray-200 text-gray-500 rounded cursor-not-allowed"
        disabled
      >
        <Loader className="animate-spin mr-2 h-4 w-4" />
        Connecting...
      </button>
    );
  }

  if (error) {
    return (
      <div className="text-red-500">
        <p>{error}</p>
        <button
          onClick={generateLinkToken}
          className="mt-2 flex items-center px-4 py-2 bg-red-100 text-red-600 rounded hover:bg-red-200"
        >
          <RefreshCw className="mr-2 h-4 w-4" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={() => open()}
      disabled={!ready || !linkToken}
      className={`px-4 py-2 rounded ${
        ready && linkToken
          ? "bg-blue-600 text-white hover:bg-blue-700"
          : "bg-gray-200 text-gray-500 cursor-not-allowed"
      }`}
    >
      Connect Your Bank Account
    </button>
  );
};

export default PlaidLinkButton;
