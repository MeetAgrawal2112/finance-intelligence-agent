// src/api/auth.ts
import { apiClient } from './client'
import type { ApiResponse, AuthTokens, User } from '../types'

export const authApi = {
  register: async (data: {
    email: string
    full_name: string
    password: string
    currency?: string
  }) => {
    const res = await apiClient.post<ApiResponse<User>>('/auth/register', data)
    return res.data
  },

  login: async (email: string, password: string) => {
    const res = await apiClient.post<ApiResponse<AuthTokens>>('/auth/login', {
      email,
      password,
    })
    // Tokens localStorage mein save karo
    const tokens = res.data.data!
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
    return res.data
  },

  logout: async () => {
    try {
      await apiClient.post('/auth/logout')
    } finally {
      localStorage.clear()
    }
  },

  getMe: async () => {
    const res = await apiClient.get<ApiResponse<User>>('/auth/me')
    return res.data
  },

  updateProfile: async (data: Partial<User>) => {
    const res = await apiClient.put<ApiResponse<User>>('/auth/me', data)
    return res.data
  },
}