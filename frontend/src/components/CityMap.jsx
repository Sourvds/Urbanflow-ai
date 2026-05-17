import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

const getColor = (type, value) => {
  if (type === 'congestion') return value > 0.7 ? '#ef4444' : value > 0.5 ? '#f59e0b' : '#10b981'
  if (type === 'aqi') return value > 100 ? '#ef4444' : value > 75 ? '#f59e0b' : '#10b981'
  return value > 1500 ? '#8b5cf6' : '#00d4ff'
}

export default function CityMap({ zones = [], overlay = 'electricity', height = '400px' }) {
  const center = zones.length
    ? [zones.reduce((s, z) => s + z.latitude, 0) / zones.length, zones.reduce((s, z) => s + z.longitude, 0) / zones.length]
    : [40.7128, -74.006]

  const getValue = (z) => {
    if (overlay === 'traffic') return z.congestion
    if (overlay === 'water') return z.water_liters / 100000
    if (overlay === 'aqi') return z.aqi
    return z.electricity_kwh
  }

  return (
    <div className="glass overflow-hidden rounded-2xl" style={{ height }}>
      <MapContainer center={center} zoom={11} style={{ height: '100%', width: '100%' }} scrollWheelZoom>
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        {zones.map((z) => {
          const val = getValue(z)
          const radius = Math.max(8, Math.min(25, val / (overlay === 'traffic' ? 0.04 : 80)))
          return (
            <CircleMarker
              key={z.id}
              center={[z.latitude, z.longitude]}
              radius={radius}
              pathOptions={{
                color: getColor(overlay === 'traffic' ? 'congestion' : overlay === 'aqi' ? 'aqi' : 'default', val),
                fillColor: getColor(overlay === 'traffic' ? 'congestion' : overlay === 'aqi' ? 'aqi' : 'default', val),
                fillOpacity: 0.6,
                weight: 2,
              }}
            >
              <Popup>
                <div className="text-gray-900 text-sm">
                  <strong>{z.name}</strong> ({z.sector_code})
                  <br />Efficiency: {z.efficiency_score}
                  <br />Alerts: {z.alert_count}
                </div>
              </Popup>
            </CircleMarker>
          )
        })}
      </MapContainer>
    </div>
  )
}
