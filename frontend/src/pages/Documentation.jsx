import { useNavigate } from 'react-router-dom'
import '../pages/Dashboard.css'

export default function Documentation() {
  const navigate = useNavigate()

  return (
    <div className="dashboard">
      <div className="header-section">
        <button 
          onClick={() => navigate('/dashboard')}
          style={{ 
            marginBottom: '20px', 
            padding: '8px 16px', 
            backgroundColor: '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px', 
            cursor: 'pointer' 
          }}
        >
          ← Back to Dashboard
        </button>
        <h1>📚 Documentation</h1>
      </div>

      <div style={{ backgroundColor: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <div style={{ marginBottom: '20px', paddingBottom: '20px', borderBottom: '1px solid #eee' }}>
          <h3>Getting Started</h3>
          <p>Welcome to Tectonic Trading Platform. This documentation covers all features and API endpoints.</p>
          <ul style={{ marginLeft: '20px', marginTop: '10px' }}>
            <li>Account Setup and Authentication</li>
            <li>Portfolio Management</li>
            <li>Trading Fundamentals</li>
            <li>Market Analysis Tools</li>
          </ul>
        </div>

        <div style={{ marginBottom: '20px', paddingBottom: '20px', borderBottom: '1px solid #eee' }}>
          <h3>API Reference</h3>
          <p>Complete REST API documentation for integrating with external systems.</p>
          <ul style={{ marginLeft: '20px', marginTop: '10px' }}>
            <li>Authentication Endpoints</li>
            <li>Trading Endpoints</li>
            <li>Portfolio Endpoints</li>
            <li>Market Data Endpoints</li>
          </ul>
        </div>

        <div style={{ marginBottom: '20px', paddingBottom: '20px', borderBottom: '1px solid #eee' }}>
          <h3>Features</h3>
          <ul style={{ marginLeft: '20px', marginTop: '10px' }}>
            <li><strong>Dashboard:</strong> Overview of portfolio performance and market data</li>
            <li><strong>Trading:</strong> Execute trades with real-time quote fetching</li>
            <li><strong>Trading Floor:</strong> Advanced multi-symbol trading interface</li>
            <li><strong>Portfolio:</strong> Track positions, equity, and performance</li>
            <li><strong>Analytics:</strong> Detailed performance metrics and statistics</li>
            <li><strong>Watchlist:</strong> Monitor favorite stocks and symbols</li>
          </ul>
        </div>

        <div>
          <h3>Technical Stack</h3>
          <ul style={{ marginLeft: '20px', marginTop: '10px' }}>
            <li>Frontend: React 18, Vite, Tailwind CSS</li>
            <li>Backend: FastAPI, SQLAlchemy, SQLite</li>
            <li>Real-time Data: Finnhub & Alpha Vantage APIs</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
