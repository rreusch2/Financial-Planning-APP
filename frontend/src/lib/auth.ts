import axios, { AxiosError } from 'axios';
import { User } from '../types/auth';
import { debugLog } from './debug';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor
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

// Add response interceptor
api.interceptors.response.use(
  (response) => {
    debugLog.response(response);
    return response;
  },
  (error) => {
    debugLog.error(error);
    if (error.response?.status === 401) {
      // Handle unauthorized access
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export class AuthService {
  private static instance: AuthService;

  private constructor() { }

  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  async login(username: string, password: string): Promise<{ user: User }> {
    try {
      const response = await api.post('/auth/login', { username, password });
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        if (!error.response) {
          throw new Error('Network error - Unable to reach the server');
        }
        throw new Error(error.response.data.error || 'Login failed');
      }
      throw error;
    }
  }

  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  }

  async getCurrentUser(): Promise<{ user: User } | null> {
    try {
      const response = await api.get('/auth/current_user');
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError && error.response?.status === 401) {
        return null;
      }
      console.error('Get current user error:', error);
      return null;
    }
  }
}