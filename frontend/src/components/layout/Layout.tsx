// src/components/layout/Layout.tsx
import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'

export default function Layout() {
  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>
      <Navbar />
      <main>
        <Outlet />
      </main>
    </div>
  )
}