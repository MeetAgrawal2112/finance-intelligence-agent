// src/components/ui/Toast.tsx
import { useEffect, useState } from 'react'
import { useToastStore, type Toast } from '../../store/toastStore'
import {
  CheckCircle, XCircle, AlertTriangle,
  Info, X
} from 'lucide-react'

// Single toast card
function ToastCard({ toast }: { toast: Toast }) {
  const { removeToast } = useToastStore()
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    // Slide in
    const timer = setTimeout(() => setVisible(true), 10)
    return () => clearTimeout(timer)
  }, [])

  const handleRemove = () => {
    setVisible(false)
    setTimeout(() => removeToast(toast.id), 300)
  }

  const styles = {
    success: {
      bg: '#f0fdf4',
      border: '#86efac',
      icon: <CheckCircle className="w-5 h-5 text-green-500 shrink-0" />,
      title: '#15803d',
    },
    error: {
      bg: '#fff1f2',
      border: '#fca5a5',
      icon: <XCircle className="w-5 h-5 text-red-500 shrink-0" />,
      title: '#dc2626',
    },
    warning: {
      bg: '#fffbeb',
      border: '#fcd34d',
      icon: <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />,
      title: '#d97706',
    },
    info: {
      bg: '#f0f9ff',
      border: '#7dd3fc',
      icon: <Info className="w-5 h-5 text-sky-500 shrink-0" />,
      title: '#0284c7',
    },
  }

  const s = styles[toast.type]

  return (
    <div
      style={{
        background: s.bg,
        border: `1px solid ${s.border}`,
        borderRadius: '0.75rem',
        padding: '0.875rem 1rem',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '0.75rem',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        minWidth: '300px',
        maxWidth: '400px',
        transform: visible ? 'translateX(0)' : 'translateX(120%)',
        opacity: visible ? 1 : 0,
        transition: 'all 0.3s ease',
      }}
    >
      {s.icon}
      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{
          color: s.title,
          fontWeight: 600,
          fontSize: '0.875rem',
          margin: 0,
        }}>
          {toast.title}
        </p>
        {toast.message && (
          <p style={{
            color: '#64748b',
            fontSize: '0.8rem',
            margin: '2px 0 0',
          }}>
            {toast.message}
          </p>
        )}
      </div>
      <button
        onClick={handleRemove}
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: '2px',
          color: '#94a3b8',
          lineHeight: 1,
        }}
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}

// Toast container — screen ke top-right corner mein
export default function ToastContainer() {
  const { toasts } = useToastStore()

  return (
    <div style={{
      position: 'fixed',
      top: '1.25rem',
      right: '1.25rem',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      gap: '0.5rem',
    }}>
      {toasts.map((t) => (
        <ToastCard key={t.id} toast={t} />
      ))}
    </div>
  )
}