import axios from 'axios';
import { debugLog } from './debug';

interface PlaidLinkResponse {
  link_token: string;
}

interface TransactionSyncResponse {
  message: string;
  new_transactions: number;
}

interface DashboardSummary {
  total_income: number;
  total_expenses: number;
  net_balance: number;
  recent_transactions: Array<{
    id: string;
    date: string;
    name: string;
    amount: number;
    category?: string;
    merchant_name?: string;
  }>;
  ai_insights: string | null;
}

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request/response interceptors for debugging
api.interceptors.request.use(
  (config) => {
    debugLog.request(config.url!, config.method!, config.data);
    return config;
  },
  (error) => {
    debugLog.error(error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    debugLog.response(response);
    return response.data;
  },
  (error) => {
    debugLog.error(error);
    return Promise.reject(error);
  }
);

export const plaidApi = {
  getLinkToken: async (): Promise<PlaidLinkResponse> => {
    try {
      const response = await api.get<PlaidLinkResponse>('/plaid/create_link_token');
      return response;
    } catch (error) {
      console.error('Error getting link token:', error);
      throw error;
    }
  },

  exchangePublicToken: async (publicToken: string): Promise<{ success: boolean }> => {
    try {
      const response = await api.post<{ success: boolean }>('/plaid/exchange_public_token', {
        public_token: publicToken,
      });
      return response;
    } catch (error) {
      console.error('Error exchanging public token:', error);
      throw error;
    }
  },

  syncTransactions: async (): Promise<TransactionSyncResponse> => {
    try {
      const response = await api.post<TransactionSyncResponse>('/transactions/sync');
      return response;
    } catch (error) {
      console.error('Error syncing transactions:', error);
      throw error;
    }
  },

  getDashboardData: async (): Promise<DashboardSummary> => {
    try {
      const response = await api.get<DashboardSummary>('/transactions/insights');
      return response;
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }
};