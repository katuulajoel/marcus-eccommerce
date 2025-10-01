/**
 * Authentication service for handling login, token refresh, and logout
 */

import axios from 'axios';
import { env } from '@shared/utils/env';
import { tokenStorage, type AuthTokens } from '@shared/utils/token-storage';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
}

export interface RefreshResponse {
  access: string;
}

export interface User {
  username: string;
  userId?: string;
}

// Create axios instance for auth endpoints (no auth headers needed)
const authApi = axios.create({
  baseURL: env.API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Authentication service
 */
export const authService = {
  /**
   * Login user with username and password
   */
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const response = await authApi.post<LoginResponse>('/api/token/', credentials);
    return {
      access: response.data.access,
      refresh: response.data.refresh,
    };
  },

  /**
   * Refresh access token using refresh token
   */
  refreshToken: async (refreshToken: string): Promise<string> => {
    const response = await authApi.post<RefreshResponse>('/api/token/refresh/', {
      refresh: refreshToken,
    });
    return response.data.access;
  },

  /**
   * Logout user (client-side token cleanup)
   */
  logout: (): void => {
    tokenStorage.clearTokens();
  },

  /**
   * Decode JWT token to extract user information
   * Note: This is a basic decode, not verification (verification happens on backend)
   */
  decodeToken: (token: string): User | null => {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );

      const payload = JSON.parse(jsonPayload);
      return {
        username: payload.username || 'Admin User',
        userId: payload.user_id?.toString(),
      };
    } catch (error) {
      console.error('Failed to decode token:', error);
      return null;
    }
  },

  /**
   * Check if access token is expired or about to expire
   * Returns true if token will expire in less than 1 minute
   */
  isTokenExpiringSoon: (token: string): boolean => {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );

      const payload = JSON.parse(jsonPayload);
      const exp = payload.exp * 1000; // Convert to milliseconds
      const now = Date.now();
      const oneMinute = 60 * 1000;

      return exp - now < oneMinute;
    } catch (error) {
      return true; // If we can't decode, assume it's expired
    }
  },
};
