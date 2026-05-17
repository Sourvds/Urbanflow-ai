import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard, Zap, Car, Droplets, Bell, MessageSquare,
  Shield, LogOut, Menu, X,
} from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../context/AuthContext'

const nav = [
  { to: '/', icon: LayoutDashboard, label: 'Command Center' },
  { to: '/electricity', icon: Zap, label: 'Electricity' },
  { to: '/traffic', icon: Car, label: 'Traffic' },
  { to: '/water', icon: Droplets, label: 'Water' },
  { to: '/alerts', icon: Bell, label: 'Alerts' },
  { to: '/chatbot', icon: MessageSquare, label: 'AI Assistant' },
]

export default function Layout() {
  const { user, logout, isAdmin } = useAuth()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="min-h-screen flex">
      <aside className={`fixed lg:static inset-y-0 left-0 z-50 w-64 glass border-r border-white/5 flex flex-col transition-transform ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        <div className="p-6 border-b border-white/5">
          <h1 className="font-display text-lg font-bold gradient-text tracking-wider">URBANFLOW</h1>
          <p className="text-xs text-gray-500 mt-1">AI Smart City Platform</p>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          {nav.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                  isActive
                    ? 'bg-cyber-500/15 text-cyber-500 border border-cyber-500/30'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`
              }
            >
              <Icon size={20} />
              <span className="text-sm font-medium">{label}</span>
            </NavLink>
          ))}
          {isAdmin && (
            <NavLink
              to="/admin"
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                  isActive ? 'bg-purple-500/15 text-purple-400 border border-purple-500/30' : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`
              }
            >
              <Shield size={20} />
              <span className="text-sm font-medium">Admin Panel</span>
            </NavLink>
          )}
        </nav>
        <div className="p-4 border-t border-white/5">
          <p className="text-xs text-gray-500 truncate">{user?.email}</p>
          <p className="text-xs text-cyber-500 capitalize mb-3">{user?.role?.replace('_', ' ')}</p>
          <button onClick={logout} className="btn-ghost w-full flex items-center gap-2 justify-center">
            <LogOut size={16} /> Sign out
          </button>
        </div>
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 bg-black/60 z-40 lg:hidden" onClick={() => setMobileOpen(false)} />
      )}

      <main className="flex-1 min-h-screen overflow-auto">
        <header className="sticky top-0 z-30 glass border-b border-white/5 px-4 lg:px-8 py-4 flex items-center justify-between">
          <button className="lg:hidden btn-ghost" onClick={() => setMobileOpen(!mobileOpen)}>
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
          <div className="hidden lg:block">
            <p className="text-xs text-gray-500 uppercase tracking-widest">Live Operations</p>
            <h2 className="font-display text-sm text-gray-300">
              {nav.find((n) => n.to === location.pathname || (n.to !== '/' && location.pathname.startsWith(n.to)))?.label || 'Command Center'}
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs text-emerald-400">Systems Online</span>
          </div>
        </header>
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="p-4 lg:p-8"
        >
          <Outlet />
        </motion.div>
      </main>
    </div>
  )
}
