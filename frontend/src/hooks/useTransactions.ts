// src/hooks/useTransactions.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { transactionsApi } from '../api/transactions'
import type { TransactionFilters } from '../types'
import { toast } from '../store/toastStore'

export function useTransactions(filters: TransactionFilters = {}) {
  return useQuery({
    queryKey: ['transactions', filters],
    queryFn: () => transactionsApi.list(filters),
    staleTime: 2 * 60 * 1000,
  })
}

export function useCreateTransaction() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: transactionsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['monthly-summary'] })
      queryClient.invalidateQueries({ queryKey: ['category-analytics'] })
      toast.success('Transaction added!', 'Successfully saved.')
    },
    onError: (err: any) => {
      toast.error('Failed', err.response?.data?.detail || 'Try again.')
    }
  })
}

export function useDeleteTransaction() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: transactionsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['monthly-summary'] })
      toast.success('Deleted!', 'Transaction removed.')
    },
  })
}

export function useImportCSV() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: transactionsApi.importCSV,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['monthly-summary'] })
      const imported = data?.data?.imported || 0
      toast.success('Import complete!', `${imported} transactions added.`)
    },
    onError: () => toast.error('Import failed', 'Check CSV format.')
  })
}