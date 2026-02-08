import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import './Watchlist.css';

export default function Watchlist() {
  const [watchlist, setWatchlist] = useState([]);
  const [newSymbol, setNewSymbol] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const fetchWatchlist = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/watchlist');
      setWatchlist(response.data);
    } catch (err) {
      console.error('Watchlist error:', err);
      // Don't show error if user has empty watchlist and server responds with 404
      if (err.response?.status === 404) {
        setWatchlist([]);
      } else {
        setError('Unable to load watchlist. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const addSymbol = async () => {
    if (!newSymbol.trim()) {
      setError('Please enter a symbol');
      return;
    }

    try {
      await api.post('/watchlist', { symbol: newSymbol.toUpperCase() });
      setNewSymbol('');
      fetchWatchlist();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add symbol');
    }
  };

  const removeSymbol = async (symbol) => {
    try {
      await api.delete(`/watchlist/${symbol}`);
      fetchWatchlist();
    } catch (err) {
      setError('Failed to remove symbol');
    }
  };

  if (loading) return <div className="watchlist-container">Loading...</div>;

  return (
    <div className="watchlist-container">
      <div className="watchlist-header">
        <h2>My Watchlist</h2>
        <p className="watchlist-count">{watchlist.length} symbols tracked</p>
      </div>

      <div className="watchlist-input">
        <input
          type="text"
          value={newSymbol}
          onChange={(e) => setNewSymbol(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addSymbol()}
          placeholder="Enter symbol (e.g., AAPL)"
          className="symbol-input"
        />
        <button onClick={addSymbol} className="btn-add">
          + Add to Watchlist
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="watchlist-items">
        {watchlist.length === 0 ? (
          <div className="empty-state">
            <p>No symbols in your watchlist yet</p>
            <p className="empty-hint">Add symbols to track their performance</p>
          </div>
        ) : (
          watchlist.map((item) => (
            <div key={item.id} className="watchlist-item">
              <div className="item-content">
                <span className="item-symbol">{item.symbol}</span>
                <span className="item-date">Added: {new Date(item.added_at).toLocaleDateString()}</span>
              </div>
              <button
                onClick={() => removeSymbol(item.symbol)}
                className="btn-remove"
                title="Remove from watchlist"
              >
                ✕
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
