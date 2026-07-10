// src/components/dashboard/SummaryCards.tsx
import { TrendingUp, TrendingDown, PiggyBank, Receipt } from 'lucide-react'

interface Props {
  income: number
  expenses: number
  savings: number
  transactionCount: number
  isLoading?: boolean
}

function StatCard({
  label, value, icon, color, bg, sub
}: {
  label: string
  value: string
  icon: React.ReactNode
  color: string
  bg: string
  sub?: string
}) {
  return (
    <div className="card" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ fontSize: '0.8rem', color: '#64748b', margin: '0 0 0.5rem', fontWeight: 500 }}>
            {label}
          </p>
          <p style={{ fontSize: '1.75rem', fontWeight: 700, color, margin: 0 }}>
            {value}
          </p>
          {sub && (
            <p style={{ fontSize: '0.75rem', color: '#94a3b8', margin: '0.25rem 0 0' }}>
              {sub}
            </p>
          )}
        </div>
        <div style={{
          width: '44px', height: '44px', background: bg,
          borderRadius: '0.75rem', display: 'flex',
          alignItems: 'center', justifyContent: 'center', color,
        }}>
          {icon}
        </div>
      </div>
    </div>
  )
}

function SkeletonCard() {
  return (
    <div className="card" style={{ padding: '1.25rem' }}>
      <div style={{ background: '#f1f5f9', borderRadius: '0.5rem', height: '80px', animation: 'pulse 1.5s infinite' }} />
    </div>
  )
}

export default function SummaryCards({ income, expenses, savings, transactionCount, isLoading }: Props) {
  const formatAmount = (amt: number) => `₹${Math.abs(amt).toLocaleString('en-IN')}`

  if (isLoading) {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        {[1,2,3,4].map(i => <SkeletonCard key={i} />)}
      </div>
    )
  }

  const savingsRate = income > 0 ? ((savings / income) * 100).toFixed(1) : '0'

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
      <StatCard
        label="Total Income"
        value={formatAmount(income)}
        icon={<TrendingUp size={20} />}
        color="#16a34a"
        bg="#f0fdf4"
        sub="This month"
      />
      <StatCard
        label="Total Expenses"
        value={formatAmount(expenses)}
        icon={<TrendingDown size={20} />}
        color="#dc2626"
        bg="#fff1f2"
        sub="This month"
      />
      <StatCard
        label="Net Savings"
        value={formatAmount(savings)}
        icon={<PiggyBank size={20} />}
        color={savings >= 0 ? '#0284c7' : '#dc2626'}
        bg={savings >= 0 ? '#f0f9ff' : '#fff1f2'}
        sub={`${savingsRate}% savings rate`}
      />
      <StatCard
        label="Transactions"
        value={transactionCount.toString()}
        icon={<Receipt size={20} />}
        color="#7c3aed"
        bg="#faf5ff"
        sub="This month"
      />
    </div>
  )
}