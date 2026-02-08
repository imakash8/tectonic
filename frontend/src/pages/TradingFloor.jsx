import React, { useState, useEffect } from 'react';
import './TradingFloor.css';
import { apiService } from '../services/api';

export default function TradingFloor() {
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [quote, setQuote] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [paperMode, setPaperMode] = useState(true);
  const [tradeForm, setTradeForm] = useState({
    direction: 'BUY',
    quantity: 100,
    entryPrice: 0,
    stopLoss: 0,
    takeProfit: 0,
    reasoning: ''
  });
  const [portfolios, setPortfolios] = useState([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);

  const commonSymbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'WMT'];

  useEffect(() => {
    fetchPortfolios();
  }, []);

  useEffect(() => {
    if (selectedPortfolio) {
      fetchQuote();
    }
  }, [selectedSymbol, selectedPortfolio]);

  const fetchPortfolios = async () => {
    try {
      const response = await apiService.getPortfolios();
      setPortfolios(response.data);
      if (response.data.length > 0) {
        setSelectedPortfolio(response.data[0].id);
      }
    } catch (err) {
      setError('Failed to load portfolios');
    }
  };

  const fetchQuote = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.getMarketQuote(selectedSymbol);
      const quoteData = response.data;
      
      setQuote(quoteData);
      
      // Auto-fill entry price
      setTradeForm(prev => ({
        ...prev,
        entryPrice: quoteData.price || 0
      }));
    } catch (err) {
      setError(`Failed to fetch quote for ${selectedSymbol}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const calculatePrices = () => {
    const entry = parseFloat(tradeForm.entryPrice) || 0;
    if (entry <= 0) return;

    // Calculate stop loss and take profit
    const atrPercent = 0.02;
    const atr = entry * atrPercent;
    
    const newStopLoss = tradeForm.direction === 'BUY' 
      ? entry - atr 
      : entry + atr;
    
    const risk = Math.abs(entry - newStopLoss);
    const newTakeProfit = tradeForm.direction === 'BUY'
      ? entry + (risk * 1.618)
      : entry - (risk * 1.618);

    setTradeForm(prev => ({
      ...prev,
      stopLoss: parseFloat(newStopLoss.toFixed(2)),
      takeProfit: parseFloat(newTakeProfit.toFixed(2))
    }));
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setTradeForm(prev => ({
      ...prev,
      [name]: name === 'direction' || name === 'reasoning' ? value : parseFloat(value) || 0
    }));
  };

  const calculateRiskReward = () => {
    const entry = tradeForm.entryPrice;
    const stop = tradeForm.stopLoss;
    const target = tradeForm.takeProfit;
    
    if (!entry || !stop || !target) return 0;
    
    const risk = Math.abs(entry - stop);
    const reward = Math.abs(target - entry);
    
    return (reward / risk).toFixed(2);
  };

  const executeTrade = async () => {
    if (!selectedPortfolio) {
      setError('Please select a portfolio');
      return;
    }

    try {
      const payload = {
        portfolio_id: selectedPortfolio,
        symbol: selectedSymbol,
        direction: tradeForm.direction,
        entry_price: tradeForm.entryPrice,
        stop_loss: tradeForm.stopLoss,
        take_profit: tradeForm.takeProfit,
        quantity: Math.floor(tradeForm.quantity),
        ai_confidence: 0.75,
        entry_reasoning: tradeForm.reasoning || `${tradeForm.direction} trade on ${selectedSymbol}`
      };

      const response = paperMode 
        ? await apiService.executePaperTrade(payload)
        : await apiService.executeTrade(payload);
      
      setError(null);
      alert(`${paperMode ? 'Paper ' : ''}Trade executed successfully!\nTrade ID: ${response.data.id}`);
      
      // Reset form
      setTradeForm({
        direction: 'BUY',
        quantity: 100,
        entryPrice: 0,
        stopLoss: 0,
        takeProfit: 0,
        reasoning: ''
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to execute trade');
      console.error(err);
    }
  };

  const riskRewardRatio = calculateRiskReward();
  const minRRRatio = tradeForm.direction === 'BUY' ? 1.5 : 1.5;
  const rrValid = riskRewardRatio >= minRRRatio;

  return (
    <div className="trading-floor">
      <div className="trading-floor-header">
        <h1>🏢 Trading Floor</h1>
        <p>Execute trades with paper trading mode for risk-free practice</p>
      </div>

      <div className="trading-floor-container">
        {/* Left Panel - Symbol Selection & Quote */}
        <div className="trading-panel left-panel">
          <div className="panel-section">
            <h3>Symbol Selection</h3>
            <div className="symbol-input">
              <input
                type="text"
                placeholder="Enter symbol (e.g., AAPL)"
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value.toUpperCase())}
              />
              <button onClick={fetchQuote} disabled={loading} className="refresh-btn">
                {loading ? '⟳' : '🔄'}
              </button>
            </div>

            <div className="symbol-grid">
              {commonSymbols.map(symbol => (
                <button
                  key={symbol}
                  className={`symbol-btn ${selectedSymbol === symbol ? 'active' : ''}`}
                  onClick={() => setSelectedSymbol(symbol)}
                >
                  {symbol}
                </button>
              ))}
            </div>
          </div>

          {quote && (
            <div className="panel-section quote-section">
              <h3>{selectedSymbol} Quote</h3>
              <div className="quote-details">
                <div className="quote-item">
                  <span>Current Price:</span>
                  <strong>${quote.price?.toFixed(2) || 'N/A'}</strong>
                </div>
                <div className="quote-item">
                  <span>High:</span>
                  <span>${quote.high?.toFixed(2) || 'N/A'}</span>
                </div>
                <div className="quote-item">
                  <span>Low:</span>
                  <span>${quote.low?.toFixed(2) || 'N/A'}</span>
                </div>
                <div className="quote-item">
                  <span>Volume:</span>
                  <span>{(quote.volume / 1000000)?.toFixed(1)}M</span>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* Right Panel - Trade Execution */}
        <div className="trading-panel right-panel">
          <div className="panel-section">
            <h3>Trade Execution</h3>
            
            <div className="mode-selector">
              <label>
                <input
                  type="radio"
                  checked={paperMode}
                  onChange={() => setPaperMode(true)}
                />
                📄 Paper Trading (Practice)
              </label>
              <label>
                <input
                  type="radio"
                  checked={!paperMode}
                  onChange={() => setPaperMode(false)}
                />
                💰 Real Trading
              </label>
            </div>

            <div className="form-group">
              <label>Portfolio</label>
              <select
                value={selectedPortfolio || ''}
                onChange={(e) => setSelectedPortfolio(parseInt(e.target.value))}
              >
                {portfolios.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.name} (Capital: ${p.starting_capital.toFixed(2)})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Direction</label>
                <select
                  name="direction"
                  value={tradeForm.direction}
                  onChange={handleInputChange}
                >
                  <option value="BUY">🔼 BUY</option>
                  <option value="SELL">🔽 SELL</option>
                </select>
              </div>

              <div className="form-group">
                <label>Quantity</label>
                <input
                  type="number"
                  name="quantity"
                  value={tradeForm.quantity}
                  onChange={handleInputChange}
                  min="1"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Entry Price ($)</label>
              <input
                type="number"
                name="entryPrice"
                value={tradeForm.entryPrice}
                onChange={handleInputChange}
                step="0.01"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Stop Loss ($)</label>
                <input
                  type="number"
                  name="stopLoss"
                  value={tradeForm.stopLoss}
                  onChange={handleInputChange}
                  step="0.01"
                />
              </div>

              <div className="form-group">
                <label>Take Profit ($)</label>
                <input
                  type="number"
                  name="takeProfit"
                  value={tradeForm.takeProfit}
                  onChange={handleInputChange}
                  step="0.01"
                />
              </div>
            </div>

            <button 
              onClick={calculatePrices} 
              className="auto-calc-btn"
            >
              Auto Calculate SL/TP
            </button>

            <div className="risk-reward-section">
              <div className={`rr-metric ${rrValid ? 'valid' : 'invalid'}`}>
                <span>Risk/Reward Ratio:</span>
                <strong>{riskRewardRatio}:1</strong>
              </div>
              <div className={`rr-status ${rrValid ? 'green' : 'red'}`}>
                {rrValid ? '✓ Valid' : '✗ Below minimum (1.5:1)'}
              </div>
            </div>

            <div className="form-group">
              <label>Trade Reasoning</label>
              <textarea
                name="reasoning"
                value={tradeForm.reasoning}
                onChange={handleInputChange}
                placeholder="Enter your trading reasoning..."
                rows="3"
              />
            </div>

            <button
              onClick={executeTrade}
              className={`execute-btn ${!rrValid ? 'disabled' : ''}`}
              disabled={!rrValid || !selectedPortfolio}
            >
              {paperMode ? '📄 Execute Paper Trade' : '💰 Execute Live Trade'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
