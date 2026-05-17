import {
  AreaChart, Area, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'

const tooltipStyle = {
  backgroundColor: 'rgba(15, 22, 41, 0.95)',
  border: '1px solid rgba(0, 212, 255, 0.2)',
  borderRadius: '12px',
  color: '#e5e7eb',
}

export function TimeSeriesChart({ data, dataKey = 'value', color = '#00d4ff', label = 'Value' }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id={`grad-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.4} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis dataKey="hour" stroke="#6b7280" tick={{ fontSize: 10 }} />
        <YAxis stroke="#6b7280" tick={{ fontSize: 10 }} />
        <Tooltip contentStyle={tooltipStyle} />
        <Area type="monotone" dataKey={dataKey} stroke={color} fill={`url(#grad-${dataKey})`} name={label} />
      </AreaChart>
    </ResponsiveContainer>
  )
}

export function ForecastChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis dataKey="timestamp" stroke="#6b7280" tick={{ fontSize: 10 }} tickFormatter={(v) => v?.slice(11, 16) || ''} />
        <YAxis stroke="#6b7280" tick={{ fontSize: 10 }} />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend />
        <Line type="monotone" dataKey="predicted" stroke="#00d4ff" dot={false} name="Predicted" />
        <Line type="monotone" dataKey="lower_bound" stroke="#8b5cf6" strokeDasharray="4 4" dot={false} name="Lower" />
        <Line type="monotone" dataKey="upper_bound" stroke="#8b5cf6" strokeDasharray="4 4" dot={false} name="Upper" />
      </LineChart>
    </ResponsiveContainer>
  )
}

export function DistrictBarChart({ data, dataKey = 'avg_kwh', nameKey = 'name', color = '#00d4ff' }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} layout="vertical" margin={{ left: 80 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis type="number" stroke="#6b7280" tick={{ fontSize: 10 }} />
        <YAxis type="category" dataKey={nameKey} stroke="#6b7280" tick={{ fontSize: 10 }} width={75} />
        <Tooltip contentStyle={tooltipStyle} />
        <Bar dataKey={dataKey} fill={color} radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
