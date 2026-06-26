// src/pages/DashboardPage.tsx — poora replace karo
import { useAuthStore } from '../store/authStore'
import { useNavigate } from 'react-router-dom'
import {
  TrendingUp, LogOut, LayoutDashboard,
  CreditCard, Bell, Bot, User
} from 'lucide-react'
import { toast } from '../store/toastStore'

export default function DashboardPage() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    toast.info('Logged out', 'Phir milenge! 👋')
    navigate('/login')
  }

  const stats = [
    {
      label: 'Total Expenses',
      value: '₹0',
      sub: 'This month',
      color: '#ef4444',
      bg: '#fff1f2',
    },
    {
      label: 'Total Income',
      value: '₹0',
      sub: 'This month',
      color: '#16a34a',
      bg: '#f0fdf4',
    },
    {
      label: 'Net Savings',
      value: '₹0',
      sub: 'This month',
      color: '#0284c7',
      bg: '#f0f9ff',
    },
    {
      label: 'Transactions',
      value: '0',
      sub: 'This month',
      color: '#7c3aed',
      bg: '#faf5ff',
    },
  ]

  const quickLinks = [
    {
      icon: <CreditCard size={24} />,
      label: 'Transactions',
      desc: 'Apni sab transactions dekho',
      color: '#0284c7',
      bg: '#f0f9ff',
    },
    {
      icon: <Bell size={24} />,
      label: 'Alerts',
      desc: 'Anomalies aur warnings',
      color: '#d97706',
      bg: '#fffbeb',
    },
    {
      icon: <Bot size={24} />,
      label: 'AI Chat',
      desc: 'Apne finances ke baare mein poochho',
      color: '#7c3aed',
      bg: '#faf5ff',
    },
    {
      icon: <TrendingUp size={24} />,
      label: 'Forecast',
      desc: 'Future spending prediction',
      color: '#16a34a',
      bg: '#f0fdf4',
    },
  ]

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>

      {/* Navbar */}
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
          <div style={{
            width: '36px',
            height: '36px',
            background: '#0284c7',
            borderRadius: '0.625rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <TrendingUp size={20} color="white" />
          </div>
          <span style={{ fontWeight: 700, color: '#0f172a', fontSize: '1rem' }}>
            Finance Intelligence
          </span>
        </div>

        {/* Nav links */}
        <div style={{
          display: 'flex',
          gap: '0.25rem',
        }}>
          {[
            { icon: <LayoutDashboard size={16} />, label: 'Dashboard' },
            { icon: <CreditCard size={16} />, label: 'Transactions' },
            { icon: <Bell size={16} />, label: 'Alerts' },
            { icon: <Bot size={16} />, label: 'AI Chat' },
          ].map((item) => (
            <button
              key={item.label}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.375rem',
                padding: '0.5rem 0.75rem',
                background: item.label === 'Dashboard' ? '#f0f9ff' : 'none',
                border: 'none',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                color: item.label === 'Dashboard' ? '#0284c7' : '#64748b',
                fontSize: '0.875rem',
                fontWeight: item.label === 'Dashboard' ? 600 : 400,
              }}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </div>

        {/* User menu */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.375rem 0.75rem',
            background: '#f8fafc',
            borderRadius: '2rem',
            border: '1px solid #e2e8f0',
          }}>
            <div style={{
              width: '28px',
              height: '28px',
              background: '#0284c7',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <User size={14} color="white" />
            </div>
            <span style={{
              fontSize: '0.875rem',
              fontWeight: 500,
              color: '#374151',
            }}>
              {user?.full_name}
            </span>
          </div>

          <button
            onClick={handleLogout}
            className="btn-secondary"
            style={{ padding: '0.5rem 0.75rem', fontSize: '0.875rem' }}
          >
            <LogOut size={15} />
            Logout
          </button>
        </div>
      </nav>

      {/* Main content */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1.5rem' }}>

        {/* Welcome header */}
        <div style={{ marginBottom: '2rem' }}>
          <h1 style={{
            fontSize: '1.75rem',
            fontWeight: 700,
            color: '#0f172a',
            margin: 0,
          }}>
            Namaste, {user?.full_name?.split(' ')[0]} 👋
          </h1>
          <p style={{ color: '#64748b', marginTop: '0.25rem' }}>
            Aaj ka din kaisa hai? Yahan hai tera financial overview.
          </p>
        </div>

        {/* Stats grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1rem',
          marginBottom: '2rem',
        }}>
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="card"
              style={{ padding: '1.25rem' }}
            >
              <p style={{
                fontSize: '0.8rem',
                color: '#64748b',
                margin: '0 0 0.5rem',
                fontWeight: 500,
              }}>
                {stat.label}
              </p>
              <p style={{
                fontSize: '1.75rem',
                fontWeight: 700,
                color: stat.color,
                margin: '0 0 0.25rem',
              }}>
                {stat.value}
              </p>
              <p style={{
                fontSize: '0.75rem',
                color: '#94a3b8',
                margin: 0,
              }}>
                {stat.sub}
              </p>
            </div>
          ))}
        </div>

        {/* Quick links */}
        <h2 style={{
          fontSize: '1rem',
          fontWeight: 600,
          color: '#374151',
          marginBottom: '1rem',
        }}>
          Quick Access
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1rem',
          marginBottom: '2rem',
        }}>
          {quickLinks.map((link) => (
            <div
              key={link.label}
              className="card"
              style={{
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                padding: '1.25rem',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)'
                e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.1)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.06)'
              }}
            >
              <div style={{
                width: '48px',
                height: '48px',
                background: link.bg,
                borderRadius: '0.75rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: link.color,
                flexShrink: 0,
              }}>
                {link.icon}
              </div>
              <div>
                <p style={{
                  fontWeight: 600,
                  color: '#0f172a',
                  margin: '0 0 0.2rem',
                  fontSize: '0.9rem',
                }}>
                  {link.label}
                </p>
                <p style={{
                  fontSize: '0.8rem',
                  color: '#64748b',
                  margin: 0,
                }}>
                  {link.desc}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Coming soon banner */}
        <div className="card" style={{
          textAlign: 'center',
          padding: '3rem',
          background: 'linear-gradient(135deg, #f0f9ff, #faf5ff)',
          border: '1px dashed #bfdbfe',
        }}>
          <Bot size={48} color="#0284c7" style={{ margin: '0 auto 1rem' }} />
          <h3 style={{
            fontSize: '1.25rem',
            fontWeight: 600,
            color: '#0f172a',
            margin: '0 0 0.5rem',
          }}>
            AI Features Coming Soon!
          </h3>
          <p style={{ color: '#64748b', margin: 0 }}>
            Day 12 mein LangChain agent setup hoga —
            phir seedha pooch sakte ho apne finances ke baare mein.
          </p>
        </div>
      </div>
    </div>
  )
}                       