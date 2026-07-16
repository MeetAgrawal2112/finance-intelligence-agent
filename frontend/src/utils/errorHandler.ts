import { toast } from '../store/toastStore'

export function handleApiError(error: any, fallback = 'Kuch gadbad ho gayi'): string {
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