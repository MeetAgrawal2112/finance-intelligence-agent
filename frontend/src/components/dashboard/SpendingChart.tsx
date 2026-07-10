// src/components/dashboard/SpendingChart.tsx
import {
  PieChart, Pie, Cell, Tooltip,
  BarChart, Bar, XAxis, YAxis,
  CartesianGrid, ResponsiveContainer, Legend
} from 'recharts'

interface CategoryData {
  category_name: string
  total_amount: number
  percentage: number
  transaction_count: number
}

interface Props {
  data: CategoryData[]
  isLoading?: boolean
}

const COLORS = [
  '#0284c7', '#16a34a', '#dc2626', '#7c3aed',
  '#d97706', '#0891b2', '#be185d', '#65a30d',
]

const formatINR = (value: number) =>
  `₹${value.toLocaleString('en-IN')}`

export default function SpendingChart({ data, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="card">
        <div style={{ height: '300px', background: '#f1f5f9', borderRadius: '0.75rem', animation: 'pulse 1.5s infinite' }} />
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <p style={{ color: '#94a3b8' }}>No spending data available</p>
        <p style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>Add transactions to see charts</p>
      </div>
    )
  }

  const pieData = data.map(d => ({
    name: d.category_name,
    value: d.total_amount,
  }))

  const barData = data.slice(0, 6).map(d => ({
    name: d.category_name.length > 10
      ? d.category_name.substring(0, 10) + '...'
      : d.category_name,
    amount: d.total_amount,
    count: d.transaction_count,
  }))

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>

      {/* Pie Chart */}
      <div className="card">
        <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#374151', marginBottom: '1rem', marginTop: 0 }}>
          Category Breakdown
        </h3>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={3}
              dataKey="value"
            >
              {pieData.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip
              formatter={(value) => {
                if (typeof value === 'number') return [formatINR(value), 'Amount']
                return []
              }}
            />
            <Legend
              formatter={(value) =>
                value.length > 12 ? value.substring(0, 12) + '...' : value
              }
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Bar Chart */}
      <div className="card">
        <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#374151', marginBottom: '1rem', marginTop: 0 }}>
          Top Categories
        </h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={barData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              dataKey="name"
              tick={{ fontSize: 11, fill: '#64748b' }}
            />
            <YAxis
              tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`}
              tick={{ fontSize: 11, fill: '#64748b' }}
            />
            <Tooltip
              formatter={(value) => {
                if (typeof value === 'number') return [formatINR(value), 'Amount']
                return []
              }}
            />
            <Bar dataKey="amount" radius={[4, 4, 0, 0]}>
              {barData.map((_, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}