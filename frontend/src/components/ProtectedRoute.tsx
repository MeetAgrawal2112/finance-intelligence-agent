// src/components/ProtectedRoute.tsx
import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function ProtectedRoute() {
  const { isAuthenticated } = useAuthStore()

  // Token hai? Dashboard dikhao. Nahi? Login pe bhejo.
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />
}