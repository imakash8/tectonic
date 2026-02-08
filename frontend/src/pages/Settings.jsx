import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import '../pages/Dashboard.css' // Reuse dashboard styles

export default function Settings() {
  const navigate = useNavigate()
  const [settings, setSettings] = useState({
    notifications: true,
    darkMode: false,
    emailAlerts: true
  })

  const handleChange = (key) => {
    setSettings(prev => ({ ...prev, [key]: !prev[key] }))
  }

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
        <h1>⚙️ Settings</h1>
      </div>

      <div style={{ backgroundColor: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <div style={{ marginBottom: '20px', paddingBottom: '20px', borderBottom: '1px solid #eee' }}>
          <h3>Notifications</h3>
          <label style={{ display: 'block', marginTop: '10px' }}>
            <input 
              type="checkbox" 
              checked={settings.notifications}
              onChange={() => handleChange('notifications')}
            />
            {' '}Enable push notifications
          </label>
          <label style={{ display: 'block', marginTop: '10px' }}>
            <input 
              type="checkbox" 
              checked={settings.emailAlerts}
              onChange={() => handleChange('emailAlerts')}
            />
            {' '}Enable email alerts
          </label>
        </div>

        <div style={{ marginBottom: '20px', paddingBottom: '20px', borderBottom: '1px solid #eee' }}>
          <h3>Appearance</h3>
          <label style={{ display: 'block', marginTop: '10px' }}>
            <input 
              type="checkbox" 
              checked={settings.darkMode}
              onChange={() => handleChange('darkMode')}
            />
            {' '}Dark mode
          </label>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h3>Account</h3>
          <button style={{ 
            padding: '10px 16px', 
            backgroundColor: '#dc3545', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px', 
            cursor: 'pointer',
            marginTop: '10px'
          }}>
            Change Password
          </button>
        </div>
      </div>
    </div>
  )
}
