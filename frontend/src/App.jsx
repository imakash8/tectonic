import { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store'

// Pages
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Trading from './pages/Trading'
import TradingFloor from './pages/TradingFloor'
import Portfolio from './pages/Portfolio'
import Analytics from './pages/Analytics'
import Watchlist from './pages/Watchlist'
import Settings from './pages/Settings'
import Help from './pages/Help'
import Documentation from './pages/Documentation'

// Components
import Header from './components/Header'
import Sidebar from './components/Sidebar'

import './App.css'

function App() {
  const token = useAuthStore((state) => state.token)
  const initializeAuth = useAuthStore((state) => state.initializeAuth)

  useEffect(() => {
    initializeAuth()
  }, [initializeAuth])

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      {token ? (
        <div className="app-container">
          <Header />
          <div className="main-content">
            <Sidebar />
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/floor" element={<TradingFloor />} />
              <Route path="/trading" element={<Trading />} />
              <Route path="/portfolio" element={<Portfolio />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/watchlist" element={<Watchlist />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/help" element={<Help />} />
              <Route path="/docs" element={<Documentation />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </div>
        </div>
      ) : (
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      )}
    </Router>
  )
}

export default App
