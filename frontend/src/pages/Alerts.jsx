import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Bell, CheckCircle } from 'lucide-react'
import { alerts as alertsApi } from '../api/client'

const priorityColors = {
  critical: 'border-rose-500/50 bg-rose-500/10 text-rose-400',
  high: 'border-orange-500/50 bg-orange-500/10 text-orange-400',
  medium: 'border-amber-500/50 bg-amber-500/10 text-amber-400',
  low: 'border-gray-500/50 bg-gray-500/10 text-gray-400',
}

export default function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [filter, setFilter] = useState('active')

  const load = () => {
    const resolved = filter === 'resolved' ? true : filter === 'active' ? false : undefined
    alertsApi.list(resolved).then((r) => setAlerts(r.data)).catch(console.error)
  }

  useEffect(load, [filter])

  const resolve = async (id) => {
    await alertsApi.resolve(id)
    load()
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold flex items-center gap-2">
          <Bell className="text-cyber-500" /> Alert Center
        </h1>
        <p className="text-gray-500 mt-1">Real-time notifications and incident history</p>
      </div>
      <div className="flex gap-2">
        {['active', 'resolved', 'all'].map((f) => (
          <button key={f} onClick={() => setFilter(f)} className={`px-4 py-2 rounded-lg text-sm capitalize ${filter === f ? 'bg-cyber-500/20 text-cyber-500' : 'bg-white/5 text-gray-400'}`}>
            {f}
          </button>
        ))}
      </div>
      <div className="space-y-3">
        {alerts.map((a) => (
          <motion.div key={a.id} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className={`glass p-5 border-l-4 ${priorityColors[a.priority] || priorityColors.medium}`}>
            <div className="flex justify-between items-start gap-4">
              <div>
                <div className="flex gap-2 mb-2">
                  <span className="text-xs uppercase tracking-wider">{a.alert_type}</span>
                  <span className="text-xs uppercase">{a.priority}</span>
                </div>
                <h3 className="font-semibold text-white">{a.title}</h3>
                <p className="text-sm text-gray-400 mt-1">{a.message}</p>
                {a.zone_name && <p className="text-xs text-cyber-500 mt-2">Zone: {a.zone_name}</p>}
              </div>
              {!a.is_resolved && (
                <button onClick={() => resolve(a.id)} className="btn-ghost flex items-center gap-1 text-emerald-400 shrink-0">
                  <CheckCircle size={16} /> Resolve
                </button>
              )}
            </div>
            <p className="text-xs text-gray-600 mt-3">{new Date(a.created_at).toLocaleString()}</p>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
