import { useState, useEffect } from 'react'
import { usePortfolioStore } from '../store'
import { apiService } from '../services/api'
import './Portfolio.css'

export default function Portfolio() {
  const { portfolios, selectedPortfolio, setPortfolios, setSelectedPortfolio } = usePortfolioStore()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [createLoading, setCreateLoading] = useState(false)
  const [createError, setCreateError] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    starting_capital: ''
  })

  useEffect(() => {
    fetchPortfolios()
  }, [])

  const fetchPortfolios = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiService.getPortfolios()
      setPortfolios(response.data)
      if (response.data.length > 0) {
        setSelectedPortfolio(response.data[0])
      }
    } catch (err) {
      setError(err.message || 'Failed to load portfolios')
      console.error('Portfolio error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePortfolio = async (e) => {
    e.preventDefault()
    
    if (!formData.name.trim() || !formData.starting_capital) {
      setCreateError('Please fill in all fields')
      return
    }

    try {
      setCreateLoading(true)
      setCreateError(null)
      const response = await apiService.createPortfolio({
        name: formData.name,
        starting_capital: parseFloat(formData.starting_capital)
      })
      
      // Add new portfolio to list
      setPortfolios([...portfolios, response.data])
      setSelectedPortfolio(response.data)
      
      // Reset form
      setFormData({ name: '', starting_capital: '' })
      setShowCreateForm(false)
    } catch (err) {
      setCreateError(err.message || 'Failed to create portfolio')
      console.error('Create portfolio error:', err)
    } finally {
      setCreateLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="portfolio">
        <div className="portfolio-header">
          <h1>Portfolio</h1>
          <p>Track your trading positions and performance</p>
        </div>
        <div className="loading">Loading portfolios...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="portfolio">
        <div className="portfolio-header">
          <h1>Portfolio</h1>
          <p>Track your trading positions and performance</p>
        </div>
        <div className="error-banner">⚠️ {error}</div>
      </div>
    )
  }

  const portfolio = selectedPortfolio || portfolios[0]

  if (!portfolio) {
    return (
      <div className="portfolio">
        <div className="portfolio-header">
          <h1>Portfolio</h1>
          <p>Track your trading positions and performance</p>
        </div>
        
        <div className="card" style={{ maxWidth: '500px', margin: '40px auto' }}>
          <h2>📁 Create Your First Portfolio</h2>
          <p style={{ color: '#64748b', marginBottom: '20px' }}>
            You don't have any portfolios yet. Create one to start trading!
          </p>
          
          {createError && (
            <div className="error-banner" style={{ marginBottom: '20px' }}>
              ⚠️ {createError}
            </div>
          )}
          
          <form onSubmit={handleCreatePortfolio}>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>
                Portfolio Name *
              </label>
              <input
                type="text"
                placeholder="e.g., My Trading Portfolio"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '14px',
                  boxSizing: 'border-box'
                }}
              />
            </div>
            
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>
                Starting Capital ($) *
              </label>
              <input
                type="number"
                placeholder="e.g., 10000"
                value={formData.starting_capital}
                onChange={(e) => setFormData({ ...formData, starting_capital: e.target.value })}
                min="100"
                step="100"
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '14px',
                  boxSizing: 'border-box'
                }}
              />
            </div>
            
            <button
              type="submit"
              disabled={createLoading}
              style={{
                width: '100%',
                padding: '10px',
                backgroundColor: createLoading ? '#cbd5e1' : '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: createLoading ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                fontWeight: '500'
              }}
            >
              {createLoading ? 'Creating...' : 'Create Portfolio'}
            </button>
          </form>
        </div>
      </div>
    )
  }

  const currentEquity = portfolio.current_equity || 0
  const startingCapital = portfolio.starting_capital || 0
  const pnl = currentEquity - startingCapital
  const pnlPercent = startingCapital > 0 ? (pnl / startingCapital) * 100 : 0

  return (
    <div className="portfolio">
      <div className="portfolio-header">
        <h1>Portfolio</h1>
        <p>Track your trading positions and performance</p>
      </div>

      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

      {portfolios.length > 1 && (
        <div className="portfolio-selector">
          <select
            value={portfolio.id}
            onChange={(e) => {
              const selected = portfolios.find((p) => p.id === parseInt(e.target.value))
              setSelectedPortfolio(selected)
            }}
          >
            {portfolios.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} - ${p.current_equity?.toFixed(0)}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="portfolio-grid">
        <div className="card">
          <h3>Portfolio Summary</h3>
          <div className="summary-items">
            <div className="summary-item">
              <span className="label">Total Capital</span>
              <span className="value">${startingCapital.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
            </div>
            <div className="summary-item">
              <span className="label">Current Equity</span>
              <span className="value">${currentEquity.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
            </div>
            <div className="summary-item">
              <span className="label">Profit/Loss</span>
              <span className={`value ${pnl >= 0 ? 'positive' : 'negative'}`}>
                {pnl >= 0 ? '+' : ''}${pnl.toLocaleString('en-US', { maximumFractionDigits: 0 })}
              </span>
            </div>
            <div className="summary-item">
              <span className="label">Return</span>
              <span className={`value ${pnlPercent >= 0 ? 'positive' : 'negative'}`}>
                {pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(1)}%
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3>Asset Allocation</h3>
          <div className="allocation">
            <div className="allocation-item">
              <div className="allocation-label">
                <span>Stocks</span>
                <span>65%</span>
              </div>
              <div className="allocation-bar">
                <div className="allocation-fill" style={{ width: '65%' }}></div>
              </div>
            </div>
            <div className="allocation-item">
              <div className="allocation-label">
                <span>Crypto</span>
                <span>20%</span>
              </div>
              <div className="allocation-bar">
                <div className="allocation-fill" style={{ width: '20%' }}></div>
              </div>
            </div>
            <div className="allocation-item">
              <div className="allocation-label">
                <span>Cash</span>
                <span>15%</span>
              </div>
              <div className="allocation-bar">
                <div className="allocation-fill" style={{ width: '15%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card full-width">
        <h3>Open Positions</h3>
        {!portfolio.positions || portfolio.positions.length === 0 ? (
          <p style={{ color: '#64748b', padding: '20px', textAlign: 'center' }}>
            No open positions. Execute trades to see them here!
          </p>
        ) : (
          <table className="positions-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Type</th>
                <th>Quantity</th>
                <th>Entry Price</th>
                <th>Current Price</th>
                <th>P/L</th>
                <th>P/L %</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>AAPL</strong></td>
                <td><span className="badge">BUY</span></td>
                <td>100</td>
                <td>$150.00</td>
                <td>$165.75</td>
                <td className="positive">+$1,575</td>
                <td className="positive">+10.5%</td>
                <td>
                  <button className="btn-close">Close</button>
                </td>
              </tr>
              <tr>
                <td><strong>MSFT</strong></td>
                <td><span className="badge">BUY</span></td>
                <td>50</td>
                <td>$380.00</td>
                <td>$392.50</td>
                <td className="positive">+$625</td>
                <td className="positive">+3.3%</td>
                <td>
                  <button className="btn-close">Close</button>
                </td>
              </tr>
              <tr>
                <td><strong>GOOGL</strong></td>
                <td><span className="badge sell">SELL</span></td>
                <td>30</td>
                <td>$140.00</td>
                <td>$135.25</td>
                <td className="positive">+$142.50</td>
                <td className="positive">+3.4%</td>
                <td>
                  <button className="btn-close">Close</button>
                </td>
              </tr>
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
