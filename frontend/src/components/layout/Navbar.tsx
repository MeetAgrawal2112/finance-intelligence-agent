// src/components/layout/Navbar.tsx
import { useNavigate, useLocation } from 'react-router-dom'
import {
  TrendingUp, LayoutDashboard, CreditCard,
  Bell, TrendingDown, LogOut, User, Bot
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { useUnreadCount } from '../../hooks/useAlerts'
import { toast } from '../../store/toastStore'

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: CreditCard,      label: 'Transactions', path: '/transactions' },
  { icon: Bell,            label: 'Alerts', path: '/alerts', showBadge: true },
  { icon: TrendingDown,    label: 'Forecast', path: '/forecast' },
  { icon: Bot,             label: 'AI Chat', path: '/dashboard#chat' },
]

export default function Navbar() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const unreadCount = useUnreadCount()

  const handleLogout = async () => {
    await logout()
    toast.info('Logged out', 'Phir milenge! 👋')
    navigate('/login')
  }

  const isActive = (path: string) =>
    location.pathname === path.split('#')[0]

  return (
    <nav style={{
      background: 'white',
      borderBottom: '1px solid #e2e8f0',
      padding: '0 1.5rem',
      height: '64px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
    }}>

      {/* Logo */}
      <div
        style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', cursor: 'pointer' }}
        onClick={() => navigate('/dashboard')}
      >
        <div style={{
          width: '36px', height: '36px', background: '#0284c7',
          borderRadius: '0.625rem', display: 'flex',
          alignItems: 'center', justifyContent: 'center',
        }}>
          <TrendingUp size={20} color="white" />
        </div>
        <span style={{ fontWeight: 700, color: '#0f172a', fontSize: '0.95rem' }}>
          Finance Intelligence
        </span>
      </div>

      {/* Nav Links */}
      <div style={{ display: 'flex', gap: '0.25rem' }}>
        {NAV_ITEMS.map(({ icon: Icon, label, path, showBadge }) => {
          const active = isActive(path)
          return (
            <button
              key={label}
              onClick={() => navigate(path.split('#')[0])}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.375rem',
                padding: '0.5rem 0.75rem',
                border: 'none',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                fontSize: '0.875rem',
                background: active ? '#f0f9ff' : 'none',
                color: active ? '#0284c7' : '#64748b',
                fontWeight: active ? 600 : 400,
                position: 'relative',
                transition: 'all 0.15s',
              }}
            >
              <Icon size={15} />
              {label}
              {/* Alert Badge */}
              {showBadge && unreadCount > 0 && (
                <span style={{
                  position: 'absolute',
                  top: '4px',
                  right: '4px',
                  background: '#dc2626',
                  color: 'white',
                  borderRadius: '50%',
                  width: '17px',
                  height: '17px',
                  fontSize: '0.6rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 700,
                  border: '2px solid white',
                }}>
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* User Menu */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.375rem 0.875rem',
          background: '#f8fafc',
          borderRadius: '2rem',
          border: '1px solid #e2e8f0',
        }}>
          <div style={{
            width: '28px', height: '28px',
            background: '#0284c7', borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <User size={14} color="white" />
          </div>
          <span style={{ fontSize: '0.875rem', fontWeight: 500, color: '#374151' }}>
            {user?.full_name?.split(' ')[0]}
          </span>
        </div>
        <button
          onClick={handleLogout}
          className="btn-secondary"
          style={{
            display: 'flex', alignItems: 'center',
            gap: '0.375rem', fontSize: '0.875rem',
            padding: '0.5rem 0.875rem',
          }}
        >
          <LogOut size={14} /> Logout
        </button>
      </div>
    </nav>
  )
}