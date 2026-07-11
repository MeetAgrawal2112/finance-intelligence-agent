// src/pages/DashboardPage.tsx — poora replace karo
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  TrendingUp, LogOut, LayoutDashboard,
  CreditCard, Bell, Bot, User, ChevronLeft, ChevronRight
} from 'lucide-react'
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

      {/* Navbar */}
      <nav style={{
        background: 'white', borderBottom: '1px solid #e2e8f0',
        padding: '0 1.5rem', height: '64px',
        display: 'flex', alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky', top: 0, zIndex: 100,
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        
      }}>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
          <div style={{
            width: '36px', height: '36px', background: '#0284c7',
            borderRadius: '0.625rem', display: 'flex',
            alignItems: 'center', justifyContent: 'center',
          }}>
            <TrendingUp size={20} color="white" />
          </div>
          <span style={{ fontWeight: 700, color: '#0f172a' }}>
            Finance Intelligence
          </span>
        </div>

        <div style={{ display: 'flex', gap: '0.25rem' }}>
          {[
            { icon: <LayoutDashboard size={15} />, label: 'Dashboard', active: true },
            { icon: <CreditCard size={15} />, label: 'Transactions', path: '/transactions' },
            { icon: <Bell size={15} />, label: 'Alerts' },
            { icon: <Bot size={15} />, label: 'AI Chat' },
          ].map(item => (
            <button key={item.label} onClick={() => item.path && navigate(item.path)}
             style={{
              display: 'flex', alignItems: 'center', gap: '0.375rem',
              padding: '0.5rem 0.75rem', border: 'none', borderRadius: '0.5rem',
              cursor: 'pointer', fontSize: '0.875rem',
              background: item.active ? '#f0f9ff' : 'none',
              color: item.active ? '#0284c7' : '#64748b',
              fontWeight: item.active ? 600 : 400,
            }}>
              {item.icon}{item.label}
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '0.5rem',
            padding: '0.375rem 0.75rem', background: '#f8fafc',
            borderRadius: '2rem', border: '1px solid #e2e8f0',
          }}>
            <div style={{
              width: '28px', height: '28px', background: '#0284c7',
              borderRadius: '50%', display: 'flex',
              alignItems: 'center', justifyContent: 'center',
            }}>
              <User size={14} color="white" />
            </div>
            <span style={{ fontSize: '0.875rem', fontWeight: 500, color: '#374151' }}>
              {user?.full_name}
            </span>
          </div>
          <button onClick={handleLogout} className="btn-secondary" style={{ fontSize: '0.875rem' }}>
            <LogOut size={15} />
            Logout
          </button>
        </div>
      </nav>

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