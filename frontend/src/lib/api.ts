import axios from 'axios';
import config from './config';

const api = axios.create({
  baseURL: config.apiUrl,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const auth = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/auth/login', credentials),
  register: (userData: { username: string; email: string; password: string }) =>
    api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/user'),
};

export const plaid = {
  getLinkToken: () => api.post('/plaid/create_link_token'),
  setAccessToken: (publicToken: string) =>
    api.post('/plaid/set_access_token', { public_token: publicToken }),
  checkConnection: () => api.get('/plaid/check_connection'),
};

export const transactions = {
  getRecent: () => api.get('/transactions/recent'),
  getAll: (params?: {
    page?: number;
    per_page?: number;
    start_date?: string;
    end_date?: string;
  }) => api.get('/transactions', { params }),
  sync: () => api.post('/transactions/sync'),
};

export const dashboard = {
  getSummary: () => api.get('/dashboard/summary'),
  getChartData: () => api.get('/dashboard/chart_data'),
  getDashboardData: () => api.get('/dashboard/data'),
};

export const aiServices = {
  getAdvice: () => api.get('/ai/advice'),
  analyzeSentiment: (description: string) =>
    api.post('/ai/analyze_sentiment', { description }),
  getCategoryAnalysis: (category: string) =>
    api.get('/ai/category_analysis', { params: { category } }),
  getTransactionInsights: (transactionId: string) =>
    api.post('/ai/transaction_insights', { transaction_id: transactionId }),
  getSpendingForecast: () => api.get('/ai/spending_forecast'),
};

export default {
  auth,
  plaid,
  transactions,
  dashboard,
  aiServices,
};