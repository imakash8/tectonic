import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store'

export default function ProtectedRoute({ children }) {
  const { token, loading } = useAuthStore()

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <p>Loading...</p>
      </div>
    )
  }

  if (!token) {
    return <Navigate to="/login" replace />
  }

  return children
}
