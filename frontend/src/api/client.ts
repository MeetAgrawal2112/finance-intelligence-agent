// src/api/client.ts
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Main axios instance
export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds
})

// Request interceptor — har request mein token add karo
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor — token expire hone pe auto refresh
apiClient.interceptors.response.use(
  // Success — as is return karo
  (response) => response,

  // Error handling
  async (error) => {
    const originalRequest = error.config

    // 401 aaya aur retry nahi kiya abhi tak
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          // Naya access token lo
          const response = await axios.post(
            `${API_BASE_URL}/api/v1/auth/refresh`,
            { refresh_token: refreshToken }
          )

          const { access_token } = response.data.data
          localStorage.setItem('access_token', access_token)

          // Original request retry karo naye token ke saath
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)

        } catch (refreshError) {
          // Refresh bhi fail hua — logout karo
          localStorage.clear()
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token — login page pe bhejo
        localStorage.clear()
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)