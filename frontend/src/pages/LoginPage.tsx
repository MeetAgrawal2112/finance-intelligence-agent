// src/pages/LoginPage.tsx — poora replace karo
import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { TrendingUp, Mail, Lock, Loader2, Eye, EyeOff } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { toast } from '../store/toastStore'

const loginSchema = z.object({
  email: z.string().email('Valid email chahiye'),
  password: z.string().min(8, 'Password minimum 8 characters'),
})

type LoginForm = z.infer<typeof loginSchema>

export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, isLoading } = useAuthStore()
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')

  // Register page se aaye? Success message dikhao
  const justRegistered = new URLSearchParams(location.search).get('registered')

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginForm) => {
    setError('')
    try {
      await login(data.email, data.password)
      toast.success('Login successful!', 'Welcome back 👋')
      navigate('/dashboard')
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Login failed. Please try again.'
      setError(msg)
      toast.error('Login failed', msg)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f0f9ff 0%, #e2e8f0 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem',
    }}>
      <div style={{ width: '100%', maxWidth: '420px' }}>

        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '64px',
            height: '64px',
            background: '#0284c7',
            borderRadius: '1rem',
            marginBottom: '1rem',
            boxShadow: '0 8px 24px rgba(2,132,199,0.3)',
          }}>
            <TrendingUp size={32} color="white" />
          </div>
          <h1 style={{
            fontSize: '1.5rem',
            fontWeight: 700,
            color: '#0f172a',
            margin: 0,
          }}>
            Finance Intelligence
          </h1>
          <p style={{ color: '#64748b', marginTop: '0.25rem', fontSize: '0.9rem' }}>
            Apne paison ka AI-powered hisaab
          </p>
        </div>

        {/* Registered success banner */}
        {justRegistered && (
          <div style={{
            background: '#f0fdf4',
            border: '1px solid #86efac',
            borderRadius: '0.75rem',
            padding: '0.75rem 1rem',
            marginBottom: '1rem',
            color: '#15803d',
            fontSize: '0.875rem',
            textAlign: 'center',
          }}>
            ✅ Account ban gaya! Ab login karo.
          </div>
        )}

        {/* Card */}
        <div className="card">
          <h2 style={{
            fontSize: '1.25rem',
            fontWeight: 600,
            color: '#0f172a',
            marginBottom: '1.5rem',
            marginTop: 0,
          }}>
            Login karo
          </h2>

          {/* Error */}
          {error && (
            <div style={{
              background: '#fff1f2',
              border: '1px solid #fca5a5',
              borderRadius: '0.75rem',
              padding: '0.75rem 1rem',
              marginBottom: '1rem',
              color: '#dc2626',
              fontSize: '0.875rem',
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)}>

            {/* Email */}
            <div style={{ marginBottom: '1rem' }}>
              <label className="label">Email</label>
              <div style={{ position: 'relative' }}>
                <Mail
                  size={16}
                  color="#94a3b8"
                  style={{
                    position: 'absolute',
                    left: '0.875rem',
                    top: '50%',
                    transform: 'translateY(-50%)',
                  }}
                />
                <input
                  {...register('email')}
                  type="email"
                  placeholder="rahul@example.com"
                  className="input-field"
                  style={{ paddingLeft: '2.5rem' }}
                />
              </div>
              {errors.email && (
                <p style={{
                  color: '#ef4444',
                  fontSize: '0.75rem',
                  marginTop: '0.25rem',
                  margin: '0.25rem 0 0',
                }}>
                  {errors.email.message}
                </p>
              )}
            </div>

            {/* Password */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label className="label">Password</label>
              <div style={{ position: 'relative' }}>
                <Lock
                  size={16}
                  color="#94a3b8"
                  style={{
                    position: 'absolute',
                    left: '0.875rem',
                    top: '50%',
                    transform: 'translateY(-50%)',
                  }}
                />
                <input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  className="input-field"
                  style={{ paddingLeft: '2.5rem', paddingRight: '2.5rem' }}
                />
                {/* Show/hide password toggle */}
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '0.875rem',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#94a3b8',
                    padding: 0,
                    display: 'flex',
                  }}
                >
                  {showPassword
                    ? <EyeOff size={16} />
                    : <Eye size={16} />
                  }
                </button>
              </div>
              {errors.password && (
                <p style={{
                  color: '#ef4444',
                  fontSize: '0.75rem',
                  margin: '0.25rem 0 0',
                }}>
                  {errors.password.message}
                </p>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                fontSize: '0.9rem',
              }}
            >
              {isLoading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Logging in...
                </>
              ) : 'Login'}
            </button>
          </form>

          <p style={{
            textAlign: 'center',
            fontSize: '0.875rem',
            color: '#64748b',
            marginTop: '1rem',
            marginBottom: 0,
          }}>
            Account nahi hai?{' '}
            <Link
              to="/register"
              style={{
                color: '#0284c7',
                fontWeight: 500,
                textDecoration: 'none',
              }}
            >
              Register karo
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}