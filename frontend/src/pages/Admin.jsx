import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Shield, Users, Database, Activity } from 'lucide-react'
import { admin as adminApi, predictions, optimization } from '../api/client'

export default function Admin() {
  const [stats, setStats] = useState(null)
  const [health, setHealth] = useState(null)
  const [users, setUsers] = useState([])
  const [reports, setReports] = useState(null)

  useEffect(() => {
    Promise.all([
      adminApi.stats(),
      adminApi.health(),
      adminApi.users(),
      adminApi.sqlReports(),
    ]).then(([s, h, u, r]) => {
      setStats(s.data)
      setHealth(h.data)
      setUsers(u.data)
      setReports(r.data)
    }).catch(console.error)
  }, [])

  const runPredictions = () => predictions.run().then(() => alert('Predictions generated'))
  const runOptimization = () => optimization.generate().then((r) => alert(`Generated ${r.data.generated} recommendations`))

  if (!stats) return <div className="flex justify-center h-64"><div className="w-10 h-10 border-2 border-cyber-500 border-t-transparent rounded-full animate-spin" /></div>

  const statCards = [
    { label: 'Users', value: stats.users, icon: Users },
    { label: 'Zones', value: stats.zones, icon: Database },
    { label: 'Active Alerts', value: stats.active_alerts, icon: Activity },
    { label: 'Predictions', value: stats.predictions, icon: Shield },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold flex items-center gap-2">
          <Shield className="text-purple-400" /> Admin Command Panel
        </h1>
        <p className="text-gray-500 mt-1">System health, users, and AI pipeline management</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map(({ label, value, icon: Icon }) => (
          <div key={label} className="glass p-5">
            <Icon className="text-purple-400 mb-2" size={22} />
            <p className="text-xs text-gray-500">{label}</p>
            <p className="text-2xl font-display">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass p-6">
          <h3 className="font-display text-sm text-gray-400 mb-4">SYSTEM HEALTH</h3>
          <p className={`text-lg font-semibold ${health?.status === 'healthy' ? 'text-emerald-400' : 'text-amber-400'}`}>
            {health?.status?.toUpperCase()} — {health?.uptime_percent}% uptime
          </p>
          <p className="text-sm text-gray-500 mt-2">Active sensors: {health?.active_sensors} | Failed: {health?.failed_sensors}</p>
          <div className="mt-4 flex gap-2">
            <button onClick={runPredictions} className="btn-primary text-sm">Run ML Predictions</button>
            <button onClick={runOptimization} className="btn-ghost border border-white/10 text-sm">Generate Optimizations</button>
          </div>
        </div>
        <div className="glass p-6">
          <h3 className="font-display text-sm text-gray-400 mb-4">USER MANAGEMENT</h3>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {users.map((u) => (
              <div key={u.id} className="flex justify-between p-2 rounded-lg bg-white/5 text-sm">
                <span>{u.full_name}</span>
                <span className="text-cyber-500 capitalize">{u.role?.replace('_', ' ')}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {reports && (
        <div className="glass p-6">
          <h3 className="font-display text-sm text-gray-400 mb-4">SQL ANALYTICS REPORTS</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-cyber-500 mb-2">District Energy (30d)</p>
              <pre className="bg-black/30 p-3 rounded-lg overflow-auto max-h-40 text-xs">{JSON.stringify(reports.district_energy?.slice(0, 5), null, 2)}</pre>
            </div>
            <div>
              <p className="text-cyber-500 mb-2">Prediction Accuracy</p>
              <pre className="bg-black/30 p-3 rounded-lg overflow-auto max-h-40 text-xs">{JSON.stringify(reports.prediction_accuracy, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
