import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMarketStore, useAuthStore } from '../store'
import { apiService } from '../services/api'
import './Dashboard.css'

export default function Dashboard() {
  const navigate = useNavigate()
  const { marketData, setMarketData } = useMarketStore()
  const token = useAuthStore((state) => state.token)
  const [portfolioSummary, setPortfolioSummary] = useState(null)
  const [trades, setTrades] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [comprehensiveAnalytics, setComprehensiveAnalytics] = useState(null)
  const [liveMarkets, setLiveMarkets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const watchSymbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']

  // Fetch data when component mounts and token is available
  useEffect(() => {
    if (token) {
      fetchData()
    }
  }, [token])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch analytics overview
      const analyticsRes = await apiService.getAnalytics()
      setAnalytics(analyticsRes.data)

      // Fetch comprehensive analytics
      try {
        const compRes = await apiService.getComprehensiveAnalytics()
        setComprehensiveAnalytics(compRes.data)
      } catch (err) {
        console.warn('Comprehensive analytics unavailable:', err.message)
        setComprehensiveAnalytics(null)
      }

      // Fetch all trades
      const tradesRes = await apiService.getTrades()
      setTrades(tradesRes.data.slice(-5)) // Last 5 trades

      // Fetch market data
      try {
        const marketRes = await apiService.getMarketOverview()
        setMarketData(marketRes.data)
      } catch (err) {
        console.warn('Market data unavailable:', err.message)
      }

      // Fetch live market prices for watch symbols
      const liveData = await Promise.all(
        watchSymbols.map(async (symbol) => {
          try {
            const res = await apiService.getQuote(symbol)
            return { symbol, ...res.data }
          } catch (err) {
            console.warn(`Failed to fetch ${symbol}:`, err.message)
            return { symbol, error: true }
          }
        })
      )
      setLiveMarkets(liveData)
    } catch (err) {
      setError(err.message || 'Failed to fetch dashboard data')
      console.error('Dashboard error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">
          <p>Loading dashboard...</p>
        </div>
      </div>
    )
  }

  const portfolioValue = analytics?.total_equity || 0
  const portfolioChange = analytics?.total_pnl || 0
  const portfolioChangePercent = analytics?.total_return_pct || 0
  const openPositions = analytics?.open_trades || 0
  const todayPnL = analytics?.total_pnl || 0
  const winRate = analytics?.win_rate || 0

  const getGradeColor = (grade) => {
    if (grade.startsWith('A')) return '#10b981'
    if (grade.startsWith('B')) return '#3b82f6'
    if (grade.startsWith('C')) return '#f59e0b'
    if (grade.startsWith('D')) return '#ef4444'
    return '#64748b'
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Welcome to Tectonic Trading Platform</p>
      </div>

      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

      <div className="dashboard-grid">
        <div className="card" style={{ cursor: 'pointer' }} onClick={() => navigate('/portfolio')}>
          <h3>Portfolio Value</h3>
          <div className="stat">
            <span className="value">${portfolioValue.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
            <span className="change positive">+${portfolioChange.toLocaleString('en-US', { maximumFractionDigits: 0 })} (+{portfolioChangePercent.toFixed(1)}%)</span>
          </div>
          <small style={{ color: '#64748b', marginTop: '10px', display: 'block' }}>Click to view details →</small>
        </div>

        <div className="card" style={{ cursor: 'pointer' }} onClick={() => navigate('/trading')}>
          <h3>Open Positions</h3>
          <div className="stat">
            <span className="value">{openPositions}</span>
            <span className="subtitle">Active trades</span>
          </div>
          <small style={{ color: '#64748b', marginTop: '10px', display: 'block' }}>Click to trade →</small>
        </div>

        <div className="card" style={{ cursor: 'pointer' }} onClick={() => navigate('/analytics')}>
          <h3>Today's P/L</h3>
          <div className="stat">
            <span className="value positive">+${todayPnL.toLocaleString()}</span>
            <span className="change positive">+{portfolioChangePercent.toFixed(1)}%</span>
          </div>
          <small style={{ color: '#64748b', marginTop: '10px', display: 'block' }}>Click to analyze →</small>
        </div>        <div className="card" style={{ cursor: 'pointer' }} onClick={() => navigate('/analytics')}>
          <h3>Win Rate</h3>
          <div className="stat">
            <span className="value">{winRate.toFixed(0)}%</span>
            <span className="subtitle">Last {analytics?.closed_trades || 30} trades</span>
          </div>
          <small style={{ color: '#64748b', marginTop: '10px', display: 'block' }}>Click to view stats →</small>
        </div>
      </div>

      {/* Live Market Data Section */}
      <div className="card full-width">
        <h3>📈 Live Market Data</h3>
        {liveMarkets.length === 0 ? (
          <p style={{ color: '#64748b', padding: '20px', textAlign: 'center' }}>Loading market data...</p>
        ) : (
          <div className="market-grid">
            {liveMarkets.map((market) => {
              if (market.error) return null
              const change = market.current_price - market.prev_close
              const changePercent = ((change / market.prev_close) * 100).toFixed(2)
              const isPositive = change >= 0
              
              return (
                <div 
                  key={market.symbol} 
                  className="market-card"
                  style={{ cursor: 'pointer' }}
                  onClick={() => navigate('/trading')}
                >
                  <div className="market-header">
                    <h4>{market.symbol}</h4>
                    <span className={`market-change ${isPositive ? 'positive' : 'negative'}`}>
                      {isPositive ? '▲' : '▼'} {Math.abs(changePercent)}%
                    </span>
                  </div>
                  <div className="market-price">
                    <span className="price">${market.current_price.toFixed(2)}</span>
                    <span className={`market-delta ${isPositive ? 'positive' : 'negative'}`}>
                      {isPositive ? '+' : ''}${change.toFixed(2)}
                    </span>
                  </div>
                  <div className="market-range">
                    <span>H: ${market.high.toFixed(2)}</span>
                    <span>L: ${market.low.toFixed(2)}</span>
                  </div>
                  <div className="market-source">
                    <small>Source: {market.source}</small>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Comprehensive Analytics Section */}
      {comprehensiveAnalytics && comprehensiveAnalytics.status === 'complete' && (
        <div className="analytics-section">
          <h2>📊 Comprehensive Analytics</h2>
          
          <div className="analytics-grid">
            {/* System Grade Card */}
            <div className="analytics-card grade-card">
              <h4>System Grade</h4>
              <div className="grade-display" style={{ borderColor: getGradeColor(comprehensiveAnalytics.system_grade) }}>
                <div className="grade-letter" style={{ color: getGradeColor(comprehensiveAnalytics.system_grade) }}>
                  {comprehensiveAnalytics.system_grade}
                </div>
                <div className="grade-score">Score: {comprehensiveAnalytics.grade_score}</div>
              </div>
            </div>

            {/* Performance Metrics */}
            <div className="analytics-card">
              <h4>Performance Metrics</h4>
              <div className="metric-row">
                <span>Win Rate:</span>
                <strong>{(comprehensiveAnalytics.win_rate_pct).toFixed(1)}%</strong>
              </div>
              <div className="metric-row">
                <span>Profit Factor:</span>
                <strong>{comprehensiveAnalytics.profit_factor.toFixed(2)}</strong>
              </div>
              <div className="metric-row">
                <span>Expectancy:</span>
                <strong>${comprehensiveAnalytics.expectancy.toFixed(2)}</strong>
              </div>
            </div>

            {/* Trade Statistics */}
            <div className="analytics-card">
              <h4>Trade Statistics</h4>
              <div className="metric-row">
                <span>Total Trades:</span>
                <strong>{comprehensiveAnalytics.total_trades}</strong>
              </div>
              <div className="metric-row">
                <span>Winning:</span>
                <strong className="green">{comprehensiveAnalytics.winning_trades}</strong>
              </div>
              <div className="metric-row">
                <span>Losing:</span>
                <strong className="red">{comprehensiveAnalytics.losing_trades}</strong>
              </div>
            </div>

            {/* Win/Loss Streaks */}
            <div className="analytics-card">
              <h4>Win/Loss Streaks</h4>
              <div className="metric-row">
                <span>Max Win Streak:</span>
                <strong className="green">{comprehensiveAnalytics.max_win_streak}</strong>
              </div>
              <div className="metric-row">
                <span>Max Loss Streak:</span>
                <strong className="red">{comprehensiveAnalytics.max_loss_streak}</strong>
              </div>
              <div className="metric-row">
                <span>Avg Win:</span>
                <strong>${comprehensiveAnalytics.avg_win.toFixed(2)}</strong>
              </div>
              <div className="metric-row">
                <span>Avg Loss:</span>
                <strong>${comprehensiveAnalytics.avg_loss.toFixed(2)}</strong>
              </div>
            </div>
          </div>

          {/* Period Performance */}
          <div className="period-metrics">
            <h3>Performance by Period</h3>
            <div className="period-grid">
              {comprehensiveAnalytics.metrics_7d && (
                <div className="period-card">
                  <h5>Last 7 Days</h5>
                  <div className="period-stat">
                    <span>Trades:</span>
                    <strong>{comprehensiveAnalytics.metrics_7d.trade_count}</strong>
                  </div>
                  <div className="period-stat">
                    <span>Win Rate:</span>
                    <strong>{(comprehensiveAnalytics.metrics_7d.win_rate).toFixed(1)}%</strong>
                  </div>
                  <div className="period-stat">
                    <span>P/L:</span>
                    <strong className={comprehensiveAnalytics.metrics_7d.total_pnl >= 0 ? 'green' : 'red'}>
                      ${comprehensiveAnalytics.metrics_7d.total_pnl.toFixed(2)}
                    </strong>
                  </div>
                </div>
              )}
              {comprehensiveAnalytics.metrics_30d && (
                <div className="period-card">
                  <h5>Last 30 Days</h5>
                  <div className="period-stat">
                    <span>Trades:</span>
                    <strong>{comprehensiveAnalytics.metrics_30d.trade_count}</strong>
                  </div>
                  <div className="period-stat">
                    <span>Win Rate:</span>
                    <strong>{(comprehensiveAnalytics.metrics_30d.win_rate).toFixed(1)}%</strong>
                  </div>
                  <div className="period-stat">
                    <span>P/L:</span>
                    <strong className={comprehensiveAnalytics.metrics_30d.total_pnl >= 0 ? 'green' : 'red'}>
                      ${comprehensiveAnalytics.metrics_30d.total_pnl.toFixed(2)}
                    </strong>
                  </div>
                </div>
              )}
              {comprehensiveAnalytics.metrics_90d && (
                <div className="period-card">
                  <h5>Last 90 Days</h5>
                  <div className="period-stat">
                    <span>Trades:</span>
                    <strong>{comprehensiveAnalytics.metrics_90d.trade_count}</strong>
                  </div>
                  <div className="period-stat">
                    <span>Win Rate:</span>
                    <strong>{(comprehensiveAnalytics.metrics_90d.win_rate).toFixed(1)}%</strong>
                  </div>
                  <div className="period-stat">
                    <span>P/L:</span>
                    <strong className={comprehensiveAnalytics.metrics_90d.total_pnl >= 0 ? 'green' : 'red'}>
                      ${comprehensiveAnalytics.metrics_90d.total_pnl.toFixed(2)}
                    </strong>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="card full-width">
        <h3>Recent Trades</h3>
        {trades.length === 0 ? (
          <p style={{ color: '#64748b', padding: '20px', textAlign: 'center' }}>
            No trades yet. Start trading to see them here!
          </p>
        ) : (
          <table className="trades-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Type</th>
                <th>Entry</th>
                <th>Exit</th>
                <th>P/L</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((trade) => (
                <tr 
                  key={trade.id}
                  style={{ cursor: 'pointer', transition: 'background-color 0.2s' }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f5f5f5'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = ''}
                  onClick={() => navigate('/portfolio')}
                >
                  <td><strong>{trade.symbol}</strong></td>
                  <td>{trade.direction}</td>
                  <td>${trade.entry_price.toFixed(2)}</td>
                  <td>{trade.exit_price ? `$${trade.exit_price.toFixed(2)}` : '-'}</td>
                  <td className={trade.pnl >= 0 ? 'positive' : 'negative'}>
                    {trade.pnl ? `${trade.pnl >= 0 ? '+' : ''}$${trade.pnl.toFixed(0)}` : '-'}
                  </td>
                  <td>
                    <span className={`badge ${trade.status === 'CLOSED' ? 'success' : ''}`}>
                      {trade.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
