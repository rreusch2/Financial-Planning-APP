import React from 'react';
import { Link } from 'react-router-dom';

function Navigation() {
  return (
    <nav>
      <ul>
        <li><Link to="/dashboard">Dashboard</Link></li>
        <li><Link to="/budget">Budget</Link></li>
        {/* Add other links here */}
      </ul>
    </nav>
  );
}

export default Navigation; 