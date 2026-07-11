// src/pages/DashboardPage.tsx — poora replace karo
import { useState } from 'react'
import {
  TrendingUp, LogOut, LayoutDashboard,
  CreditCard, Bell, Bot, User, ChevronLeft, ChevronRight,
  AlertTriangle
} from 'lucide-react'
import { useUnreadCount } from '../hooks/useAlerts'

import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { toast } from '../store/toastStore'
import { useMonthlySummary, useCategoryAnalytics } from '../hooks/useDashboard'
import { useTransactions } from '../hooks/useTransactions'
import SummaryCards from '../components/dashboard/SummaryCards'
import SpendingChart from '../components/dashboard/SpendingChart'
import RecentTransactions from '../components/dashboard/RecentTransactions'
import AIChat from '../components/dashboard/AIChat'

export default function DashboardPage() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const unreadAlerts = useUnreadCount()
  const now = new Date()
  const [month, setMonth] = useState(now.getMonth() + 1)
  const [year, setYear] = useState(now.getFullYear())

  const { data: summaryData, isLoading: summaryLoading } =
    useMonthlySummary(month, year)

  const { data: analyticsData, isLoading: analyticsLoading } =
    useCategoryAnalytics(month, year)

  const { data: txnData, isLoading: txnLoading } =
    useTransactions({ page: 1, page_size: 10 })

  const summary = summaryData?.data
  const categories = analyticsData?.data?.categories || []
  const transactions = txnData?.data?.items || []

  const handleLogout = async () => {
    await logout()
    toast.info('Logged out', 'Phir milenge! 👋')
    navigate('/login')
  }

  const prevMonth = () => {
    if (month === 1) { setMonth(12); setYear(y => y - 1) }
    else setMonth(m => m - 1)
  }

  const nextMonth = () => {
    if (month === 12) { setMonth(1); setYear(y => y + 1) }
    else setMonth(m => m + 1)
  }

  const monthNames = ['Jan','Feb','Mar','Apr','May','Jun',
                      'Jul','Aug','Sep','Oct','Nov','Dec']

                      
  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>

      {/* Main Content */}
      <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '2rem 1.5rem' }}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
            Namaste, {user?.full_name?.split(' ')[0]} 👋
          </h1>
          <p style={{ color: '#64748b', margin: '0.25rem 0 0', fontSize: '0.875rem' }}>
            Yahan hai tera financial overview
          </p>
        </div>

          {/* Month Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button onClick={prevMonth} className="btn-secondary" style={{ padding: '0.5rem' }}>
            <ChevronLeft size={16} />
          </button>
          <span style={{ fontWeight: 600, color: '#374151', minWidth: '80px', textAlign: 'center', fontSize: '0.875rem' }}>
            {monthNames[month-1]} {year}
          </span>
          <button onClick={nextMonth} className="btn-secondary" style={{ padding: '0.5rem' }}>
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

        {/* Summary Cards */}
        <div style={{ marginBottom: '1.5rem' }}>
          <SummaryCards
            income={summary?.total_income || 0}
            expenses={summary?.total_expenses || 0}
            savings={summary?.net_savings || 0}
            transactionCount={summary?.transaction_count || 0}
            isLoading={summaryLoading}
          />
          {unreadAlerts > 0 && (
  <div
    onClick={() => navigate('/alerts')}
    style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      padding: '0.875rem 1.25rem',
      background: '#fff1f2',
      border: '1px solid #fca5a5',
      borderRadius: '0.875rem',
      cursor: 'pointer',
      marginBottom: '1.5rem',
      transition: 'background 0.15s',
    }}
  >
    <AlertTriangle size={20} color="#dc2626" />
    <div style={{ flex: 1 }}>
      <p style={{ margin: 0, fontWeight: 600, fontSize: '0.875rem', color: '#dc2626' }}>
        {unreadAlerts} unread alert{unreadAlerts > 1 ? 's' : ''}
      </p>
      <p style={{ margin: 0, fontSize: '0.75rem', color: '#ef4444' }}>
        Suspicious transactions detected — click to review
      </p>
    </div>
    <span style={{ fontSize: '0.8rem', color: '#dc2626', fontWeight: 500 }}>
      View →
    </span>
  </div>
)}
        </div>

        {/* Charts */}
        <div style={{ marginBottom: '1.5rem' }}>
          <SpendingChart
            data={categories}
            isLoading={analyticsLoading}
          />
        </div>

        {/* Bottom Grid — Transactions + AI Chat */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '1rem',
        }}>
          <RecentTransactions
            transactions={transactions}
            isLoading={txnLoading}
          />
          <AIChat />
        </div>
      </div>
    </div>
  )
}