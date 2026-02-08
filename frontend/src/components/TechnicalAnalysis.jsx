import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import './TechnicalAnalysis.css';

export default function TechnicalAnalysis({ symbol }) {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (symbol) {
      fetchAnalysis();
    }
  }, [symbol]);

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/analysis/technical/${symbol}`);
      setAnalysis(response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch technical analysis');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="analysis-container">Loading analysis...</div>;
  if (!analysis) return null;

  const getSignalColor = (signal) => {
    switch (signal) {
      case 'BUY':
        return '#10b981';
      case 'SELL':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  return (
    <div className="analysis-container">
      <div className="analysis-header">
        <h3>Technical Analysis - {symbol}</h3>
        <div className="signal-badge" style={{ backgroundColor: getSignalColor(analysis.signal) }}>
          {analysis.signal} (Confidence: {(analysis.confidence * 100).toFixed(0)}%)
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="indicators-grid">
        {/* RSI Indicator */}
        <div className="indicator-card">
          <div className="indicator-name">RSI (14)</div>
          <div className="indicator-value">{analysis.rsi?.toFixed(2) || 'N/A'}</div>
          <div className="indicator-bar">
            <div className="rsi-gauge">
              <div className="gauge-zone oversold">Oversold (30)</div>
              <div className="gauge-zone neutral">Neutral (30-70)</div>
              <div className="gauge-zone overbought">Overbought (70)</div>
              {analysis.rsi && (
                <div
                  className="gauge-pointer"
                  style={{ left: `${(analysis.rsi / 100) * 100}%` }}
                />
              )}
            </div>
          </div>
          <div className="indicator-signal">
            {analysis.rsi < 30 ? '⬆️ Oversold' : analysis.rsi > 70 ? '⬇️ Overbought' : '➡️ Neutral'}
          </div>
        </div>

        {/* MACD Indicator */}
        {analysis.macd && (
          <div className="indicator-card">
            <div className="indicator-name">MACD</div>
            <div className="macd-values">
              <div className="macd-line">
                <span>MACD:</span>
                <span className="value">{analysis.macd.macd.toFixed(4)}</span>
              </div>
              <div className="signal-line">
                <span>Signal:</span>
                <span className="value">{analysis.macd.signal.toFixed(4)}</span>
              </div>
              <div className="histogram">
                <span>Histogram:</span>
                <span className={`value ${analysis.macd.histogram > 0 ? 'positive' : 'negative'}`}>
                  {analysis.macd.histogram.toFixed(4)}
                </span>
              </div>
            </div>
            <div className="indicator-signal">
              {analysis.macd.histogram > 0 ? '📈 Bullish' : '📉 Bearish'}
            </div>
          </div>
        )}

        {/* Volume Analysis */}
        {analysis.volume_analysis && (
          <div className="indicator-card">
            <div className="indicator-name">Volume Analysis</div>
            <div className="volume-stats">
              <div className="stat-row">
                <span>Avg Volume:</span>
                <span>{(analysis.volume_analysis.avg_volume / 1000000).toFixed(2)}M</span>
              </div>
              <div className="stat-row">
                <span>Current Volume:</span>
                <span>{(analysis.volume_analysis.current_volume / 1000000).toFixed(2)}M</span>
              </div>
              <div className="stat-row">
                <span>Ratio:</span>
                <span className={analysis.volume_analysis.volume_above_avg ? 'above' : 'below'}>
                  {analysis.volume_analysis.volume_ratio.toFixed(2)}x
                </span>
              </div>
              <div className="stat-row">
                <span>Price Change:</span>
                <span className={analysis.volume_analysis.price_change > 0 ? 'positive' : 'negative'}>
                  {analysis.volume_analysis.price_change > 0 ? '+' : ''}
                  {analysis.volume_analysis.price_change.toFixed(2)}%
                </span>
              </div>
            </div>
            <div className="indicator-signal">
              {analysis.volume_analysis.strength === 'bullish' && '🔺 Bullish'}
              {analysis.volume_analysis.strength === 'bearish' && '🔻 Bearish'}
              {analysis.volume_analysis.strength === 'neutral' && '➡️ Neutral'}
            </div>
          </div>
        )}
      </div>

      <div className="analysis-footer">
        <button onClick={fetchAnalysis} className="btn-refresh">
          🔄 Refresh Analysis
        </button>
        <span className="timestamp">
          Last updated: {new Date(analysis.timestamp).toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
}
