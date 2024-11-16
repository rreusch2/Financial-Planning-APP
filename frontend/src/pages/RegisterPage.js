// src/pages/RegisterPage.js
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const RegisterPage = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [flashMessages, setFlashMessages] = useState([]);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Client-side validation
    if (password !== confirmPassword) {
      setFlashMessages([{ category: 'error', message: 'Passwords do not match. Please try again.' }]);
      return;
    }

    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password, confirm_password: confirmPassword }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle server-side validation errors
        setFlashMessages(data.messages || [{ category: 'error', message: 'Registration failed.' }]);
      } else {
        // Registration successful
        setFlashMessages([{ category: 'success', message: 'Registration successful. Please log in.' }]);
        // Redirect to login page after a short delay
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      }
    } catch (error) {
      console.error('Error during registration:', error);
      setFlashMessages([{ category: 'error', message: 'An unexpected error occurred. Please try again later.' }]);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white p-6 rounded shadow-md">
        <h1 className="text-2xl font-bold mb-4 text-center">Register</h1>

        {/* Flash Messages */}
        {flashMessages.length > 0 && (
          <div id="flash-messages" className="mb-4">
            {flashMessages.map((msg, index) => (
              <div
                key={index}
                className={`p-2 mb-2 rounded ${
                  msg.category === 'success' ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'
                }`}
              >
                {msg.message}
              </div>
            ))}
          </div>
        )}

        {/* Registration Form */}
        <form onSubmit={handleSubmit} className="register-form">
          <div className="mb-4">
            <label htmlFor="username" className="block mb-1">
              Username:
            </label>
            <input
              type="text"
              id="username"
              name="username"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full border px-3 py-2 rounded"
            />
          </div>

          <div className="mb-4">
            <label htmlFor="email" className="block mb-1">
              Email:
            </label>
            <input
              type="email"
              id="email"
              name="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full border px-3 py-2 rounded"
            />
          </div>

          <div className="mb-4">
            <label htmlFor="password" className="block mb-1">
              Password:
            </label>
            <input
              type="password"
              id="password"
              name="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full border px-3 py-2 rounded"
            />
            <small className="text-gray-600">Password must be at least 8 characters long.</small>
          </div>

          <div className="mb-4">
            <label htmlFor="confirm_password" className="block mb-1">
              Confirm Password:
            </label>
            <input
              type="password"
              id="confirm_password"
              name="confirm_password"
              placeholder="Re-enter your password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="w-full border px-3 py-2 rounded"
            />
          </div>

          <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded">
            Register
          </button>
        </form>

        <p className="mt-4 text-center">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-600 hover:underline">
            Log in here.
          </Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
