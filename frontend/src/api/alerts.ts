// src/api/alerts.ts
import { apiClient } from './client'

export const alertsApi = {
  list: async (params: { is_read?: boolean; limit?: number } = {}) => {
    const res = await apiClient.get('/alerts', { params })
    return res.data
  },

  markRead: async (id: string) => {
    const res = await apiClient.put(`/alerts/${id}/read`)
    return res.data
  },

  markResolved: async (id: string) => {
    const res = await apiClient.put(`/alerts/${id}/resolve`)
    return res.data
  },

  markAllRead: async () => {
    const res = await apiClient.put('/alerts/read-all')
    return res.data
  },

  getStats: async () => {
    const res = await apiClient.get('/ml/anomaly-stats')
    return res.data
  },
}