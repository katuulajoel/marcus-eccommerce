"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import axios from "axios"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  customer?: {
    id: number
    name: string
    phone: string
    email_verified: boolean
  }
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  register: (data: RegisterData) => Promise<void>
  isAuthenticated: boolean
}

interface RegisterData {
  username: string
  email: string
  password: string
  password2: string
  name: string
  phone?: string
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Axios instance with interceptor for token management
export const axiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
})

// Request interceptor to add token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("accessToken")
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// Response interceptor to handle token refresh
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem("refreshToken")
        if (!refreshToken) {
          throw new Error("No refresh token")
        }

        // Try to refresh token
        const response = await axios.post(`${API_BASE_URL}/api/auth/refresh/`, {
          refresh: refreshToken,
        })

        const { access } = response.data
        localStorage.setItem("accessToken", access)

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`
        return axiosInstance(originalRequest)
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem("accessToken")
        localStorage.removeItem("refreshToken")
        window.location.href = "/login"
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  },
)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Load user on mount if token exists
  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem("accessToken")
      if (token) {
        try {
          const response = await axiosInstance.get("/auth/me/")
          setUser(response.data)
        } catch (error) {
          console.error("Failed to load user:", error)
          localStorage.removeItem("accessToken")
          localStorage.removeItem("refreshToken")
        }
      }
      setLoading(false)
    }

    loadUser()
  }, [])

  const login = async (username: string, password: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/login/`, {
        username,
        password,
      })

      const { access, refresh, user: userData } = response.data

      localStorage.setItem("accessToken", access)
      localStorage.setItem("refreshToken", refresh)
      setUser(userData)
    } catch (error: any) {
      throw new Error(error.response?.data?.error || "Login failed")
    }
  }

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem("refreshToken")
      if (refreshToken) {
        await axiosInstance.post("/auth/logout/", { refresh: refreshToken })
      }
    } catch (error) {
      console.error("Logout error:", error)
    } finally {
      localStorage.removeItem("accessToken")
      localStorage.removeItem("refreshToken")
      setUser(null)
    }
  }

  const register = async (data: RegisterData) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/register/`, data)

      // Auto-login after registration
      await login(data.username, data.password)
    } catch (error: any) {
      const errorData = error.response?.data
      if (errorData) {
        // Format validation errors
        const errors = Object.entries(errorData)
          .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : value}`)
          .join("\n")
        throw new Error(errors || "Registration failed")
      }
      throw new Error("Registration failed")
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        register,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
