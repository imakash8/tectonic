import { useNavigate } from 'react-router-dom'
import '../pages/Dashboard.css'

export default function Help() {
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
        <h1>❓ Help & Support</h1>
      </div>

      <div style={{ backgroundColor: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <div style={{ marginBottom: '20px', paddingBottom: '20px', borderBottom: '1px solid #eee' }}>
          <h3>Frequently Asked Questions</h3>
          <div style={{ marginTop: '10px' }}>
            <h4>How do I place a trade?</h4>
            <p>Navigate to the Trading section, enter a stock symbol, enter your desired quantity, and click Execute Trade.</p>
          </div>
          <div style={{ marginTop: '15px' }}>
            <h4>How do I view my portfolio?</h4>
            <p>Click on Portfolio in the sidebar to see all your positions, equity, and performance metrics.</p>
          </div>
          <div style={{ marginTop: '15px' }}>
            <h4>What is the Trading Floor?</h4>
            <p>The Trading Floor is an advanced interface for executing complex trades with real-time market data.</p>
          </div>
        </div>

        <div style={{ marginBottom: '20px', paddingBottom: '20px', borderBottom: '1px solid #eee' }}>
          <h3>Contact Support</h3>
          <p>Email: <a href="mailto:support@tectonic.com">support@tectonic.com</a></p>
          <p>Live Chat: Available Monday-Friday, 9 AM - 5 PM EST</p>
        </div>

        <div>
          <h3>Video Tutorials</h3>
          <p>Check out our YouTube channel for step-by-step guides on using the platform.</p>
          <button style={{ 
            padding: '10px 16px', 
            backgroundColor: '#28a745', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px', 
            cursor: 'pointer'
          }}>
            Watch Tutorials
          </button>
        </div>
      </div>
    </div>
  )
}
