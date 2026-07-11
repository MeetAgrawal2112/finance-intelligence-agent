// src/components/transactions/AddTransactionModal.tsx
import { useState } from 'react'
import { X, Loader2 } from 'lucide-react'
import { useCreateTransaction } from '../../hooks/useTransactions'

interface Props {
  onClose: () => void
}

type FormState = {
  amount: string
  transaction_type: 'debit' | 'credit'
  description: string
  merchant_name: string
  transaction_date: string
  currency: string
}

export default function AddTransactionModal({ onClose }: Props) {
  const createMutation = useCreateTransaction()
  const [form, setForm] = useState<FormState>({
    amount: '',
    transaction_type: 'debit',
    description: '',
    merchant_name: '',
    transaction_date: new Date().toISOString().split('T')[0],
    currency: 'INR',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.amount || !form.description) return

    try {
      await createMutation.mutateAsync({
        ...form,
        amount: parseFloat(form.amount),
        transaction_date: new Date(form.transaction_date).toISOString(),
      })
      onClose()
    } catch (err) {
      console.error(err)
    }
  }

  const inputStyle = {
    width: '100%', padding: '0.625rem 0.875rem',
    border: '1px solid #e2e8f0', borderRadius: '0.625rem',
    fontSize: '0.875rem', outline: 'none', boxSizing: 'border-box' as const,
  }

  const labelStyle = {
    display: 'block', fontSize: '0.8rem',
    fontWeight: 500, color: '#374151', marginBottom: '0.375rem',
  }

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div style={{
        background: 'white', borderRadius: '1rem',
        padding: '1.5rem', width: '100%', maxWidth: '440px',
        boxShadow: '0 20px 40px rgba(0,0,0,0.15)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>
            Add Transaction
          </h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
            <X size={20} color="#64748b" />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.75rem' }}>
            <div>
              <label style={labelStyle}>Amount (₹) *</label>
              <input
                type="number"
                placeholder="1000"
                value={form.amount}
                onChange={e => setForm(f => ({ ...f, amount: e.target.value }))}
                style={inputStyle}
                required
              />
            </div>
            <div>
              <label style={labelStyle}>Type *</label>
              <select
                value={form.transaction_type}
                onChange={e => setForm(f => ({
                  ...f,
                  transaction_type: e.target.value as FormState['transaction_type'],
                }))}
                style={inputStyle}
              >
                <option value="debit">Debit (Expense)</option>
                <option value="credit">Credit (Income)</option>
              </select>
            </div>
          </div>

          <div style={{ marginBottom: '0.75rem' }}>
            <label style={labelStyle}>Description *</label>
            <input
              placeholder="Zomato biryani order"
              value={form.description}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
              style={inputStyle}
              required
            />
          </div>

          <div style={{ marginBottom: '0.75rem' }}>
            <label style={labelStyle}>Merchant Name</label>
            <input
              placeholder="Zomato"
              value={form.merchant_name}
              onChange={e => setForm(f => ({ ...f, merchant_name: e.target.value }))}
              style={inputStyle}
            />
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <label style={labelStyle}>Date *</label>
            <input
              type="date"
              value={form.transaction_date}
              onChange={e => setForm(f => ({ ...f, transaction_date: e.target.value }))}
              style={inputStyle}
              required
            />
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="btn-primary"
              style={{
                width: 'auto', display: 'flex',
                alignItems: 'center', gap: '0.5rem',
              }}
            >
              {createMutation.isPending ? (
                <><Loader2 size={14} className="animate-spin" /> Saving...</>
              ) : 'Add Transaction'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}