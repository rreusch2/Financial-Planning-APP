export interface User {
  id: number;
  username: string;
  email: string;
  has_plaid_connection: boolean;
}

export interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

export interface LoginResponse {
  success: boolean;
  user: User;
}