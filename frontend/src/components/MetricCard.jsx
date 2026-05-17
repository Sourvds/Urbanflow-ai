import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown } from 'lucide-react'

export default function MetricCard({ label, value, unit, change, trend, icon: Icon, delay = 0 }) {
  const up = trend === 'up'
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="glass-hover p-5 relative overflow-hidden group"
    >
      <div className="absolute top-0 right-0 w-24 h-24 bg-cyber-500/5 rounded-full blur-2xl group-hover:bg-cyber-500/10 transition-colors" />
      <div className="flex items-start justify-between mb-3">
        {Icon && (
          <div className="p-2 rounded-lg bg-cyber-500/10 text-cyber-500">
            <Icon size={20} />
          </div>
        )}
        {change != null && (
          <span className={`flex items-center gap-1 text-xs ${up ? 'text-emerald-400' : 'text-rose-400'}`}>
            {up ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            {Math.abs(change)}%
          </span>
        )}
      </div>
      <p className="text-xs text-gray-500 uppercase tracking-wider">{label}</p>
      <p className="text-2xl font-display font-semibold mt-1 metric-glow text-white">
        {typeof value === 'number' ? value.toLocaleString() : value}
        <span className="text-sm text-gray-500 ml-1 font-sans">{unit}</span>
      </p>
    </motion.div>
  )
}
