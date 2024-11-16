// src/components/PlaidLinkButton.js

import React, { useEffect, useState } from 'react';
import { PlaidLink } from 'react-plaid-link';

const PlaidLinkButton = () => {
  const [linkToken, setLinkToken] = useState(null);

  useEffect(() => {
    // Fetch the link token from backend
    fetch('/api/create_link_token', {
      method: 'GET',
      credentials: 'include',
    })
    .then(response => response.json())
    .then(data => {
      if (data.link_token) {
        setLinkToken(data.link_token);
      } else {
        console.error('Error fetching link token:', data.error);
      }
    })
    .catch(error => console.error('Error:', error));
  }, []);

  const onSuccess = (public_token, metadata) => {
    // Exchange the public token for an access token
    fetch('/api/exchange_public_token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ public_token }),
    })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        console.error('Error exchanging public token:', data.error);
      } else {
        console.log('Public token exchanged successfully:', data);
      }
    })
    .catch(error => console.error('Error:', error));
  };

  const config = {
    token: linkToken,
    onSuccess,
    onExit: (error, metadata) => {
      if (error) {
        console.error('Plaid Link Error:', error);
      }
      // Handle the case when user exits the Plaid Link flow
    },
  };

  if (!linkToken) {
    return <div>Loading...</div>;
  }

  return (
    <PlaidLink {...config}>
      Connect your bank account
    </PlaidLink>
  );
};

export default PlaidLinkButton;
