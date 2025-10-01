"use client"

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react"
import axios from "axios"
import { authService, type LoginCredentials, type User } from "@shared/services/auth-service"
import { tokenStorage } from "@shared/utils/token-storage"
import { env } from "@shared/utils/env"

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: LoginCredentials, rememberMe?: boolean) => Promise<void>
  logout: () => void
  refreshAccessToken: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Create axios instance for authenticated API calls
export const api = axios.create({
  baseURL: env.API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [refreshTimer, setRefreshTimer] = useState<NodeJS.Timeout | null>(null)

  /**
   * Setup axios interceptor to attach access token to requests
   */
  useEffect(() => {
    const requestInterceptor = api.interceptors.request.use(
      (config) => {
        const token = tokenStorage.getAccessToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    const responseInterceptor = api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        // If 401 and we haven't retried yet, try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            await refreshAccessToken()
            const newToken = tokenStorage.getAccessToken()
            if (newToken) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`
              return api(originalRequest)
            }
          } catch (refreshError) {
            // Refresh failed, logout user
            logout()
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )

    return () => {
      api.interceptors.request.eject(requestInterceptor)
      api.interceptors.response.eject(responseInterceptor)
    }
  }, [])

  /**
   * Refresh access token using refresh token
   */
  const refreshAccessToken = useCallback(async () => {
    const refreshToken = tokenStorage.getRefreshToken()
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    try {
      const newAccessToken = await authService.refreshToken(refreshToken)
      tokenStorage.setAccessToken(newAccessToken)

      // Update user info from new token
      const userInfo = authService.decodeToken(newAccessToken)
      if (userInfo) {
        setUser(userInfo)
      }

      // Schedule next refresh
      scheduleTokenRefresh(newAccessToken)
    } catch (error) {
      console.error('Failed to refresh token:', error)
      throw error
    }
  }, [])

  /**
   * Schedule automatic token refresh before expiry
   */
  const scheduleTokenRefresh = useCallback((token: string) => {
    // Clear existing timer
    if (refreshTimer) {
      clearTimeout(refreshTimer)
    }

    // Extract expiry time from token
    try {
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      )
      const payload = JSON.parse(jsonPayload)
      const exp = payload.exp * 1000 // Convert to milliseconds
      const now = Date.now()
      const refreshTime = exp - now - 60000 // Refresh 1 minute before expiry

      if (refreshTime > 0) {
        const timer = setTimeout(() => {
          refreshAccessToken()
        }, refreshTime)
        setRefreshTimer(timer)
      }
    } catch (error) {
      console.error('Failed to schedule token refresh:', error)
    }
  }, [refreshTimer, refreshAccessToken])

  /**
   * Initialize auth state from stored tokens
   */
  useEffect(() => {
    const initAuth = async () => {
      const accessToken = tokenStorage.getAccessToken()
      const refreshToken = tokenStorage.getRefreshToken()

      if (accessToken && refreshToken) {
        // Check if access token is still valid
        if (authService.isTokenExpiringSoon(accessToken)) {
          // Try to refresh
          try {
            await refreshAccessToken()
          } catch (error) {
            console.error('Failed to refresh token on init:', error)
            tokenStorage.clearTokens()
          }
        } else {
          // Token is still valid
          const userInfo = authService.decodeToken(accessToken)
          if (userInfo) {
            setUser(userInfo)
            scheduleTokenRefresh(accessToken)
          }
        }
      }

      setIsLoading(false)
    }

    initAuth()

    // Cleanup timer on unmount
    return () => {
      if (refreshTimer) {
        clearTimeout(refreshTimer)
      }
    }
  }, [])

  /**
   * Login user
   */
  const login = async (credentials: LoginCredentials, rememberMe = false) => {
    try {
      const tokens = await authService.login(credentials)
      tokenStorage.setTokens(tokens, rememberMe)

      const userInfo = authService.decodeToken(tokens.access)
      if (userInfo) {
        setUser(userInfo)
      }

      // Schedule token refresh
      scheduleTokenRefresh(tokens.access)
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  /**
   * Logout user
   */
  const logout = useCallback(() => {
    authService.logout()
    setUser(null)
    if (refreshTimer) {
      clearTimeout(refreshTimer)
      setRefreshTimer(null)
    }
  }, [refreshTimer])

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    refreshAccessToken,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Export api instance for use in other services
export { api as authenticatedApi }
