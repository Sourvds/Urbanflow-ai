import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Zap, Car, Droplets, Wind, Activity, AlertTriangle, Leaf, Sparkles } from 'lucide-react'
import MetricCard from '../components/MetricCard'
import CityMap from '../components/CityMap'
import { TimeSeriesChart } from '../components/Charts'
import { dashboard, maps } from '../api/client'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [zones, setZones] = useState([])
  const [mapOverlay, setMapOverlay] = useState('electricity')

  useEffect(() => {
    Promise.all([dashboard.overview(), maps.zones()])
      .then(([d, z]) => {
        setData(d.data)
        setZones(z.data)
      })
      .catch(console.error)
  }, [])

  if (!data) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-10 h-10 border-2 border-cyber-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const chartData = data.metrics?.map((m, i) => ({
    hour: m.label,
    value: m.value,
  })) || []

  return (
    <div className="space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl lg:text-3xl font-bold text-white">
            Smart City <span className="gradient-text">Command Center</span>
          </h1>
          <p className="text-gray-500 mt-1">Real-time AI analytics across all urban systems</p>
        </div>
        <motion.div className="glass px-6 py-3 flex items-center gap-4">
          <Sparkles className="text-cyber-500" size={24} />
          <div>
            <p className="text-xs text-gray-500">City Efficiency Score</p>
            <p className="text-3xl font-display font-bold text-cyber-500">{data.city_efficiency_score}</p>
          </div>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <MetricCard label="Electricity" value={data.electricity_kwh} unit="kWh" change={2.4} trend="up" icon={Zap} delay={0} />
        <MetricCard label="Traffic Load" value={(data.traffic_congestion * 100).toFixed(1)} unit="%" change={1.2} trend="down" icon={Car} delay={0.05} />
        <MetricCard label="Water" value={data.water_liters} unit="L" change={0.8} trend="up" icon={Droplets} delay={0.1} />
        <MetricCard label="Air Quality" value={data.air_quality_index} unit="AQI" change={3.1} trend="down" icon={Wind} delay={0.15} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <MetricCard label="Energy Efficiency" value={data.energy_efficiency_score} unit="/100" icon={Activity} delay={0.2} />
        <MetricCard label="Active Alerts" value={data.active_alerts} unit="" icon={AlertTriangle} delay={0.25} />
        <MetricCard label="Carbon Estimate" value={data.carbon_emission_tons} unit="tons" icon={Leaf} delay={0.3} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 glass p-6">
          <h3 className="font-display text-sm text-gray-400 mb-4">RESOURCE OVERVIEW</h3>
          <TimeSeriesChart data={chartData} dataKey="value" label="Usage" />
        </div>
        <div className="glass p-6">
          <h3 className="font-display text-sm text-gray-400 mb-4">AI RECOMMENDATIONS</h3>
          <ul className="space-y-3 max-h-72 overflow-y-auto">
            {data.recommendations?.map((r) => (
              <li key={r.id} className="p-3 rounded-xl bg-white/5 border border-white/5 text-sm">
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  r.priority === 'high' ? 'bg-rose-500/20 text-rose-400' : 'bg-cyber-500/20 text-cyber-400'
                }`}>{r.priority}</span>
                <p className="mt-2 text-gray-300">{r.recommendation}</p>
                <p className="text-xs text-emerald-400 mt-1">Save ~{r.expected_savings_percent}%</p>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="glass p-6">
        <div className="flex flex-wrap gap-2 mb-4">
          {['electricity', 'traffic', 'water', 'aqi'].map((o) => (
            <button
              key={o}
              onClick={() => setMapOverlay(o)}
              className={`px-4 py-1.5 rounded-lg text-xs uppercase tracking-wider ${
                mapOverlay === o ? 'bg-cyber-500/20 text-cyber-500 border border-cyber-500/40' : 'bg-white/5 text-gray-400'
              }`}
            >
              {o}
            </button>
          ))}
        </div>
        <CityMap zones={zones} overlay={mapOverlay} height="420px" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass p-6">
          <h3 className="font-display text-sm text-gray-400 mb-4">DISTRICT RANKINGS</h3>
          <div className="space-y-2">
            {data.district_rankings?.map((d) => (
              <div key={d.zone_id} className="flex items-center gap-4 p-3 rounded-xl bg-white/5">
                <span className="font-display text-cyber-500 w-8">#{d.rank}</span>
                <div className="flex-1">
                  <p className="font-medium">{d.name}</p>
                  <p className="text-xs text-gray-500">{d.sector_code}</p>
                </div>
                <div className="text-right">
                  <p className="text-cyber-500 font-display">{d.efficiency_score}</p>
                  <p className="text-xs text-gray-500">efficiency</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="glass p-6">
          <h3 className="font-display text-sm text-gray-400 mb-4">LIVE ACTIVITY FEED</h3>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {data.recent_activity?.map((a) => (
              <div key={a.id} className="flex gap-3 text-sm border-l-2 border-cyber-500/30 pl-3">
                <span className="text-xs text-gray-600 whitespace-nowrap">
                  {new Date(a.created_at).toLocaleTimeString()}
                </span>
                <div>
                  <p className="text-gray-300">{a.message}</p>
                  <p className="text-xs text-gray-500">{a.component}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
