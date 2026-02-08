import { useState } from 'react'
import { Link } from 'react-router-dom'
import './Sidebar.css'

export default function Sidebar() {
  const [isMobileOpen, setIsMobileOpen] = useState(false)

  return (
    <>
      {/* Mobile toggle button */}
      <button 
        className="mobile-sidebar-toggle"
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        style={{ display: 'none' }}
      >
        ☰
      </button>

      <aside className={`sidebar ${isMobileOpen ? 'mobile-open' : ''}`}>
        <div className="sidebar-content">
          <div className="sidebar-section">
            <h3>Navigation</h3>
            <ul>
              <li><Link to="/dashboard" onClick={() => setIsMobileOpen(false)}>📊 Dashboard</Link></li>
              <li><Link to="/trading" onClick={() => setIsMobileOpen(false)}>🎯 Trading</Link></li>
              <li><Link to="/floor" onClick={() => setIsMobileOpen(false)}>🏛️ Trading Floor</Link></li>
              <li><Link to="/portfolio" onClick={() => setIsMobileOpen(false)}>💼 Portfolio</Link></li>
              <li><Link to="/analytics" onClick={() => setIsMobileOpen(false)}>📈 Analytics</Link></li>
              <li><Link to="/watchlist" onClick={() => setIsMobileOpen(false)}>⭐ Watchlist</Link></li>
            </ul>
          </div>
          
          <div className="sidebar-section">
            <h3>Tools</h3>
            <ul>
              <li><Link to="/settings" onClick={() => setIsMobileOpen(false)}>⚙️ Settings</Link></li>
              <li><Link to="/help" onClick={() => setIsMobileOpen(false)}>❓ Help</Link></li>
              <li><Link to="/docs" onClick={() => setIsMobileOpen(false)}>📚 Documentation</Link></li>
            </ul>
          </div>
        
        <div className="sidebar-section status">
          <h3>Status</h3>
          <div className="status-item">
            <span className="status-indicator">●</span>
            <span>API Connected</span>
          </div>
          <div className="status-item">
            <span className="status-indicator">●</span>
            <span>Markets Open</span>
          </div>
        </div>
      </div>
    </aside>
    </>
  )
}
