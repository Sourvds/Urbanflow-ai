import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Zap, Loader2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const [email, setEmail] = useState('admin@urbanflow.ai')
  const [password, setPassword] = useState('UrbanFlow2026!')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login, user } = useAuth()
  const navigate = useNavigate()

  if (user) {
    navigate('/')
    return null
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const D = 'div'
  const Wrapper = D

  return (
    <Wrapper className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md glass p-8"
      >
        <Wrapper className="text-center mb-8">
          <Wrapper className="inline-flex p-3 rounded-2xl bg-cyber-500/10 text-cyber-500 mb-4">
            <Zap size={32} />
          </Wrapper>
          <h1 className="font-display text-2xl font-bold gradient-text">URBANFLOW AI</h1>
          <p className="text-gray-500 text-sm mt-2">Smart City Resource Optimization</p>
        </Wrapper>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Wrapper>
            <label className="text-xs text-gray-500 uppercase tracking-wider">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full mt-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-cyber-500/50 outline-none transition-colors"
              required
            />
          </Wrapper>
          <Wrapper>
            <label className="text-xs text-gray-500 uppercase tracking-wider">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full mt-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-cyber-500/50 outline-none transition-colors"
              required
            />
          </Wrapper>
          {error && <p className="text-rose-400 text-sm">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
            {loading ? <Loader2 className="animate-spin" size={20} /> : 'Access Command Center'}
          </button>
        </form>
        <p className="text-xs text-gray-600 text-center mt-6">
          Demo: admin@urbanflow.ai / UrbanFlow2026!
        </p>
      </motion.div>
    </Wrapper>
  )
}
