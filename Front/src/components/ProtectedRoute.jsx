import { Navigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function ProtectedRoute({ children }) {
  const { session, carregando } = useAuth()
  if (carregando) return <div className="centro">Carregando…</div>
  if (!session) return <Navigate to="/login" replace />
  return children
}
