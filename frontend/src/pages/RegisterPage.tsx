// src/pages/RegisterPage.tsx — poora replace karo
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  TrendingUp, Mail, Lock, User,
  Loader2, Eye, EyeOff
} from 'lucide-react'
import { authApi } from '../api/auth'
import { toast } from '../store/toastStore'

const registerSchema = z.object({
  full_name: z.string().min(2, 'Naam minimum 2 characters'),
  email: z.string().email('Valid email chahiye'),
  password: z.string().min(8, 'Password minimum 8 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords match nahi kar rahe',
  path: ['confirmPassword'],
})

type RegisterForm = z.infer<typeof registerSchema>

export default function RegisterPage() {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = async (data: RegisterForm) => {
    setError('')
    setIsLoading(true)
    try {
      await authApi.register({
        full_name: data.full_name,
        email: data.email,
        password: data.password,
      })
      toast.success('Account ban gaya!', 'Ab login karo.')
      navigate('/login?registered=true')
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Registration failed.'
      setError(msg)
      toast.error('Registration failed', msg)
    } finally {
      setIsLoading(false)
    }
  }

  const inputGroup = (
    label: string,
    name: keyof RegisterForm,
    type: string,
    placeholder: string,
    icon: React.ReactNode,
    extraRight?: React.ReactNode
  ) => (
    <div style={{ marginBottom: '1rem' }}>
      <label className="label">{label}</label>
      <div style={{ position: 'relative' }}>
        <span style={{
          position: 'absolute',
          left: '0.875rem',
          top: '50%',
          transform: 'translateY(-50%)',
          color: '#94a3b8',
          display: 'flex',
        }}>
          {icon}
        </span>
        <input
          {...register(name)}
          type={type}
          placeholder={placeholder}
          className="input-field"
          style={{
            paddingLeft: '2.5rem',
            paddingRight: extraRight ? '2.5rem' : '1rem',
          }}
        />
        {extraRight && (
          <span style={{
            position: 'absolute',
            right: '0.875rem',
            top: '50%',
            transform: 'translateY(-50%)',
          }}>
            {extraRight}
          </span>
        )}
      </div>
      {errors[name] && (
        <p style={{
          color: '#ef4444',
          fontSize: '0.75rem',
          margin: '0.25rem 0 0',
        }}>
          {errors[name]?.message}
        </p>
      )}
    </div>
  )

  const toggleBtn = (
    <button
      type="button"
      onClick={() => setShowPassword(!showPassword)}
      style={{
        background: 'none',
        border: 'none',
        cursor: 'pointer',
        color: '#94a3b8',
        padding: 0,
        display: 'flex',
      }}
    >
      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
    </button>
  )

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
          <p style={{
            color: '#64748b',
            marginTop: '0.25rem',
            fontSize: '0.9rem',
          }}>
            Account banao — free mein!
          </p>
        </div>

        {/* Card */}
        <div className="card">
          <h2 style={{
            fontSize: '1.25rem',
            fontWeight: 600,
            color: '#0f172a',
            marginBottom: '1.5rem',
            marginTop: 0,
          }}>
            Register karo
          </h2>

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
            {inputGroup(
              'Poora Naam', 'full_name', 'text',
              'Rahul Sharma', <User size={16} />
            )}
            {inputGroup(
              'Email', 'email', 'email',
              'rahul@example.com', <Mail size={16} />
            )}
            {inputGroup(
              'Password', 'password',
              showPassword ? 'text' : 'password',
              'Minimum 8 characters',
              <Lock size={16} />,
              toggleBtn
            )}
            {inputGroup(
              'Password Confirm Karo', 'confirmPassword',
              showPassword ? 'text' : 'password',
              'Same password dobara',
              <Lock size={16} />
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary"
              style={{
                marginTop: '0.5rem',
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
                  Creating account...
                </>
              ) : 'Account Banao'}
            </button>
          </form>

          <p style={{
            textAlign: 'center',
            fontSize: '0.875rem',
            color: '#64748b',
            marginTop: '1rem',
            marginBottom: 0,
          }}>
            Pehle se account hai?{' '}
            <Link
              to="/login"
              style={{
                color: '#0284c7',
                fontWeight: 500,
                textDecoration: 'none',
              }}
            >
              Login karo
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}