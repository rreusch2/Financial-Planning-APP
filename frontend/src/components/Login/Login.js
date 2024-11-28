// src/components/Login/Login.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchWithError } from "../../api"; // Centralize API calls

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetchWithError("/api/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
        credentials: "include",
      });

      if (response) {
        console.log("Login successful:", response.message);

        // Fetch the current user to ensure authentication state
        const userData = await fetchWithError("/api/auth/check", {
          method: "GET",
          credentials: "include",
        });

        console.log("Current user:", userData);
        navigate("/dashboard"); // Redirect after successful login
      }
    } catch (err) {
      console.error("Login error:", err);
      setError(err.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>
        {error && <div className="text-red-500 mb-4">{error}</div>}
        <form onSubmit={handleLogin}>
          <div className="mb-4">
            <label className="block text-gray-700">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-3 py-2 border rounded"
            />
          </div>
          <div className="mb-6">
            <label className="block text-gray-700">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-3 py-2 border rounded"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className={`w-full py-2 px-4 bg-blue-600 text-white rounded ${
              loading ? "opacity-50 cursor-not-allowed" : "hover:bg-blue-700"
            }`}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
        <div className="mt-4 text-center">
          <a href="/register" className="text-blue-600 hover:underline">
            Don't have an account? Register here.
          </a>
        </div>
      </div>
    </div>
  );
};

export default Login;
