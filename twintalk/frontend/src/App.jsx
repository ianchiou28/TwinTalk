import { useState, useEffect } from 'react'
import { isLoggedIn, logout, getMe } from './services/api'
import Onboarding from './pages/Onboarding'
import World from './pages/World'
import Ego from './pages/Ego'
import './index.css'

const PAGES = {
  world: { icon: '', label: '世界' },
  ego: { icon: '', label: '本我' },
}

export default function App() {
  const [user, setUser] = useState(null)
  const [page, setPage] = useState('ego')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isLoggedIn()) {
      getMe()
        .then((data) => setUser(data.user))
        .catch(() => logout())
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
    setPage('ego')
  }

  if (loading) {
    return (
      <div className="onboarding-container">
        <div className="loading-dots"><span /><span /><span /></div>
      </div>
    )
  }

  // Not logged in, or logged in but hasn't completed onboarding
  if (!user || !user.onboarding_completed) {
    return <Onboarding onLogin={handleLogin} />
  }

  const handleLogout = () => {
    logout()
    setUser(null)
  }

  const renderPage = () => (page === 'world' ? <World /> : <Ego />)

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <h1>TwinTalk</h1>
        </div>

        <nav className="sidebar-nav">
          {Object.entries(PAGES).map(([key, { icon, label }]) => (
            <button
              key={key}
              className={`nav-item ${page === key ? 'active' : ''}`}
              onClick={() => {
                setPage(key)
              }}
            >
              <span className="nav-icon">{icon}</span>
              <span>{label}</span>
            </button>
          ))}
        </nav>

        <div style={{
          borderTop: '1px solid rgba(255,255,255,0.1)',
          paddingTop: '16px',
          marginTop: 'auto',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '8px 14px',
            marginBottom: '8px',
          }}>
            <div style={{
              width: '32px',
              height: '32px',
              background: 'var(--accent-danger)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '14px',
              fontWeight: '900',
              color: 'white',
              flexShrink: 0,
              fontFamily: "'Space Mono', monospace",
            }}>
              {(user.nickname || '?').charAt(0).toUpperCase()}
            </div>
            <div style={{ overflow: 'hidden' }}>
              <div style={{ fontSize: '13px', fontWeight: '700', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                {user.nickname}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: "'Space Mono', monospace" }}>
                v{user.profile_version || 0}
              </div>
            </div>
          </div>
          <button
            className="nav-item"
            onClick={handleLogout}
            style={{ fontSize: '13px', color: 'var(--text-muted)' }}
          >
            <span>退出</span>
          </button>
        </div>
      </aside>

      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  )
}
