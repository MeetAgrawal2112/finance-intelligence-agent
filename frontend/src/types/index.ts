// src/types/index.ts
// Yeh backend schemas ke saath match karne chahiye

export interface User {
  id: string
  email: string
  full_name: string
  currency: string
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export type TransactionType = 'debit' | 'credit'
export type TransactionStatus = 'pending' | 'completed' | 'failed' | 'refunded'

export interface Transaction {
  id: string
  amount: number
  currency: string
  transaction_type: TransactionType
  status: TransactionStatus
  description: string
  merchant_name: string | null
  transaction_date: string
  category_id: string | null
  account_id: string | null
  is_anomaly: boolean
  anomaly_score: number
  ml_category_confidence: number
  is_manually_categorized: boolean
  notes: string | null
  created_at: string
}

export interface Category {
  id: string
  name: string
  icon: string
  color: string
  is_system: boolean
}

export interface MonthlySummary {
  month: number
  year: number
  total_income: number
  total_expenses: number
  net_savings: number
  transaction_count: number
  top_category: string | null
}

export interface CategoryAnalytics {
  category_id: string | null
  category_name: string
  total_amount: number
  transaction_count: number
  percentage: number
  avg_transaction: number
}

export interface PaginationInfo {
  total: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface ApiResponse<T> {
  success: boolean
  message: string
  data: T | null
}

export interface TransactionFilters {
  search?: string
  start_date?: string
  end_date?: string
  transaction_type?: TransactionType
  category_id?: string
  anomalies_only?: boolean
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}