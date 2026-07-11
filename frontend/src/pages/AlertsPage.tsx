// src/pages/AlertsPage.tsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  TrendingUp, Bell, AlertTriangle, CheckCircle,
  Shield, LogOut, LayoutDashboard, CreditCard,
  Bot, Eye, Check, CheckCheck, Info
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import {
  useAlerts, useMarkRead,
  useMarkResolved, useMarkAllRead
} from '../hooks/useAlerts'
import { format } from 'date-fns'

const SEVERITY_CONFIG = {
  high: {
    color: '#dc2626', bg: '#fff1f2',
    border: '#fca5a5', icon: <AlertTriangle size={16} />,
    label: 'High Risk'
  },
  medium: {
    color: '#d97706', bg: '#fffbeb',
    border: '#fcd34d', icon: <AlertTriangle size={16} />,
    label: 'Medium Risk'
  },
  low: {
    color: '#0284c7', bg: '#f0f9ff',
    border: '#7dd3fc', icon: <Info size={16} />,
    label: 'Low Risk'
  },
}

const TYPE_LABELS: Record<string, string> = {
  anomaly: '🚨 Anomaly',
  budget_warning: '⚠️ Budget Warning',
  budget_exceeded: '🔴 Budget Exceeded',
  large_transaction: '💸 Large Transaction',
  duplicate: '🔄 Duplicate',
}

