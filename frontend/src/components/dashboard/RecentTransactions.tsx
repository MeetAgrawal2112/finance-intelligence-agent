// src/components/dashboard/RecentTransactions.tsx
import { AlertTriangle, TrendingDown, TrendingUp } from 'lucide-react'
import type { Transaction } from '../../types'
import { format } from 'date-fns'

interface Props {
  transactions: Transaction[]
  isLoading?: boolean
}

export default function RecentTransactions({ transactions, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="card">
        <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#374151', marginTop: 0 }}>
          Recent Transactions
        </h3>
        {[1,2,3,4,5].map(i => (
          <div key={i} style={{
            height: '52px', background: '#f8fafc',
            borderRadius: '0.5rem', marginBottom: '0.5rem',
            animation: 'pulse 1.5s infinite'
          }} />
        ))}
      </div>
    )
  }

  return (
    <div className="card">
      <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#374151', marginTop: 0, marginBottom: '1rem' }}>
        Recent Transactions
      </h3>

      {transactions.length === 0 ? (
        <p style={{ color: '#94a3b8', textAlign: 'center', padding: '2rem 0' }}>
          No transactions yet. Add some!
        </p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {transactions.slice(0, 8).map(txn => (
            <div
              key={txn.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.625rem',
                borderRadius: '0.625rem',
                background: txn.is_anomaly ? '#fff1f2' : '#f8fafc',
                border: txn.is_anomaly ? '1px solid #fca5a5' : '1px solid transparent',
              }}
            >
              {/* Icon */}
              <div style={{
                width: '36px', height: '36px',
                borderRadius: '0.5rem',
                background: txn.transaction_type === 'credit' ? '#f0fdf4' : '#fff1f2',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0,
              }}>
                {txn.transaction_type === 'credit'
                  ? <TrendingUp size={16} color="#16a34a" />
                  : <TrendingDown size={16} color="#dc2626" />
                }
              </div>

              {/* Details */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{
                  margin: 0, fontSize: '0.875rem', fontWeight: 500,
                  color: '#1e293b', whiteSpace: 'nowrap',
                  overflow: 'hidden', textOverflow: 'ellipsis',
                }}>
                  {txn.merchant_name || txn.description}
                </p>
                <p style={{ margin: 0, fontSize: '0.75rem', color: '#94a3b8' }}>
                  {format(new Date(txn.transaction_date), 'dd MMM yyyy')}
                </p>
              </div>

              {/* Amount + Anomaly */}
              <div style={{ textAlign: 'right', flexShrink: 0 }}>
                <p style={{
                  margin: 0, fontSize: '0.875rem', fontWeight: 600,
                  color: txn.transaction_type === 'credit' ? '#16a34a' : '#dc2626',
                }}>
                  {txn.transaction_type === 'credit' ? '+' : '-'}₹{txn.amount.toLocaleString('en-IN')}
                </p>
                {txn.is_anomaly && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '2px', justifyContent: 'flex-end' }}>
                    <AlertTriangle size={10} color="#dc2626" />
                    <span style={{ fontSize: '0.65rem', color: '#dc2626' }}>Suspicious</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}