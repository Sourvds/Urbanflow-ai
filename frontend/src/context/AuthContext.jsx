import { createContext, useContext, useState, useEffect } from 'react'
import { auth as authApi } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('urbanflow_user'))
    } catch {
      return null
    }
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('urbanflow_token')
    if (!token) {
      setLoading(false)
      return
    }
    authApi
      .me()
      .then((r) => setUser(r.data))
      .catch(() => {
        localStorage.removeItem('urbanflow_token')
        localStorage.removeItem('urbanflow_user')
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const { data } = await authApi.login(email, password)
    localStorage.setItem('urbanflow_token', data.access_token)
    localStorage.setItem('urbanflow_user', JSON.stringify(data.user))
    setUser(data.user)
    return data.user
  }

  const logout = () => {
    localStorage.removeItem('urbanflow_token')
    localStorage.removeItem('urbanflow_user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, isAdmin: user?.role === 'admin' }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