export default function AlertsPage() {
  const { logout } = useAuthStore()
  const navigate = useNavigate()
  const [filter, setFilter] = useState<'all' | 'unread' | 'resolved'>('all')

  const { data, isLoading } = useAlerts(
    filter === 'unread' ? false : undefined
  )
  const markRead = useMarkRead()
  const markResolved = useMarkResolved()
  const markAllRead = useMarkAllRead()

  const alerts = data?.data?.alerts || []
  const unreadCount = data?.data?.total_unread || 0

  const filteredAlerts = alerts.filter((a: any) => {
    if (filter === 'resolved') return a.is_resolved
    if (filter === 'unread') return !a.is_read
    return true
  })

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>

      {/* Content */}
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '2rem 1.5rem' }}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
              Alerts & Anomalies
            </h1>
            <p style={{ color: '#64748b', margin: '0.25rem 0 0', fontSize: '0.875rem' }}>
              {unreadCount} unread alerts
            </p>
          </div>
          {unreadCount > 0 && (
            <button
              onClick={() => markAllRead.mutate()}
              disabled={markAllRead.isPending}
              className="btn-secondary"
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}
            >
              <CheckCheck size={15} /> Mark All Read
            </button>
          )}
        </div>

        {/* Stats Row */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '1rem',
          marginBottom: '1.5rem',
        }}>
          {[
            {
              label: 'Total Alerts',
              value: alerts.length,
              icon: <Bell size={20} />,
              color: '#7c3aed', bg: '#faf5ff'
            },
            {
              label: 'Unread',
              value: unreadCount,
              icon: <AlertTriangle size={20} />,
              color: '#dc2626', bg: '#fff1f2'
            },
            {
              label: 'Resolved',
              value: alerts.filter((a: any) => a.is_resolved).length,
              icon: <Shield size={20} />,
              color: '#16a34a', bg: '#f0fdf4'
            },
          ].map(stat => (
            <div key={stat.label} className="card" style={{ padding: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <p style={{ margin: 0, fontSize: '0.75rem', color: '#64748b', fontWeight: 500 }}>
                    {stat.label}
                  </p>
                  <p style={{ margin: '0.25rem 0 0', fontSize: '1.75rem', fontWeight: 700, color: stat.color }}>
                    {stat.value}
                  </p>
                </div>
                <div style={{
                  width: '44px', height: '44px', background: stat.bg,
                  borderRadius: '0.75rem', display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                  color: stat.color,
                }}>
                  {stat.icon}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Filter Tabs */}
        <div style={{ display: 'flex', gap: '0.375rem', marginBottom: '1rem' }}>
          {(['all', 'unread', 'resolved'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              style={{
                padding: '0.5rem 1rem', border: 'none',
                borderRadius: '2rem', cursor: 'pointer',
                fontSize: '0.8rem', fontWeight: filter === f ? 600 : 400,
                background: filter === f ? '#0284c7' : '#f1f5f9',
                color: filter === f ? 'white' : '#64748b',
              }}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
              {f === 'unread' && unreadCount > 0 && (
                <span style={{
                  marginLeft: '0.375rem', background: filter === f ? 'rgba(255,255,255,0.3)' : '#dc2626',
                  color: 'white', borderRadius: '50%',
                  padding: '0 4px', fontSize: '0.7rem',
                }}>
                  {unreadCount}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Alerts List */}
        {isLoading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {[1,2,3].map(i => (
              <div key={i} className="card" style={{
                height: '100px',
                animation: 'pulse 1.5s infinite'
              }} />
            ))}
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '4rem' }}>
            <Shield size={48} color="#86efac" style={{ margin: '0 auto 1rem' }} />
            <h3 style={{ color: '#0f172a', margin: '0 0 0.5rem' }}>
              Sab safe hai! ✅
            </h3>
            <p style={{ color: '#64748b', margin: 0 }}>
              {filter === 'unread'
                ? 'Koi unread alerts nahi hain.'
                : 'Koi alerts nahi hain.'}
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {filteredAlerts.map((alert: any) => {
              const sev = SEVERITY_CONFIG[alert.severity as keyof typeof SEVERITY_CONFIG]
              || SEVERITY_CONFIG.low

              return (
                <div
                  key={alert.id}
                  className="card"
                  style={{
                    padding: '1rem 1.25rem',
                    borderLeft: `4px solid ${sev.color}`,
                    opacity: alert.is_resolved ? 0.7 : 1,
                    background: alert.is_read ? 'white' : sev.bg,
                  }}
                >
                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>

                    {/* Icon */}
                    <div style={{
                      width: '36px', height: '36px', flexShrink: 0,
                      background: sev.bg, borderRadius: '0.5rem',
                      display: 'flex', alignItems: 'center',
                      justifyContent: 'center', color: sev.color,
                      border: `1px solid ${sev.border}`,
                    }}>
                      {sev.icon}
                    </div>

                    {/* Content */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                        <span style={{
                          fontSize: '0.7rem', fontWeight: 600,
                          color: sev.color, background: sev.bg,
                          padding: '0.15rem 0.5rem', borderRadius: '2rem',
                          border: `1px solid ${sev.border}`,
                        }}>
                          {sev.label}
                        </span>
                        <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
                          {TYPE_LABELS[alert.alert_type] || alert.alert_type}
                        </span>
                        {!alert.is_read && (
                          <span style={{
                            width: '8px', height: '8px', background: '#0284c7',
                            borderRadius: '50%', display: 'inline-block',
                          }} />
                        )}
                      </div>

                      <h3 style={{
                        margin: '0 0 0.25rem', fontSize: '0.9rem',
                        fontWeight: 600, color: '#0f172a',
                      }}>
                        {alert.title}
                      </h3>

                      <p style={{
                        margin: '0 0 0.5rem', fontSize: '0.8rem',
                        color: '#64748b', lineHeight: 1.5,
                        whiteSpace: 'pre-line',
                      }}>
                        {alert.message}
                      </p>

                      <p style={{ margin: 0, fontSize: '0.7rem', color: '#94a3b8' }}>
                        {format(new Date(alert.created_at), 'dd MMM yyyy, HH:mm')}
                      </p>
                    </div>

                    {/* Actions */}
                    <div style={{ display: 'flex', gap: '0.375rem', flexShrink: 0 }}>
                      {!alert.is_read && (
                        <button
                          onClick={() => markRead.mutate(alert.id)}
                          style={{
                            background: '#f0f9ff', border: '1px solid #bae6fd',
                            borderRadius: '0.5rem', padding: '0.375rem 0.625rem',
                            cursor: 'pointer', color: '#0284c7',
                            fontSize: '0.75rem', display: 'flex',
                            alignItems: 'center', gap: '0.25rem',
                          }}
                        >
                          <Eye size={13} /> Read
                        </button>
                      )}
                      {!alert.is_resolved && (
                        <button
                          onClick={() => markResolved.mutate(alert.id)}
                          style={{
                            background: '#f0fdf4', border: '1px solid #86efac',
                            borderRadius: '0.5rem', padding: '0.375rem 0.625rem',
                            cursor: 'pointer', color: '#16a34a',
                            fontSize: '0.75rem', display: 'flex',
                            alignItems: 'center', gap: '0.25rem',
                          }}
                        >
                          <Check size={13} /> Resolve
                        </button>
                      )}
                      {alert.is_resolved && (
                        <span style={{
                          display: 'flex', alignItems: 'center', gap: '0.25rem',
                          fontSize: '0.75rem', color: '#16a34a',
                        }}>
                          <CheckCircle size={13} /> Resolved
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}