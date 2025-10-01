/**
 * Token storage utility for managing authentication tokens
 * Provides secure storage and retrieval of access and refresh tokens
 */

export interface AuthTokens {
  access: string;
  refresh: string;
}

const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const REMEMBER_ME_KEY = 'remember_me';

/**
 * Store tokens in appropriate storage based on "remember me" preference
 * Access token: Always in memory (sessionStorage) for security
 * Refresh token: localStorage if remember me is true, otherwise sessionStorage
 */
export const tokenStorage = {
  /**
   * Save tokens to storage
   */
  setTokens: (tokens: AuthTokens, rememberMe: boolean = false): void => {
    // Store access token in sessionStorage (cleared when browser closes)
    sessionStorage.setItem(ACCESS_TOKEN_KEY, tokens.access);

    // Store remember me preference
    const storage = rememberMe ? localStorage : sessionStorage;
    storage.setItem(REMEMBER_ME_KEY, rememberMe.toString());

    // Store refresh token based on remember me preference
    if (rememberMe) {
      localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
      sessionStorage.removeItem(REFRESH_TOKEN_KEY);
    } else {
      sessionStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
    }
  },

  /**
   * Get access token from storage
   */
  getAccessToken: (): string | null => {
    return sessionStorage.getItem(ACCESS_TOKEN_KEY);
  },

  /**
   * Get refresh token from storage (checks both localStorage and sessionStorage)
   */
  getRefreshToken: (): string | null => {
    return localStorage.getItem(REFRESH_TOKEN_KEY) || sessionStorage.getItem(REFRESH_TOKEN_KEY);
  },

  /**
   * Update only the access token (used after refresh)
   */
  setAccessToken: (accessToken: string): void => {
    sessionStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  },

  /**
   * Clear all tokens from storage
   */
  clearTokens: (): void => {
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(REFRESH_TOKEN_KEY);
    sessionStorage.removeItem(REMEMBER_ME_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(REMEMBER_ME_KEY);
  },

  /**
   * Check if remember me is enabled
   */
  isRememberMeEnabled: (): boolean => {
    const rememberMe = localStorage.getItem(REMEMBER_ME_KEY) || sessionStorage.getItem(REMEMBER_ME_KEY);
    return rememberMe === 'true';
  },

  /**
   * Check if user has valid tokens (at least refresh token exists)
   */
  hasTokens: (): boolean => {
    return !!tokenStorage.getRefreshToken();
  }
};
