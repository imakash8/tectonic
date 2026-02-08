import { useState, useEffect } from 'react'
import { useTradeStore } from '../store'
import { apiService } from '../services/api'
import './Trading.css'

// Common stock symbols for autocomplete
const COMMON_SYMBOLS = [
  'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META', 'AVGO', 'ASML',
  'NFLX', 'PYPL', 'INTC', 'AMD', 'QCOM', 'CSCO', 'ADBE', 'CRM', 'ORCL', 'IBM',
  'BA', 'CAT', 'DD', 'GE', 'MMM', 'JNJ', 'KO', 'PG', 'WMT', 'MCD',
  'NIKE', 'ADIDAS', 'LULU', 'ULTA', 'NKE', 'TJX', 'HD', 'LOW', 'DG', 'AZO',
  'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC', 'BLK', 'BX',
  'XOM', 'CVX', 'COP', 'MPC', 'HES', 'EOG', 'SLB', 'HAL', 'OKE', 'PSX',
  'VRTX', 'GILD', 'BIIB', 'AMGN', 'LLY', 'PFE', 'ABBV', 'JNJ', 'MRNA', 'BNTX',
  'TSLA', 'GM', 'F', 'LCID', 'RIVN', 'CCIV', 'NIO', 'XPE', 'LI', 'XPEV',
  'SPY', 'QQQ', 'IWM', 'EEM', 'GLD', 'TLT', 'HYG', 'LQD', 'AGG', 'IVV',
  'COIN', 'MSTR', 'RIOT', 'MARA', 'CLSK', 'HUT', 'CORE', 'CIFR', 'SATS', 'MRKR'
].sort()

