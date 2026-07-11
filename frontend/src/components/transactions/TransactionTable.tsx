// src/components/transactions/TransactionTable.tsx
import {
  TrendingUp, TrendingDown, AlertTriangle,
  Trash2, Edit2, CheckCircle
} from 'lucide-react'
import type { Transaction } from '../../types'
import { format } from 'date-fns'

interface Props {
  transactions: Transaction[]
  isLoading?: boolean
  onDelete?: (id: string) => void
  onEdit?: (transaction: Transaction) => void
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  total: number
}

function SkeletonRow() {
  return (
    <tr>
      {[1,2,3,4,5,6].map(i => (
        <td key={i} style={{ padding: '1rem' }}>
          <div style={{
            height: '16px', background: '#f1f5f9',
            borderRadius: '4px', animation: 'pulse 1.5s infinite'
          }} />
        </td>
      ))}
    </tr>
  )
}

export default function TransactionTable({
  transactions, isLoading, onDelete, onEdit,
  currentPage, totalPages, onPageChange, total
}: Props) {

  const TYPE_COLOR = {
    debit: { color: '#dc2626', bg: '#fff1f2', icon: <TrendingDown size={14} /> },
    credit: { color: '#16a34a', bg: '#f0fdf4', icon: <TrendingUp size={14} /> },
  }

  return (
    <div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
              {['Date', 'Merchant', 'Category', 'Amount', 'Type', 'Status', 'Actions'].map(h => (
                <th key={h} style={{
                  padding: '0.75rem 1rem', textAlign: 'left',
                  fontSize: '0.75rem', fontWeight: 600,
                  color: '#64748b', letterSpacing: '0.05em',
                }}>
                  {h.toUpperCase()}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              [1,2,3,4,5].map(i => <SkeletonRow key={i} />)
            ) : transactions.length === 0 ? (
              <tr>
                <td colSpan={7} style={{
                  padding: '3rem', textAlign: 'center',
                  color: '#94a3b8'
                }}>
                  No transactions found. Add some or import CSV!
                </td>
              </tr>
            ) : (
              transactions.map(txn => {
                const typeStyle = TYPE_COLOR[txn.transaction_type]
                return (
                  <tr
                    key={txn.id}
                    style={{
                      borderBottom: '1px solid #f1f5f9',
                      background: txn.is_anomaly
                        ? '#fff8f8' : 'white',
                      transition: 'background 0.15s',
                    }}
                    onMouseEnter={e => {
                      if (!txn.is_anomaly)
                        (e.currentTarget as HTMLElement).style.background = '#f8fafc'
                    }}
                    onMouseLeave={e => {
                      (e.currentTarget as HTMLElement).style.background =
                        txn.is_anomaly ? '#fff8f8' : 'white'
                    }}
                  >
                    {/* Date */}
                    <td style={{ padding: '0.875rem 1rem' }}>
                      <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                        {format(new Date(txn.transaction_date), 'dd MMM yyyy')}
                      </span>
                    </td>

                    {/* Merchant */}
                    <td style={{ padding: '0.875rem 1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {txn.is_anomaly && (
                          <AlertTriangle size={14} color="#dc2626" />
                        )}
                        <div>
                          <p style={{
                            margin: 0, fontSize: '0.875rem',
                            fontWeight: 500, color: '#1e293b',
                            maxWidth: '150px', overflow: 'hidden',
                            textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                          }}>
                            {txn.merchant_name || txn.description}
                          </p>
                          {txn.merchant_name && (
                            <p style={{
                              margin: 0, fontSize: '0.7rem', color: '#94a3b8',
                              maxWidth: '150px', overflow: 'hidden',
                              textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                            }}>
                              {txn.description}
                            </p>
                          )}
                        </div>
                      </div>
                    </td>

                    {/* Category */}
                    <td style={{ padding: '0.875rem 1rem' }}>
                      {txn.category_id ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                          <span style={{ fontSize: '0.75rem', color: '#374151' }}>
                            Category
                          </span>
                          {txn.is_manually_categorized && (
                            <CheckCircle size={12} color="#16a34a" aria-label="Manually set" />
                          )}
                        </div>
                      ) : (
                        <span style={{
                          fontSize: '0.75rem', color: '#94a3b8',
                          fontStyle: 'italic'
                        }}>
                          Uncategorised
                        </span>
                      )}
                    </td>

                    {/* Amount */}
                    <td style={{ padding: '0.875rem 1rem' }}>
                      <span style={{
                        fontSize: '0.875rem', fontWeight: 600,
                        color: typeStyle.color,
                      }}>
                        {txn.transaction_type === 'credit' ? '+' : '-'}
                        ₹{txn.amount.toLocaleString('en-IN')}
                      </span>
                    </td>

                    {/* Type */}
                    <td style={{ padding: '0.875rem 1rem' }}>
                      <span style={{
                        display: 'inline-flex', alignItems: 'center',
                        gap: '0.25rem', padding: '0.2rem 0.5rem',
                        background: typeStyle.bg, color: typeStyle.color,
                        borderRadius: '2rem', fontSize: '0.7rem', fontWeight: 500,
                      }}>
                        {typeStyle.icon}
                        {txn.transaction_type}
                      </span>
                    </td>

                    {/* Status */}
                    <td style={{ padding: '0.875rem 1rem' }}>
                      {txn.is_anomaly ? (
                        <span style={{
                          display: 'inline-flex', alignItems: 'center',
                          gap: '0.25rem', padding: '0.2rem 0.5rem',
                          background: '#fff1f2', color: '#dc2626',
                          borderRadius: '2rem', fontSize: '0.7rem', fontWeight: 500,
                        }}>
                          <AlertTriangle size={10} /> Suspicious
                        </span>
                      ) : (
                        <span style={{
                          display: 'inline-flex', alignItems: 'center',
                          gap: '0.25rem', padding: '0.2rem 0.5rem',
                          background: '#f0fdf4', color: '#16a34a',
                          borderRadius: '2rem', fontSize: '0.7rem', fontWeight: 500,
                        }}>
                          <CheckCircle size={10} /> Normal
                        </span>
                      )}
                    </td>

                    {/* Actions */}
                    <td style={{ padding: '0.875rem 1rem' }}>
                      <div style={{ display: 'flex', gap: '0.375rem' }}>
                        {onEdit && (
                          <button
                            onClick={() => onEdit(txn)}
                            style={{
                              background: '#f0f9ff', border: 'none',
                              borderRadius: '0.375rem', padding: '0.375rem',
                              cursor: 'pointer', color: '#0284c7',
                            }}
                            title="Edit"
                          >
                            <Edit2 size={14} />
                          </button>
                        )}
                        {onDelete && (
                          <button
                            onClick={() => onDelete(txn.id)}
                            style={{
                              background: '#fff1f2', border: 'none',
                              borderRadius: '0.375rem', padding: '0.375rem',
                              cursor: 'pointer', color: '#dc2626',
                            }}
                            title="Delete"
                          >
                            <Trash2 size={14} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{
          display: 'flex', alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1rem 1.25rem',
          borderTop: '1px solid #f1f5f9',
        }}>
          <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
            Showing {((currentPage-1)*20)+1}–{Math.min(currentPage*20, total)} of {total}
          </span>
          <div style={{ display: 'flex', gap: '0.375rem' }}>
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="btn-secondary"
              style={{ padding: '0.375rem 0.75rem', fontSize: '0.8rem' }}
            >
              Previous
            </button>
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const page = i + 1
              return (
                <button
                  key={page}
                  onClick={() => onPageChange(page)}
                  style={{
                    padding: '0.375rem 0.625rem',
                    border: 'none', borderRadius: '0.375rem',
                    cursor: 'pointer', fontSize: '0.8rem',
                    background: page === currentPage ? '#0284c7' : '#f1f5f9',
                    color: page === currentPage ? 'white' : '#374151',
                    fontWeight: page === currentPage ? 600 : 400,
                  }}
                >
                  {page}
                </button>
              )
            })}
            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="btn-secondary"
              style={{ padding: '0.375rem 0.75rem', fontSize: '0.8rem' }}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}