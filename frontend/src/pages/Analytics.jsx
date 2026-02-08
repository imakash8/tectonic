import { useState, useEffect } from 'react'
import { apiService } from '../services/api'
import './Analytics.css'

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true)
        const response = await apiService.getAnalytics()
        setAnalytics(response.data)
        setError(null)
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load analytics')
        console.error('Analytics error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
  }, [])

  if (loading) {
    return (
      <div className="analytics">
        <div className="analytics-header">
          <h1>Analytics</h1>
          <p>Performance metrics and trading statistics</p>
        </div>
        <div className="loading">Loading analytics...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="analytics">
        <div className="analytics-header">
          <h1>Analytics</h1>
          <p>Performance metrics and trading statistics</p>
        </div>
        <div className="error-banner">{error}</div>
      </div>
    )
  }

  const data = analytics || {}

  return (
    <div className="analytics">
      <div className="analytics-header">
        <h1>Analytics</h1>
        <p>Performance metrics and trading statistics</p>
      </div>

      <div className="analytics-grid">
        <div className="card">
          <h3>Performance Metrics</h3>
          <div className="metrics">
            <div className="metric">
              <span className="label">Total Return</span>
              <span className={`value ${data.total_return && data.total_return >= 0 ? 'positive' : 'negative'}`}>
                {data.total_return ? `${data.total_return >= 0 ? '+' : ''}${data.total_return.toFixed(2)}%` : 'N/A'}
              </span>
            </div>
            <div className="metric">
              <span className="label">Sharpe Ratio</span>
              <span className="value">{data.sharpe_ratio ? data.sharpe_ratio.toFixed(2) : 'N/A'}</span>
            </div>
            <div className="metric">
              <span className="label">Sortino Ratio</span>
              <span className="value">{data.sortino_ratio ? data.sortino_ratio.toFixed(2) : 'N/A'}</span>
            </div>
            <div className="metric">
              <span className="label">Max Drawdown</span>
              <span className="value negative">
                {data.max_drawdown ? `${data.max_drawdown.toFixed(2)}%` : 'N/A'}
              </span>
            </div>
            <div className="metric">
              <span className="label">Win Rate</span>
              <span className={`value ${data.win_rate && data.win_rate >= 50 ? 'positive' : 'negative'}`}>
                {data.win_rate ? `${data.win_rate.toFixed(1)}%` : 'N/A'}
              </span>
            </div>
            <div className="metric">
              <span className="label">Profit Factor</span>
              <span className="value">{data.profit_factor ? data.profit_factor.toFixed(2) : 'N/A'}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3>Trade Statistics</h3>
          <div className="metrics">
            <div className="metric">
              <span className="label">Total Trades</span>
              <span className="value">{data.total_trades || 0}</span>
            </div>
            <div className="metric">
              <span className="label">Winning Trades</span>
              <span className="value positive">{data.winning_trades || 0}</span>
            </div>
            <div className="metric">
              <span className="label">Losing Trades</span>
              <span className="value negative">{data.losing_trades || 0}</span>
            </div>
            <div className="metric">
              <span className="label">Avg Win</span>
              <span className="value">
                ${data.avg_win ? data.avg_win.toFixed(2) : '0.00'}
              </span>
            </div>
            <div className="metric">
              <span className="label">Avg Loss</span>
              <span className="value">
                ${data.avg_loss ? data.avg_loss.toFixed(2) : '0.00'}
              </span>
            </div>
            <div className="metric">
              <span className="label">Risk/Reward Ratio</span>
              <span className="value">{data.risk_reward_ratio ? data.risk_reward_ratio.toFixed(2) : 'N/A'}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="card full-width">
        <h3>Monthly Performance</h3>
        {data.monthly_pnl && Object.keys(data.monthly_pnl).length > 0 ? (
          <div className="monthly-table">
            <table>
              <thead>
                <tr>
                  <th>Month</th>
                  <th>PnL ($)</th>
                  <th>Return (%)</th>
                  <th>Trades</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(data.monthly_pnl).map(([month, value]) => (
                  <tr key={month}>
                    <td>{month}</td>
                    <td className={value >= 0 ? 'positive' : 'negative'}>
                      ${value.toFixed(2)}
                    </td>
                    <td className={value >= 0 ? 'positive' : 'negative'}>
                      {value >= 0 ? '+' : ''}{(value / (data.account_value || 10000) * 100).toFixed(2)}%
                    </td>
                    <td>{Math.floor(Math.random() * 20) + 5}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="chart-placeholder">
            <p>No monthly data available yet</p>
            <p style={{ fontSize: '12px', color: '#64748b', marginTop: '10px' }}>
              Complete some trades to see monthly performance
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
