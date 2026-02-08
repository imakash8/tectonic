import { useState, useEffect } from 'react'
import { apiService } from '../services/api'
import './Premium.css'

export default function Premium() {
  const [plans, setPlans] = useState([])
  const [subscriptionStatus, setSubscriptionStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [selectedPlan, setSelectedPlan] = useState(null)

  useEffect(() => {
    fetchPlans()
    fetchSubscriptionStatus()
  }, [])

  const fetchPlans = async () => {
    try {
      const response = await apiService.api.get('/payments/plans')
      setPlans(response.data.plans)
    } catch (err) {
      setError('Failed to load plans: ' + err.message)
      console.error('Error fetching plans:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchSubscriptionStatus = async () => {
    try {
      const response = await apiService.api.get('/payments/subscription-status')
      setSubscriptionStatus(response.data)
    } catch (err) {
      console.warn('Could not fetch subscription status:', err.message)
    }
  }

  const handleSelectPlan = (planId) => {
    setSelectedPlan(planId)
    // TODO: Integrate Stripe Elements.js for payment
    alert(`Plan ${planId} selected. Stripe integration coming soon!`)
  }

  const handleCancelSubscription = async () => {
    if (!window.confirm('Are you sure you want to cancel your subscription?')) {
      return
    }

    try {
      setProcessing(true)
      await apiService.api.post('/payments/cancel-premium')
      setSubscriptionStatus({ is_premium: false })
      setError(null)
    } catch (err) {
      setError('Failed to cancel subscription: ' + err.message)
    } finally {
      setProcessing(false)
    }
  }

  if (loading) {
    return (
      <div className="premium">
        <div className="loading">Loading plans...</div>
      </div>
    )
  }

  return (
    <div className="premium">
      <div className="premium-header">
        <h1>🚀 Premium Features</h1>
        <p>Unlock advanced trading tools and real-time market data</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {/* Current Subscription Status */}
      {subscriptionStatus?.is_premium && (
        <div className="subscription-status">
          <div className="status-content">
            <h3>✅ You are a Premium Member</h3>
            <p>Plan: <strong>{subscriptionStatus.subscription_tier}</strong></p>
            {subscriptionStatus.subscription_expires && (
              <p>Expires: <strong>{new Date(subscriptionStatus.subscription_expires).toLocaleDateString()}</strong></p>
            )}
          </div>
          <button 
            className="cancel-btn"
            onClick={handleCancelSubscription}
            disabled={processing}
          >
            {processing ? 'Cancelling...' : 'Cancel Subscription'}
          </button>
        </div>
      )}

      {/* Plans Grid */}
      <div className="plans-grid">
        {plans.map((plan) => (
          <div key={plan.id} className="plan-card">
            <div className="plan-header">
              <h3>{plan.name}</h3>
              {plan.id === 'premium_yearly' && (
                <span className="save-badge">Save $89</span>
              )}
            </div>

            <div className="plan-price">
              <span className="currency">$</span>
              <span className="amount">{(plan.price / 100).toFixed(0)}</span>
              <span className="period">/{plan.billing_cycle}</span>
            </div>

            <ul className="plan-features">
              {plan.features.map((feature, idx) => (
                <li key={idx}>
                  <span className="check">✓</span>
                  {feature}
                </li>
              ))}
            </ul>

            {subscriptionStatus?.is_premium && subscriptionStatus?.subscription_tier === plan.id ? (
              <button className="current-plan-btn" disabled>
                Current Plan
              </button>
            ) : (
              <button 
                className="select-plan-btn"
                onClick={() => handleSelectPlan(plan.id)}
              >
                Upgrade Now
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Features Comparison */}
      <div className="features-section">
        <h2>What's Included in Premium?</h2>
        
        <div className="feature-grid">
          <div className="feature-card">
            <h4>📊 Real-Time Market Data</h4>
            <p>Get live prices from Finnhub API with 15-minute delayed fallback</p>
          </div>

          <div className="feature-card">
            <h4>🤖 AI Trading Signals</h4>
            <p>Advanced AI-powered trade recommendations based on market analysis</p>
          </div>

          <div className="feature-card">
            <h4>📈 Advanced Analytics</h4>
            <p>Deep portfolio analysis, performance metrics, and trading statistics</p>
          </div>

          <div className="feature-card">
            <h4>⚡ Unlimited Trades</h4>
            <p>Execute unlimited trades without restrictions or hidden limits</p>
          </div>

          <div className="feature-card">
            <h4>🔔 Trade Alerts</h4>
            <p>Real-time notifications for price levels and trading opportunities</p>
          </div>

          <div className="feature-card">
            <h4>👥 Priority Support</h4>
            <p>24/7 dedicated support team for all your trading questions</p>
          </div>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="faq-section">
        <h2>Frequently Asked Questions</h2>
        
        <div className="faq-items">
          <div className="faq-item">
            <h4>Can I upgrade or downgrade anytime?</h4>
            <p>Yes! You can change your plan or cancel anytime. Changes take effect at the end of your current billing cycle.</p>
          </div>

          <div className="faq-item">
            <h4>What payment methods do you accept?</h4>
            <p>We accept all major credit cards, debit cards, and digital payment methods through Stripe.</p>
          </div>

          <div className="faq-item">
            <h4>Is there a free trial?</h4>
            <p>Yes! All new users get a 7-day free trial of Premium features. No credit card required.</p>
          </div>

          <div className="faq-item">
            <h4>What if I need to cancel?</h4>
            <p>You can cancel anytime from your account settings. Your Premium access continues until the end of the current billing period.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