export default function Trading() {
  const [symbol, setSymbol] = useState('')
  const [direction, setDirection] = useState('BUY')
  const [entryPrice, setEntryPrice] = useState('')
  const [stopLossPercent, setStopLossPercent] = useState('2') // Risk percentage
  const [takeProfitPercent, setTakeProfitPercent] = useState('5') // Profit percentage
  const [quantity, setQuantity] = useState('1')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [gatesStatus, setGatesStatus] = useState({})
  const [liveQuote, setLiveQuote] = useState(null)
  const [companyProfile, setCompanyProfile] = useState(null)
  const [quoteLoading, setQuoteLoading] = useState(false)
  const [portfolios, setPortfolios] = useState([])
  const [selectedPortfolioId, setSelectedPortfolioId] = useState(null)
  const [showSymbolSuggestions, setShowSymbolSuggestions] = useState(false)
  const [filteredSymbols, setFilteredSymbols] = useState([])
  const { addTrade } = useTradeStore()

  // Fetch portfolios on mount
  useEffect(() => {
    const fetchPortfolios = async () => {
      try {
        const res = await apiService.getPortfolios()
        if (res.data.length > 0) {
          setPortfolios(res.data)
          setSelectedPortfolioId(res.data[0].id)
        }
      } catch (err) {
        console.error('Failed to fetch portfolios:', err)
      }
    }
    fetchPortfolios()
  }, [])

  // Handle symbol input and show suggestions
  const handleSymbolChange = (e) => {
    const value = e.target.value.toUpperCase()
    setSymbol(value)
    
    if (value.length >= 1) {
      // Filter symbols that match the input
      const filtered = COMMON_SYMBOLS.filter(sym => sym.includes(value))
      setFilteredSymbols(filtered)
      setShowSymbolSuggestions(true)
    } else {
      setShowSymbolSuggestions(false)
      setFilteredSymbols([])
    }
  }

  const selectSymbol = (sym) => {
    setSymbol(sym)
    setShowSymbolSuggestions(false)
    setFilteredSymbols([])

  }

  // Fetch live quote and company profile when symbol changes
  useEffect(() => {
    if (symbol && symbol.length >= 1) {
      fetchQuoteAndProfile()
    }
  }, [symbol])

  const fetchQuoteAndProfile = async () => {
    try {
      setQuoteLoading(true)
      setError(null)
      
      // Fetch quote
      const quoteResponse = await apiService.getQuote(symbol.toUpperCase())
      setLiveQuote(quoteResponse.data)
      setEntryPrice(quoteResponse.data.current_price.toFixed(2))
      
      // Fetch company profile
      try {
        const profileResponse = await apiService.getCompanyProfile(symbol.toUpperCase())
        setCompanyProfile(profileResponse.data)
      } catch (err) {
        console.warn(`Failed to fetch company profile for ${symbol}:`, err.message)
        setCompanyProfile(null)
      }
    } catch (err) {
      console.warn(`Failed to fetch quote for ${symbol}:`, err.message)
      setError(`Could not find data for ${symbol}`)
      setLiveQuote(null)
      setCompanyProfile(null)
    } finally {
      setQuoteLoading(false)
    }
  }

  // Calculate stop loss and take profit prices based on percentages
  const calculatePrices = () => {
    const entry = parseFloat(entryPrice)
    const stopPercent = parseFloat(stopLossPercent)
    const profitPercent = parseFloat(takeProfitPercent)
    
    if (!entry || !stopPercent || !profitPercent) return null

    let stopLossPrice, takeProfitPrice

    if (direction === 'BUY') {
      // For BUY: stop loss is BELOW entry, take profit is ABOVE entry
      stopLossPrice = entry * (1 - stopPercent / 100)
      takeProfitPrice = entry * (1 + profitPercent / 100)
    } else {
      // For SELL: stop loss is ABOVE entry, take profit is BELOW entry
      stopLossPrice = entry * (1 + stopPercent / 100)
      takeProfitPrice = entry * (1 - profitPercent / 100)
    }

    return {
      stopLoss: stopLossPrice,
      takeProfit: takeProfitPrice
    }
  }

  const prices = calculatePrices()

  const calculateRiskReward = () => {
    if (!prices) return null
    
    const entry = parseFloat(entryPrice)
    const risk = Math.abs(entry - prices.stopLoss)
    const reward = Math.abs(prices.takeProfit - entry)
    
    return risk > 0 ? (reward / risk).toFixed(2) : null
  }

  const riskRewardRatio = calculateRiskReward()

  const handleExecuteTrade = async (e) => {
    e.preventDefault()
    
    if (!selectedPortfolioId) {
      setError('Please create or select a portfolio first')
      return
    }
    
    if (!symbol || !entryPrice || !stopLossPercent || !takeProfitPercent || !quantity) {
      setError('Please fill all required fields')
      return
    }

    if (!prices) {
      setError('Invalid price calculation')
      return
    }

    try {
      setLoading(true)
      setError(null)
      setSuccess(null)
      
      // Refresh quote right before execution (fresh data for Gate 1)
      try {
        const freshQuoteResponse = await apiService.getQuote(symbol.toUpperCase())
        if (freshQuoteResponse.data) {
          setLiveQuote(freshQuoteResponse.data)
        }
      } catch (quoteErr) {
        logger.warn('Could not refresh quote before execution:', quoteErr)
        // Continue anyway, use cached quote
      }
      
      const response = await apiService.executeTrade({
        portfolio_id: selectedPortfolioId,
        symbol: symbol.toUpperCase(),
        direction,
        entry_price: parseFloat(entryPrice),
        stop_loss: prices.stopLoss,
        take_profit: prices.takeProfit,
        quantity: parseInt(quantity),
        ai_confidence: 0.75
      })

      addTrade(response.data)
      
      // Set gates status from the response
      if (response.data.validation_gates) {
        setGatesStatus(response.data.validation_gates)
      }
      
      setSuccess(`✓ Trade executed successfully! Order #${response.data.id}`)
      
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to execute trade')
      console.error('Trading error:', err)
    } finally {
      setLoading(false)
    }
  }


  return (
    <div className="trading">
      <div className="trading-header">
        <h1>Trading</h1>
        <p>Execute trades with 9-gate validation system</p>
      </div>

      {portfolios.length === 0 && (
        <div style={{ padding: '40px 20px', textAlign: 'center', background: '#f9fafb', borderRadius: '8px', margin: '20px' }}>
          <h3>📁 No Portfolios Found</h3>
          <p>You need to create a portfolio first to execute trades.</p>
          <p style={{ fontSize: '14px', color: '#666', marginTop: '10px' }}>
            Go to <strong>Portfolio</strong> tab to create your first portfolio.
          </p>
        </div>
      )}

      {portfolios.length > 0 && (
        <div className="trading-content">
          <div className="card">
            <h3>Execute Trade</h3>
          
          {/* Live Quote Display */}
          {liveQuote && (
            <div className="live-quote-banner">
              <div className="quote-info">
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  {companyProfile?.logo && (
                    <img 
                      src={companyProfile.logo} 
                      alt={companyProfile.name}
                      style={{ width: '32px', height: '32px', borderRadius: '4px' }}
                    />
                  )}
                  <div>
                    <span className="quote-symbol">{liveQuote.symbol}</span>
                    <div style={{ fontSize: '12px', color: '#64748b' }}>
                      {companyProfile?.name || 'Loading...'}
                    </div>
                  </div>
                </div>
                <span className="quote-price">${liveQuote.current_price.toFixed(2)}</span>
                <span className={`quote-change ${(liveQuote.current_price - liveQuote.prev_close) >= 0 ? 'positive' : 'negative'}`}>
                  {(liveQuote.current_price - liveQuote.prev_close) >= 0 ? '▲' : '▼'} 
                  {((((liveQuote.current_price - liveQuote.prev_close) / liveQuote.prev_close) * 100).toFixed(2))}%
                </span>
              </div>
              <div className="quote-details">
                <span>H: ${liveQuote.high.toFixed(2)}</span>
                <span>L: ${liveQuote.low.toFixed(2)}</span>
                <span>O: ${liveQuote.open.toFixed(2)}</span>
                <span style={{ fontSize: '11px', color: '#64748b' }}>Source: {liveQuote.source}</span>
              </div>
            </div>
          )}
          
          <form onSubmit={handleExecuteTrade} className="trade-form">
            <div className="form-row">
              <div className="form-group" style={{ position: 'relative' }}>
                <label>Symbol *</label>
                <input
                  type="text"
                  value={symbol}
                  onChange={handleSymbolChange}
                  onFocus={() => {
                    if (symbol.length >= 1) {
                      setShowSymbolSuggestions(true)
                    }
                  }}
                  placeholder="e.g., AAPL, MSFT, GOOGL..."
                  required
                  autoComplete="off"
                />
                <small style={{ color: '#64748b', marginTop: '4px', display: 'block' }}>
                  {quoteLoading ? 'Fetching data...' : 'Start typing to search...'}
                </small>
                
                {showSymbolSuggestions && filteredSymbols.length > 0 && (
                  <div className="symbol-dropdown">
                    {filteredSymbols.slice(0, 10).map((sym, index) => (
                      <div
                        key={index}
                        className="symbol-option"
                        onClick={() => selectSymbol(sym)}
                      >
                        {sym}
                      </div>
                    ))}
                    {filteredSymbols.length > 10 && (
                      <div className="symbol-option-count">
                        +{filteredSymbols.length - 10} more
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="form-group">
                <label>Direction *</label>
                <select value={direction} onChange={(e) => setDirection(e.target.value)}>
                  <option value="BUY">BUY</option>
                  <option value="SELL">SELL</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Entry Price *</label>
                <input
                  type="number"
                  step="0.01"
                  value={entryPrice}
                  onChange={(e) => setEntryPrice(e.target.value)}
                  placeholder="0.00"
                  required
                />
              </div>

              <div className="form-group">
                <label>Risk % (Stop Loss) *</label>
                <input
                  type="number"
                  step="0.1"
                  value={stopLossPercent}
                  onChange={(e) => setStopLossPercent(e.target.value)}
                  placeholder="2"
                  required
                />
                <small style={{ color: '#64748b', marginTop: '4px', display: 'block' }}>
                  {prices && entryPrice ? `Price: $${prices.stopLoss.toFixed(2)}` : 'Enter entry price'}
                </small>
              </div>

              <div className="form-group">
                <label>Profit % (Take Profit) *</label>
                <input
                  type="number"
                  step="0.1"
                  value={takeProfitPercent}
                  onChange={(e) => setTakeProfitPercent(e.target.value)}
                  placeholder="5"
                  required
                />
                <small style={{ color: '#64748b', marginTop: '4px', display: 'block' }}>
                  {prices && entryPrice ? `Price: $${prices.takeProfit.toFixed(2)}` : 'Enter entry price'}
                </small>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Quantity *</label>
                <input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  min="1"
                  required
                />
              </div>

              {riskRewardRatio && (
                <div className="form-group">
                  <label>Risk:Reward</label>
                  <div className="rr-ratio" style={{ color: riskRewardRatio >= 1.5 ? '#10b981' : '#ef4444' }}>
                    1:{riskRewardRatio}
                  </div>
                </div>
              )}
            </div>

            <div className="form-actions">
              <button type="submit" className="primary" disabled={loading}>
                {loading ? 'Executing...' : 'Execute Trade'}
              </button>
              <button type="reset" className="secondary" onClick={() => {
                setSymbol('')
                setDirection('BUY')
                setEntryPrice('')
                setStopLossPercent('2')
                setTakeProfitPercent('5')
                setQuantity('1')
                setGatesStatus({})
                setSuccess(null)
                setError(null)
                setCompanyProfile(null)
                setLiveQuote(null)
              }}>
                Clear
              </button>
            </div>
          </form>
          </div>

          <div className="card">
          <h3>Validation Gates Status</h3>
          
          {error && <div className="error-banner">{error}</div>}
          {success && <div className="success-banner">{success}</div>}
          
          <p style={{ color: '#64748b', fontSize: '14px', marginBottom: '15px', marginTop: success || error ? '10px' : '0px' }}>
            {Object.keys(gatesStatus).length === 0 ? 'Execute a trade to see validation gate results →' : 'Results from last execution'}
          </p>
          <div className="gates-list">
            <div className={`gate-item ${Object.keys(gatesStatus).length === 0 ? 'disabled' : ''}`}>
              <span className="gate-number">1</span>
              <span className="gate-name">Quote Freshness</span>
              <span className={`gate-status ${gatesStatus.gate_1?.passed ? 'passed' : Object.keys(gatesStatus).length > 0 ? 'failed' : 'placeholder'}`}>
                {Object.keys(gatesStatus).length === 0 ? '—' : gatesStatus.gate_1?.passed ? '✓ PASS' : '✗ FAIL'}
              </span>
            </div>
            <div className={`gate-item ${Object.keys(gatesStatus).length === 0 ? 'disabled' : ''}`}>
              <span className="gate-number">2</span>
              <span className="gate-name">Price Deviation</span>
              <span className={`gate-status ${gatesStatus.gate_2?.passed ? 'passed' : Object.keys(gatesStatus).length > 0 ? 'failed' : 'placeholder'}`}>
                {Object.keys(gatesStatus).length === 0 ? '—' : gatesStatus.gate_2?.passed ? '✓ PASS' : '✗ FAIL'}
              </span>
            </div>
            <div className={`gate-item ${Object.keys(gatesStatus).length === 0 ? 'disabled' : ''}`}>
              <span className="gate-number">3</span>
              <span className="gate-name">Liquidity Check</span>
              <span className={`gate-status ${gatesStatus.gate_3?.passed ? 'passed' : Object.keys(gatesStatus).length > 0 ? 'failed' : 'placeholder'}`}>
                {Object.keys(gatesStatus).length === 0 ? '—' : gatesStatus.gate_3?.passed ? '✓ PASS' : '✗ FAIL'}
              </span>
            </div>
            <div className={`gate-item ${Object.keys(gatesStatus).length === 0 ? 'disabled' : ''}`}>
              <span className="gate-number">4</span>
              <span className="gate-name">Volatility Regime</span>
              <span className={`gate-status ${gatesStatus.gate_4?.passed ? 'passed' : Object.keys(gatesStatus).length > 0 ? 'failed' : 'placeholder'}`}>
                {Object.keys(gatesStatus).length === 0 ? '—' : gatesStatus.gate_4?.passed ? '✓ PASS' : '✗ FAIL'}
              </span>
            </div>
            <div className={`gate-item ${Object.keys(gatesStatus).length === 0 ? 'disabled' : ''}`}>
              <span className="gate-number">5</span>
              <span className="gate-name">Market Hours</span>
              <span className={`gate-status ${gatesStatus.gate_5?.passed ? 'passed' : Object.keys(gatesStatus).length > 0 ? 'failed' : 'placeholder'}`}>
                {Object.keys(gatesStatus).length === 0 ? '—' : gatesStatus.gate_5?.passed ? '✓ PASS' : '✗ FAIL'}
              </span>
            </div>
            <div className={`gate-item ${Object.keys(gatesStatus).length === 0 ? 'disabled' : ''}`}>
              <span className="gate-number">6</span>
              <span className="gate-name">Risk/Reward Ratio</span>
              <span className={`gate-status ${gatesStatus.gate_6?.passed ? 'passed' : Object.keys(gatesStatus).length > 0 ? 'failed' : 'placeholder'}`}>
                {Object.keys(gatesStatus).length === 0 ? '—' : gatesStatus.gate_6?.passed ? '✓ PASS' : '✗ FAIL'}
              </span>
            </div>
            <div className={`gate-item ${Object.keys(gatesStatus).length === 0 ? 'disabled' : ''}`}>
              <span className="gate-number">7</span>
              <span className="gate-name">Portfolio Exposure</span>
              <span className={`gate-status ${gatesStatus.gate_7?.passed ? 'passed' : Object.keys(gatesStatus).length > 0 ? 'failed' : 'placeholder'}`}>
                {Object.keys(gatesStatus).length === 0 ? '—' : gatesStatus.gate_7?.passed ? '✓ PASS' : '✗ FAIL'}
              </span>
            </div>
            <div className={`gate-item ${Object.keys(gatesStatus).length === 0 ? 'disabled' : ''}`}>
              <span className="gate-number">8</span>
              <span className="gate-name">Order Flow Pressure</span>
              <span className={`gate-status ${gatesStatus.gate_8?.passed ? 'passed' : Object.keys(gatesStatus).length > 0 ? 'failed' : 'placeholder'}`}>
                {Object.keys(gatesStatus).length === 0 ? '—' : gatesStatus.gate_8?.passed ? '✓ PASS' : '✗ FAIL'}
              </span>
            </div>
            <div className={`gate-item ${Object.keys(gatesStatus).length === 0 ? 'disabled' : ''}`}>
              <span className="gate-number">9</span>
              <span className="gate-name">AI Confidence</span>
              <span className={`gate-status ${gatesStatus.gate_9?.passed ? 'passed' : Object.keys(gatesStatus).length > 0 ? 'failed' : 'placeholder'}`}>
                {Object.keys(gatesStatus).length === 0 ? '—' : gatesStatus.gate_9?.passed ? '✓ PASS' : '✗ FAIL'}
              </span>
            </div>
          </div>
          </div>
        </div>
      )}
    </div>
  )
}
