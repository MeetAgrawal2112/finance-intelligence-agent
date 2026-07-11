// src/hooks/useAlerts.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { alertsApi } from '../api/alerts'
import { toast } from '../store/toastStore'

export function useAlerts(isRead?: boolean) {
  return useQuery({
    queryKey: ['alerts', isRead],
    queryFn: () => alertsApi.list({ is_read: isRead }),
    refetchInterval: 30000, // Har 30 sec mein refresh
  })
}

export function useUnreadCount() {
  const { data } = useAlerts(false)
  return data?.data?.total_unread || 0
}

export function useMarkRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: alertsApi.markRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    }
  })
}

export function useMarkResolved() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: alertsApi.markResolved,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      toast.success('Alert resolved!')
    }
  })
}

export function useMarkAllRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: alertsApi.markAllRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      toast.success('All alerts marked as read')
    }
  })
}