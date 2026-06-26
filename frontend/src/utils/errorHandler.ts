// src/utils/errorHandler.ts
import { toast } from '../store/toastStore'

/**
 * API errors ko handle karo aur user-friendly
 * toast messages dikhao.
 */
export function handleApiError(error: any, fallback = 'Kuch gadbad ho gayi'): string {
  // Network error — backend chal nahi raha
  if (!error.response) {
    const msg = 'Server se connect nahi ho pa raha. Backend chal raha hai?'
    toast.error('Connection Error', msg)
    return msg
  }

  const status = error.response.status
  const detail = error.response.data?.detail

  const messages: Record<number, string> = {
    400: detail || 'Invalid request',
    401: 'Session expire ho gayi. Please login karo.',
    403: 'Tumhare paas permission nahi hai.',
    404: 'Data nahi mila.',
    422: 'Invalid data bheja. Please check karo.',
    429: 'Bahut zyada requests. Thoda ruko.',
    500: 'Server error. Baad mein try karo.',
  }

  const msg = messages[status] || detail || fallback
  toast.error(`Error ${status}`, msg)
  return msg
}