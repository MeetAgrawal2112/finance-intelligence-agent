// src/store/authStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '../types'
import { authApi } from '../api/auth'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean

  // Actions
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  setUser: (user: User) => void
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email, password) => {
        set({ isLoading: true })
        try {
          const response = await authApi.login(email, password)
          const tokens = response.data!
          set({
            user: tokens.user,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: async () => {
        await authApi.logout()
        set({ user: null, isAuthenticated: false })
      },

      setUser: (user) => set({ user }),

      checkAuth: async () => {
        const token = localStorage.getItem('access_token')
        if (!token) {
          set({ isAuthenticated: false, user: null })
          return
        }
        try {
          const response = await authApi.getMe()
          set({ user: response.data!, isAuthenticated: true })
        } catch {
          set({ isAuthenticated: false, user: null })
          localStorage.clear()
        }
      },
    }),
    {
      name: 'auth-storage',
      // Sirf yeh fields persist karo
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)