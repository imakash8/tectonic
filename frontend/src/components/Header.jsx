import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store'
import './Header.css'

export default function Header() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [showUserMenu, setShowUserMenu] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo" style={{ cursor: 'pointer' }} onClick={() => navigate('/dashboard')}>
          <h1>⚡ Tectonic Trading Platform</h1>
        </div>
        
        {user && (
          <nav className="nav">
            <ul>
              <li><Link to="/dashboard">Dashboard</Link></li>
              <li><Link to="/floor">Trading Floor</Link></li>
              <li><Link to="/trading">Trading</Link></li>
              <li><Link to="/portfolio">Portfolio</Link></li>
              <li><Link to="/analytics">Analytics</Link></li>
              <li><Link to="/watchlist">Watchlist</Link></li>
            </ul>
          </nav>
        )}

        <div className="user-menu">
          {user ? (
            <div className="user-profile">
              <button 
                className="user-button"
                onClick={() => setShowUserMenu(!showUserMenu)}
              >
                👤 {user.email || 'User'}
              </button>
              
              {showUserMenu && (
                <div className="dropdown-menu">
                  <button onClick={handleLogout} className="logout-btn">
                    🚪 Logout
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link to="/login" className="primary">Login</Link>
          )}
        </div>
      </div>
    </header>
  )
}
