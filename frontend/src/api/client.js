import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('urbanflow_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

client.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('urbanflow_token')
      localStorage.removeItem('urbanflow_user')
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  },
)

export default client

export const auth = {
  login: (email, password) => {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    return client.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  signup: (data) => client.post('/auth/signup', data),
  me: () => client.get('/auth/me'),
}

export const dashboard = {
  overview: () => client.get('/dashboard/overview'),
}

export const maps = {
  zones: () => client.get('/maps/zones'),
}

export const electricity = {
  analytics: (zoneId) => client.get('/electricity/analytics', { params: { zone_id: zoneId } }),
}

export const traffic = {
  analytics: (zoneId) => client.get('/traffic/analytics', { params: { zone_id: zoneId } }),
}

export const water = {
  analytics: (zoneId) => client.get('/water/analytics', { params: { zone_id: zoneId } }),
}

export const alerts = {
  list: (resolved) => client.get('/alerts', { params: { resolved } }),
  resolve: (id) => client.patch(`/alerts/${id}/resolve`),
}

export const predictions = {
  list: () => client.get('/predictions'),
  run: () => client.post('/predictions/run'),
}

export const optimization = {
  list: () => client.get('/optimization/recommendations'),
  generate: () => client.post('/optimization/generate'),
}

export const admin = {
  stats: () => client.get('/admin/stats'),
  users: () => client.get('/admin/users'),
  sqlReports: () => client.get('/admin/sql-reports'),
  health: () => client.get('/admin/system-health'),
}

export const chatbot = {
  ask: (message) => client.post('/chatbot/ask', { message }),
}
