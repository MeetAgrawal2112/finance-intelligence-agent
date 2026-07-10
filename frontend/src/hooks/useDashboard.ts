// src/hooks/useDashboard.ts
import { useQuery } from '@tanstack/react-query'
import { transactionsApi } from '../api/transactions'

export function useMonthlySummary(month: number, year: number) {
  return useQuery({
    queryKey: ['monthly-summary', month, year],
    queryFn: () => transactionsApi.getMonthlySummary(month, year),
    staleTime: 5 * 60 * 1000,  // 5 minutes
  })
}

export function useCategoryAnalytics(month?: number, year?: number) {
  return useQuery({
    queryKey: ['category-analytics', month, year],
    queryFn: () => transactionsApi.getAnalytics(month, year),
    staleTime: 15 * 60 * 1000, // 15 minutes
  })
}

export function useSpendingForecast() {
  return useQuery({
    queryKey: ['spending-forecast'],
    queryFn: async () => {
      const { apiClient } = await import('../api/client')
      const res = await apiClient.get('/ml/forecast')
      return res.data
    },
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}