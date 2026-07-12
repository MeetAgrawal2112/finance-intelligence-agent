// src/pages/TransactionsPage.tsx
import { useState } from 'react'
// import { useNavigate } from 'react-router-dom'
import { Plus, Upload, Search,
  X, AlertTriangle
} from 'lucide-react'
// import { useAuthStore } from '../store/authStore'
import { toast } from '../store/toastStore'
import { useTransactions, useDeleteTransaction } from '../hooks/useTransactions'
import TransactionTable from '../components/transactions/TransactionTable'
import AddTransactionModal from '../components/transactions/AddTransactionModal'
import CSVImport from '../components/transactions/CSVImport'
import type { TransactionFilters } from '../types'

export default function TransactionsPage() {
  const deleteMutation = useDeleteTransaction()

  const [filters, setFilters] = useState<TransactionFilters>({
    page: 1,
    page_size: 20,
    sort_by: 'transaction_date',
    sort_order: 'desc',
  })
  const [search, setSearch] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [showImport, setShowImport] = useState(false)
  const [anomalyOnly, setAnomalyOnly] = useState(false)
  const [typeFilter, setTypeFilter] = useState('')

  const { data, isLoading } = useTransactions({
    ...filters,
    search: search || undefined,
    anomalies_only: anomalyOnly,
    transaction_type: typeFilter as any || undefined,
  })

  const transactions = data?.data?.items || []
  const pagination = data?.data?.pagination || {}
  const total = pagination.total || 0
  const totalPages = pagination.total_pages || 1

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this transaction?')) return
    try {
      await deleteMutation.mutateAsync(id)
    } catch (err) {
      toast.error('Delete failed', 'Try again.')
    }
  }

  const clearFilters = () => {
    setSearch('')
    setAnomalyOnly(false)
    setTypeFilter('')
    setFilters(f => ({ ...f, page: 1 }))
  }

  const hasActiveFilters = search || anomalyOnly || typeFilter

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>

      {/* Content */}
      <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '2rem 1.5rem' }}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
              Transactions
            </h1>
            <p style={{ color: '#64748b', margin: '0.25rem 0 0', fontSize: '0.875rem' }}>
              {total} total transactions
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              onClick={() => setShowImport(true)}
              className="btn-secondary"
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}
            >
              <Upload size={15} /> Import CSV
            </button>
            <button
              onClick={() => setShowAddModal(true)}
              className="btn-primary"
              style={{
                width: 'auto', display: 'flex',
                alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem',
              }}
            >
              <Plus size={15} /> Add Transaction
            </button>
          </div>
        </div>

        {/* Filters Bar */}
        <div className="card" style={{ padding: '1rem', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>

            {/* Search */}
            <div style={{ position: 'relative', flex: 1, minWidth: '200px' }}>
              <Search size={15} color="#94a3b8" style={{
                position: 'absolute', left: '0.75rem',
                top: '50%', transform: 'translateY(-50%)',
              }} />
              <input
                placeholder="Search merchant or description..."
                value={search}
                onChange={e => {
                  setSearch(e.target.value)
                  setFilters(f => ({ ...f, page: 1 }))
                }}
                style={{
                  width: '100%', padding: '0.5rem 0.75rem 0.5rem 2.25rem',
                  border: '1px solid #e2e8f0', borderRadius: '0.625rem',
                  fontSize: '0.875rem', outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            </div>

            {/* Type Filter */}
            <select
              value={typeFilter}
              onChange={e => {
                setTypeFilter(e.target.value)
                setFilters(f => ({ ...f, page: 1 }))
              }}
              style={{
                padding: '0.5rem 0.75rem', border: '1px solid #e2e8f0',
                borderRadius: '0.625rem', fontSize: '0.875rem',
                background: 'white', cursor: 'pointer',
              }}
            >
              <option value="">All Types</option>
              <option value="debit">Debit Only</option>
              <option value="credit">Credit Only</option>
            </select>

            {/* Anomaly Toggle */}
            <button
              onClick={() => {
                setAnomalyOnly(!anomalyOnly)
                setFilters(f => ({ ...f, page: 1 }))
              }}
              style={{
                display: 'flex', alignItems: 'center', gap: '0.375rem',
                padding: '0.5rem 0.75rem', border: `1px solid ${anomalyOnly ? '#dc2626' : '#e2e8f0'}`,
                borderRadius: '0.625rem', background: anomalyOnly ? '#fff1f2' : 'white',
                color: anomalyOnly ? '#dc2626' : '#64748b',
                cursor: 'pointer', fontSize: '0.875rem', fontWeight: anomalyOnly ? 600 : 400,
              }}
            >
              <AlertTriangle size={14} />
              Suspicious Only
            </button>

            {/* Clear Filters */}
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.25rem',
                  padding: '0.5rem 0.75rem', border: 'none',
                  borderRadius: '0.625rem', background: '#f1f5f9',
                  color: '#64748b', cursor: 'pointer', fontSize: '0.8rem',
                }}
              >
                <X size={13} /> Clear
              </button>
            )}
          </div>
        </div>

        {/* Table */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <TransactionTable
            transactions={transactions}
            isLoading={isLoading}
            onDelete={handleDelete}
            currentPage={filters.page || 1}
            totalPages={totalPages}
            onPageChange={page => setFilters(f => ({ ...f, page }))}
            total={total}
          />
        </div>
      </div>

      {/* Modals */}
      {showAddModal && (
        <AddTransactionModal onClose={() => setShowAddModal(false)} />
      )}
      {showImport && (
        <CSVImport onClose={() => setShowImport(false)} />
      )}
    </div>
  )
}