import { useAuthStore } from '../store'

export const useAuth = () => {
  const { 
    user, 
    token, 
    setUser, 
    setToken, 
    logout,
    loading 
  } = useAuthStore()

  return {
    user,
    token,
    isAuthenticated: !!token,
    setUser,
    setToken,
    logout,
    loading,
  }
}
