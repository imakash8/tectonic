import { create } from 'zustand'

export const useTradeStore = create((set) => ({
  trades: [],
  selectedTrade: null,
  loading: false,
  error: null,
  
  setTrades: (trades) => set({ trades }),
  setSelectedTrade: (trade) => set({ selectedTrade: trade }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  
  addTrade: (trade) => set((state) => ({
    trades: [...state.trades, trade],
  })),
  
  updateTrade: (id, updates) => set((state) => ({
    trades: state.trades.map((t) => (t.id === id ? { ...t, ...updates } : t)),
  })),
  
  removeTrade: (id) => set((state) => ({
    trades: state.trades.filter((t) => t.id !== id),
  })),
}))

export const usePortfolioStore = create((set) => ({
  portfolios: [],
  selectedPortfolio: null,
  loading: false,
  
  setPortfolios: (portfolios) => set({ portfolios }),
  setSelectedPortfolio: (portfolio) => set({ selectedPortfolio: portfolio }),
  setLoading: (loading) => set({ loading }),
  
  addPortfolio: (portfolio) => set((state) => ({
    portfolios: [...state.portfolios, portfolio],
  })),
  
  updatePortfolio: (id, updates) => set((state) => ({
    portfolios: state.portfolios.map((p) => (p.id === id ? { ...p, ...updates } : p)),
  })),
}))

export const useMarketStore = create((set) => ({
  marketData: {},
  indices: {},
  loading: false,
  
  setMarketData: (data) => set({ marketData: data }),
  setIndices: (indices) => set({ indices }),
  setLoading: (loading) => set({ loading }),
}))

export const useAuthStore = create((set) => ({
  user: null,
  token: null,
  loading: false,

  setUser: (user) => set({ user }),
  setToken: (token) => {
    if (token) {
      localStorage.setItem('access_token', token)
    }
    set({ token })
  },
  
  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_id')
    set({ user: null, token: null })
  },

  initializeAuth: () => {
    const token = localStorage.getItem('access_token')
    const userId = localStorage.getItem('user_id')
    
    if (token && userId) {
      set({ 
        token,
        user: { id: userId }
      })
    }
  },

  setLoading: (loading) => set({ loading }),
}))
