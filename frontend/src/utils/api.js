const BASE_URL = "http://localhost:5028/api";

async function fetchWithError(endpoint, options = {}) {
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      credentials: "include",
    });

    const contentType = response.headers.get("content-type");
    let data;
    if (contentType && contentType.includes("application/json")) {
      data = await response.json();
    } else {
      throw new Error("Invalid response format from server");
    }

    if (!response.ok) {
      throw new Error(data.error || `HTTP error! status: ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

// Auth functions
export const checkAuth = () => fetchWithError("/auth/check");

export const login = (credentials) =>
  fetchWithError("/auth/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  });

export const register = (userData) =>
  fetchWithError("/auth/register", {
    method: "POST",
    body: JSON.stringify(userData),
  });

export const logout = () =>
  fetchWithError("/auth/logout", {
    method: "POST",
  });

// Transaction functions
export const fetchTransactions = (params = {}) => {
  const queryString = new URLSearchParams(params).toString();
  return fetchWithError(`/transactions${queryString ? `?${queryString}` : ""}`);
};

export const fetchAccountSummary = () => fetchWithError("/account_summary");

export const syncTransactions = () =>
  fetchWithError("/transactions/sync", {
    method: "POST",
  });

// Forecast function
export const fetchForecast = (forecastParams) =>
  fetchWithError("/forecast", {
    method: "POST",
    body: JSON.stringify(forecastParams),
  });

export const fetchBudgets = () => fetchWithError("/budgets");
export const createBudget = (data) =>
  fetchWithError("/budgets", { method: "POST", body: JSON.stringify(data) });
export const updateBudget = (id, data) =>
  fetchWithError(`/budgets/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
export const deleteBudget = (id) =>
  fetchWithError(`/budgets/${id}`, { method: "DELETE" });

export const fetchSavingsGoals = () => fetchWithError("/savings");
export const createSavingsGoal = (data) =>
  fetchWithError("/savings", { method: "POST", body: JSON.stringify(data) });
export const updateSavingsGoal = (id, data) =>
  fetchWithError(`/savings/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
export const deleteSavingsGoal = (id) =>
  fetchWithError(`/savings/${id}`, { method: "DELETE" });


  // Plaid functions
export const createLinkToken = () => fetchWithError("/create_link_token");

export const exchangePublicToken = (publicToken) =>
  fetchWithError("/exchange_public_token", {
    method: "POST",
    body: JSON.stringify({ public_token: publicToken }),
  });

// Grouped exports for convenience
export const api = {
  // Auth
  checkAuth,
  login,
  register,
  logout,

  // Transactions
  fetchTransactions,
  fetchAccountSummary,
  syncTransactions,

  // Forecast
  fetchForecast,

  // Plaid
  createLinkToken,
  exchangePublicToken,
};

export default api;
