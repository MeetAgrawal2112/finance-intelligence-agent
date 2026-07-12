// src/pages/ForecastPage.tsx
import { useState } from 'react'
// import { useNavigate } from 'react-router-dom'
import {
  TrendingUp, TrendingDown, Minus,
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell
} from 'recharts'
// import { useAuthStore } from '../store/authStore'
import { useSpendingForecast } from '../hooks/useDashboard'
import { apiClient } from '../api/client'
import { useQuery } from '@tanstack/react-query'

const COLORS = [
  '#0284c7','#16a34a','#dc2626','#7c3aed',
  '#d97706','#0891b2','#be185d','#65a30d',
]

function useSavingsAdvice(income: number) {
  return useQuery({
    queryKey: ['savings-advice', income],
    queryFn: async () => {
      const res = await apiClient.get(
        `/ml/savings-advice?monthly_income=${income}`
      )
      return res.data
    },
  })
}

export default function ForecastPage() {
  const [income, setIncome] = useState(75000)
  const [inputIncome, setInputIncome] = useState('75000')

  const { data: forecastData, isLoading: forecastLoading } = useSpendingForecast()
  const { data: adviceData } = useSavingsAdvice(income)

  const forecast = forecastData?.data
  const predictions = forecast?.predictions || []
  const advice = adviceData?.data


  const STATUS_CONFIG = {
    excellent: { color: '#16a34a', bg: '#f0fdf4', emoji: '🎉' },
    good: { color: '#0284c7', bg: '#f0f9ff', emoji: '👍' },
    warning: { color: '#d97706', bg: '#fffbeb', emoji: '⚠️' },
    danger: { color: '#dc2626', bg: '#fff1f2', emoji: '🚨' },
  }

  const trendIcon = (trend: string) => {
    if (trend === 'increasing') return <TrendingUp size={14} color="#dc2626" />
    if (trend === 'decreasing') return <TrendingDown size={14} color="#16a34a" />
    return <Minus size={14} color="#64748b" />
  }


  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>

      <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '2rem 1.5rem' }}>

        {/* Header */}
        <div style={{ marginBottom: '1.5rem' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
            Spending Forecast
          </h1>
          <p style={{ color: '#64748b', margin: '0.25rem 0 0', fontSize: '0.875rem' }}>
            {forecast?.forecast_period
              ? `${forecast.forecast_period.start} → ${forecast.forecast_period.end}`
              : 'Next 30 days prediction'
            }
          </p>
        </div>

        {/* Summary Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem', marginBottom: '1.5rem'
        }}>
          <div className="card" style={{ padding: '1.25rem' }}>
            <p style={{ margin: '0 0 0.5rem', fontSize: '0.75rem', color: '#64748b', fontWeight: 500 }}>
              Total Predicted
            </p>
            <p style={{ margin: 0, fontSize: '1.75rem', fontWeight: 700, color: '#dc2626' }}>
              ₹{(forecast?.total_predicted || 0).toLocaleString('en-IN')}
            </p>
            <p style={{ margin: '0.25rem 0 0', fontSize: '0.75rem', color: '#94a3b8' }}>
              Next 30 days
            </p>
          </div>

          <div className="card" style={{ padding: '1.25rem' }}>
            <p style={{ margin: '0 0 0.5rem', fontSize: '0.75rem', color: '#64748b', fontWeight: 500 }}>
              Savings Potential
            </p>
            <p style={{ margin: 0, fontSize: '1.75rem', fontWeight: 700, color: '#16a34a' }}>
              ₹{(forecast?.savings_potential || 0).toLocaleString('en-IN')}
            </p>
            <p style={{ margin: '0.25rem 0 0', fontSize: '0.75rem', color: '#94a3b8' }}>
              With 20% cut in top 3
            </p>
          </div>

          <div className="card" style={{ padding: '1.25rem' }}>
            <p style={{ margin: '0 0 0.5rem', fontSize: '0.75rem', color: '#64748b', fontWeight: 500 }}>
              Top Category
            </p>
            <p style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, color: '#7c3aed' }}>
              {forecast?.top_spending_category || 'N/A'}
            </p>
            <p style={{ margin: '0.25rem 0 0', fontSize: '0.75rem', color: '#94a3b8' }}>
              Highest predicted spend
            </p>
          </div>
        </div>

        {/* Charts Row */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>

          {/* Bar Chart */}
          <div className="card">
            <h3 style={{ margin: '0 0 1rem', fontSize: '0.9rem', fontWeight: 600, color: '#374151' }}>
              Category Forecast
            </h3>
            {forecastLoading ? (
              <div style={{ height: '250px', background: '#f1f5f9', borderRadius: '0.5rem', animation: 'pulse 1.5s infinite' }} />
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart
                  data={predictions.slice(0, 6).map((p: any) => ({
                    name: p.category.length > 10 ? p.category.slice(0, 10) + '...' : p.category,
                    predicted: p.predicted_amount,
                    lower: p.lower_bound,
                    upper: p.upper_bound,
                  }))}
                  margin={{ top: 5, right: 10, left: 10, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} />
                  <YAxis
                    tickFormatter={v => `₹${(v/1000).toFixed(0)}k`}
                    tick={{ fontSize: 11, fill: '#64748b' }}
                  />
                  <Tooltip
                    formatter={(v: any) => [`₹${(v as number).toLocaleString('en-IN')}`, 'Predicted']}
                  />
                  <Bar dataKey="predicted" radius={[4,4,0,0]}>
                    {predictions.slice(0, 6).map((_: any, i: number) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Savings Advice Card */}
          <div className="card">
            <h3 style={{ margin: '0 0 1rem', fontSize: '0.9rem', fontWeight: 600, color: '#374151' }}>
              Savings Analysis
            </h3>

            {/* Income Input */}
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ fontSize: '0.8rem', color: '#64748b', display: 'block', marginBottom: '0.375rem' }}>
                Monthly Income (₹)
              </label>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                  type="number"
                  value={inputIncome}
                  onChange={e => setInputIncome(e.target.value)}
                  style={{
                    flex: 1, padding: '0.5rem 0.75rem',
                    border: '1px solid #e2e8f0', borderRadius: '0.625rem',
                    fontSize: '0.875rem', outline: 'none',
                  }}
                />
                <button
                  onClick={() => setIncome(Number(inputIncome))}
                  className="btn-primary"
                  style={{ width: 'auto', padding: '0.5rem 0.75rem', fontSize: '0.8rem' }}
                >
                  Calculate
                </button>
              </div>
            </div>

            {advice && (() => {
              const status = STATUS_CONFIG[advice.savings?.status as keyof typeof STATUS_CONFIG]
                || STATUS_CONFIG.warning
              return (
                <div>
                  <div style={{
                    background: status.bg, borderRadius: '0.75rem',
                    padding: '0.875rem', marginBottom: '0.75rem',
                  }}>
                    <p style={{ margin: '0 0 0.25rem', fontSize: '1.25rem' }}>
                      {status.emoji} {advice.savings?.status?.toUpperCase()}
                    </p>
                    <p style={{ margin: 0, fontSize: '0.8rem', color: '#374151' }}>
                      {advice.savings?.message}
                    </p>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                    {[
                      { label: 'Predicted Expenses', value: advice.savings?.predicted_expenses, color: '#dc2626' },
                      { label: 'Predicted Savings', value: advice.savings?.predicted_savings, color: '#16a34a' },
                      { label: 'Savings Rate', value: `${advice.savings?.savings_rate}%`, color: '#0284c7', isPercent: true },
                      { label: 'Target (20%)', value: advice.savings?.targets?.savings_target, color: '#7c3aed' },
                    ].map(item => (
                      <div key={item.label} style={{
                        background: '#f8fafc', borderRadius: '0.5rem',
                        padding: '0.625rem',
                      }}>
                        <p style={{ margin: '0 0 0.2rem', fontSize: '0.7rem', color: '#64748b' }}>
                          {item.label}
                        </p>
                        <p style={{ margin: 0, fontSize: '0.9rem', fontWeight: 700, color: item.color }}>
                          {item.isPercent
                            ? item.value
                            : `₹${Number(item.value || 0).toLocaleString('en-IN')}`
                          }
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )
            })()}
          </div>
        </div>

        {/* Detailed Predictions Table */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid #f1f5f9' }}>
            <h3 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 600, color: '#374151' }}>
              Category-wise Predictions
            </h3>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f8fafc' }}>
                {['Category', 'Predicted', 'Range', 'Daily Avg', 'Trend', 'Confidence'].map(h => (
                  <th key={h} style={{
                    padding: '0.75rem 1rem', textAlign: 'left',
                    fontSize: '0.7rem', fontWeight: 600,
                    color: '#64748b', letterSpacing: '0.05em',
                  }}>
                    {h.toUpperCase()}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {predictions.map((p: any, i: number) => (
                <tr key={p.category} style={{ borderTop: '1px solid #f1f5f9' }}>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div style={{
                        width: '10px', height: '10px', borderRadius: '50%',
                        background: COLORS[i % COLORS.length],
                      }} />
                      <span style={{ fontSize: '0.875rem', fontWeight: 500, color: '#1e293b' }}>
                        {p.category}
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <span style={{ fontSize: '0.875rem', fontWeight: 700, color: '#dc2626' }}>
                      ₹{p.predicted_amount.toLocaleString('en-IN')}
                    </span>
                  </td>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      ₹{p.lower_bound.toLocaleString('en-IN')} – ₹{p.upper_bound.toLocaleString('en-IN')}
                    </span>
                  </td>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <span style={{ fontSize: '0.8rem', color: '#374151' }}>
                      ₹{p.daily_average.toLocaleString('en-IN')}
                    </span>
                  </td>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      {trendIcon(p.trend)}
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                        {p.trend}
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div style={{
                        flex: 1, height: '6px', background: '#f1f5f9',
                        borderRadius: '3px', overflow: 'hidden',
                        maxWidth: '80px',
                      }}>
                        <div style={{
                          height: '100%',
                          width: `${(p.confidence || 0) * 100}%`,
                          background: COLORS[i % COLORS.length],
                          borderRadius: '3px',
                        }} />
                      </div>
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                        {((p.confidence || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}