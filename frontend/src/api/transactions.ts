// src/api/transactions.ts
import { apiClient } from './client'
import type {
  ApiResponse, Transaction, MonthlySummary,
  CategoryAnalytics, TransactionFilters
} from '../types'

export const transactionsApi = {
  list: async (filters: TransactionFilters = {}) => {
    const res = await apiClient.get('/transactions', { params: filters })
    return res.data
  },

  create: async (data: Partial<Transaction>) => {
    const res = await apiClient.post<ApiResponse<Transaction>>(
      '/transactions', data
    )
    return res.data
  },

  update: async (id: string, data: Partial<Transaction>) => {
    const res = await apiClient.put<ApiResponse<Transaction>>(
      `/transactions/${id}`, data
    )
    return res.data
  },

  delete: async (id: string) => {
    const res = await apiClient.delete(`/transactions/${id}`)
    return res.data
  },

  importCSV: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post('/transactions/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return res.data
  },

  getMonthlySummary: async (month: number, year: number) => {
    const res = await apiClient.get<ApiResponse<MonthlySummary>>(
      '/transactions/summary',
      { params: { month, year } }
    )
    return res.data
  },

  getAnalytics: async (month?: number, year?: number) => {
    const res = await apiClient.get('/transactions/analytics', {
      params: { month, year }
    })
    return res.data
  },
}