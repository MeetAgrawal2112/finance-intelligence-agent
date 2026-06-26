// src/store/toastStore.ts
import { create } from 'zustand'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: string
  type: ToastType
  title: string
  message?: string
  duration?: number  // milliseconds — default 4000
}

interface ToastState {
  toasts: Toast[]
  addToast: (toast: Omit<Toast, 'id'>) => void
  removeToast: (id: string) => void
  clearAll: () => void
}

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],

  addToast: (toast) => {
    const id = Math.random().toString(36).substring(2)
    const duration = toast.duration ?? 4000

    set((state) => ({
      toasts: [...state.toasts, { ...toast, id }]
    }))

    // Auto remove after duration
    setTimeout(() => {
      set((state) => ({
        toasts: state.toasts.filter((t) => t.id !== id)
      }))
    }, duration)
  },

  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id)
    }))
  },

  clearAll: () => set({ toasts: [] }),
}))

// Helper functions — poori app mein easy use ke liye
export const toast = {
  success: (title: string, message?: string) =>
    useToastStore.getState().addToast({ type: 'success', title, message }),

  error: (title: string, message?: string) =>
    useToastStore.getState().addToast({ type: 'error', title, message }),

  warning: (title: string, message?: string) =>
    useToastStore.getState().addToast({ type: 'warning', title, message }),

  info: (title: string, message?: string) =>
    useToastStore.getState().addToast({ type: 'info', title, message }),
}