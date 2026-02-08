import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// Authenticated API client (includes auth token)
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Public API client (for unauthenticated endpoints like market data)
const publicApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor: Add authentication token only to authenticated requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor: Handle token refresh and errors for authenticated requests
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Handle 401 Unauthorized - try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        // Try using refresh token first, then fall back to access token
        const refreshToken = localStorage.getItem('refresh_token') || localStorage.getItem('access_token')
        
        if (refreshToken) {
          const refreshResponse = await axios.post(
            `${API_BASE_URL}/auth/refresh`,
            { refresh_token: refreshToken }
          )
          
          const { access_token } = refreshResponse.data
          localStorage.setItem('access_token', access_token)
          
          // Also save refresh token if returned
          if (refreshResponse.data.refresh_token) {
            localStorage.setItem('refresh_token', refreshResponse.data.refresh_token)
          }
          
          // Update original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } else {
          // No tokens available, redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          return Promise.reject(error)
        }
      } catch (refreshError) {
        // Refresh failed, logout user and redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    // Handle 429 Too Many Requests (Rate limiting)
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'] || 60
      console.warn(`Rate limited. Retry after ${retryAfter} seconds`)
    }

    // Handle 500+ Server errors
    if (error.response?.status >= 500) {
      console.error('Server error:', error.response.status)
    }

    return Promise.reject(error)
  }
)

// Response interceptor for public API (no token refresh)
publicApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status >= 500) {
      console.error('Server error:', error.response.status)
    }
    return Promise.reject(error)
  }
)

export const apiService = {
  // === Authentication ===
  register: (email, password) => 
    api.post('/auth/register', { email, password }),
  
  login: (email, password) => 
    api.post('/auth/login', { email, password }),
  
  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  },
  
  getCurrentUser: () => 
    api.get('/auth/me'),
  
  refreshToken: (refreshToken) => 
    api.post('/auth/refresh', { refresh_token: refreshToken }),
  
  updateProfile: (data) => 
    api.put('/auth/profile', data),
  
  changePassword: (oldPassword, newPassword) => 
    api.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword }),

  // === Market Data (Public - no auth required) ===
  getQuote: (symbol) => 
    publicApi.get(`/market/quote/${symbol}`),
  
  getMarketQuote: (symbol) => 
    publicApi.get(`/market/quote/${symbol}`),
  
  getCompanyProfile: (symbol) => 
    publicApi.get(`/market/profile/${symbol}`),
  
  getMarketOverview: () => 
    publicApi.get('/market/overview'),
  
  getHistoricalData: (symbol, interval = '1d') => 
    publicApi.get(`/market/historical/${symbol}`, { params: { interval } }),
  
  getMarketNews: () => 
    publicApi.get('/market/news'),

  // === Trading ===
  getTradeSignal: (symbol, direction) => 
    api.post('/trading/signal', { symbol, direction }),
  
  executeTrade: (data) => 
    api.post('/trading/execute', data),
  
  executePaperTrade: (data) => 
    api.post('/trading/paper/execute', data),
  
  closeTrade: (tradeId, data) => 
    api.post(`/trading/close/${tradeId}`, data),
  
  getTrades: (filters = {}) => 
    api.get('/trading/trades', { params: filters }),
  
  getTrade: (id) => 
    api.get(`/trading/trades/${id}`),
  
  updateTrade: (id, data) => 
    api.put(`/trading/trades/${id}`, data),
  
  getTradeValidationGates: (tradeData) => 
    api.post('/trading/validate-gates', tradeData),

  // === Portfolio ===
  getPortfolio: (id) => {
    if (id) return api.get(`/portfolio/${id}`)
    return api.get('/portfolio/')
  },
  
  getPortfolios: () => 
    api.get('/portfolio/'),
  
  createPortfolio: (data) => 
    api.post('/portfolio', data),
  
  updatePortfolio: (id, data) => 
    api.put(`/portfolio/${id}`, data),
  
  deletePortfolio: (id) => 
    api.delete(`/portfolio/${id}`),
  
  getPositions: (portfolioId) => 
    api.get(`/portfolio/${portfolioId}/positions`),
  
  getPortfolioHistory: (portfolioId) => 
    api.get(`/portfolio/${portfolioId}/history`),

  // === Analytics ===
  getAnalytics: () => 
    api.get('/analytics/overview'),
  
  getComprehensiveAnalytics: () => 
    api.get('/analytics/comprehensive'),
  
  getPerformance: (timeframe = '1M') => 
    api.get('/analytics/performance', { params: { timeframe } }),
  
  getMonthlyPnL: (portfolioId) => 
    api.get(`/analytics/monthly-pnl/${portfolioId}`),
  
  getTradeStats: (portfolioId) => 
    api.get(`/analytics/trade-stats/${portfolioId}`),
  
  getRiskMetrics: (portfolioId) => 
    api.get(`/analytics/risk-metrics/${portfolioId}`),
  
  getBacktestResults: (strategyId) => 
    api.get(`/analytics/backtest/${strategyId}`),

  // === Settings ===
  getSettings: () => 
    api.get('/settings'),
  
  updateSettings: (data) => 
    api.put('/settings', data),
  
  getNotificationPreferences: () => 
    api.get('/settings/notifications'),
  
  updateNotificationPreferences: (data) => 
    api.put('/settings/notifications', data),

  // === Alerts & Notifications ===
  getAlerts: () => 
    api.get('/alerts'),
  
  createAlert: (data) => 
    api.post('/alerts', data),
  
  deleteAlert: (id) => 
    api.delete(`/alerts/${id}`),
  
  markAlertAsRead: (id) => 
    api.post(`/alerts/${id}/read`),

  // === Backtesting ===
  createBacktest: (data) => 
    api.post('/backtest', data),
  
  getBacktests: () => 
    api.get('/backtest'),
  
  getBacktestDetail: (id) => 
    api.get(`/backtest/${id}`),
  
  runBacktest: (id) => 
    api.post(`/backtest/${id}/run`),
  
  cancelBacktest: (id) => 
    api.post(`/backtest/${id}/cancel`),

  // === Health & Status ===
  getHealth: () => 
    api.get('/health'),
  
  getSystemStatus: () => 
    api.get('/status'),
}

// Export axios instance for custom requests
export { api }
