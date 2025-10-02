/**
 * Authenticated API client for admin operations
 * Includes JWT token in Authorization headers and handles token refresh
 */

import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';
import { env } from '@shared/utils/env';
import { tokenStorage } from '@shared/utils/token-storage';
import { authService } from '@shared/services/auth-service';

/**
 * Create authenticated axios instance for admin operations
 */
const createAdminApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: env.API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor to add auth token
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const accessToken = tokenStorage.getAccessToken();
      if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor to handle token refresh
  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      // If 401 and we haven't retried yet, try to refresh token
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        const refreshToken = tokenStorage.getRefreshToken();
        if (refreshToken) {
          try {
            const newAccessToken = await authService.refreshToken(refreshToken);
            tokenStorage.setAccessToken(newAccessToken);
            // Update the refresh token in storage in case it was rotated
            tokenStorage.setTokens({
              access: newAccessToken,
              refresh: refreshToken,
            }, tokenStorage.isRememberMeEnabled());

            // Retry the original request with new token
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return client(originalRequest);
          } catch (refreshError) {
            // Refresh failed, logout user
            authService.logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        } else {
          // No refresh token, redirect to login
          authService.logout();
          window.location.href = '/login';
        }
      }

      return Promise.reject(error);
    }
  );

  return client;
};

export const adminApiClient = createAdminApiClient();
