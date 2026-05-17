import { useEffect, useState } from 'react'
import { ForecastChart, TimeSeriesChart, DistrictBarChart } from '../components/Charts'
import CityMap from '../components/CityMap'
import { maps } from '../api/client'

export default function ModulePage({ title, subtitle, color, fetchAnalytics, mapOverlay, barKey, barNameKey }) {
  const [data, setData] = useState(null)
  const [zones, setZones] = useState([])

  useEffect(() => {
    Promise.all([fetchAnalytics(), maps.zones()])
      .then(([a, z]) => {
        setData(a.data)
        setZones(z.data)
      })
      .catch(console.error)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (!data) {
    return <div className="flex justify-center h-64"><div className="w-10 h-10 border-2 border-cyber-500 border-t-transparent rounded-full animate-spin" /></div>
  }

  const hourly = (data.hourly_series || []).map((h) => ({ hour: h.hour?.slice(-5) || h.hour, value: h.value }))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-white">{title}</h1>
        <p className="text-gray-500 mt-1">{subtitle}</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries(data.summary || {}).map(([k, v]) => (
          <div key={k} className="glass p-4">
            <p className="text-xs text-gray-500 uppercase">{k.replace(/_/g, ' ')}</p>
            <p className="text-xl font-display mt-1" style={{ color }}>{typeof v === 'number' ? (v < 1 && v > 0 ? `${(v * 100).toFixed(1)}%` : v.toLocaleString()) : v}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="glass p-6">
          <h3 className="font-display text-sm text-gray-400 mb-4">HOURLY TREND</h3>
          <TimeSeriesChart data={hourly} color={color} />
        </div>
        <div className="glass p-6">
          <h3 className="font-display text-sm text-gray-400 mb-4">24H AI FORECAST</h3>
          <ForecastChart data={data.forecasts || []} />
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="glass p-6">
          <h3 className="font-display text-sm text-gray-400 mb-4">DISTRICT BREAKDOWN</h3>
          <DistrictBarChart data={data.district_breakdown || []} dataKey={barKey} nameKey={barNameKey} color={color} />
        </div>
        <div className="glass p-6">
          <h3 className="font-display text-sm text-gray-400 mb-4">AI RECOMMENDATIONS</h3>
          <ul className="space-y-2 max-h-72 overflow-y-auto">
            {(data.recommendations || []).map((r, i) => (
              <li key={i} className="p-3 rounded-xl bg-white/5 text-sm text-gray-300">{typeof r === 'string' ? r : r.recommendation}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="glass p-6">
        <h3 className="font-display text-sm text-gray-400 mb-4">CITY MAP</h3>
        <CityMap zones={zones} overlay={mapOverlay} height="380px" />
      </div>

      {(data.anomalies?.length > 0) && (
        <div className="glass p-6">
          <h3 className="font-display text-sm text-rose-400 mb-4">ANOMALY DETECTION</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {data.anomalies.map((a, i) => (
              <div key={i} className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-sm">
                Value: {a.value?.toFixed?.(2) ?? a.value} — Severity: {a.severity}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
