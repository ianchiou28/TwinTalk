import { useEffect, useState } from 'react'
import { findMatches, followUser, unfollowUser } from '../services/api'

function MatchCard({ match, onStartDm, isFollowing, onFollowChange }) {
  const [isFollowingLocal, setIsFollowingLocal] = useState(isFollowing)

  const handleFollow = async () => {
    try {
      if (isFollowingLocal) {
        await unfollowUser(match.user.id)
        setIsFollowingLocal(false)
      } else {
        await followUser(match.user.id)
        setIsFollowingLocal(true)
      }
      onFollowChange?.()
    } catch (error) {
      console.error('关注操作失败:', error)
    }
  }

  return (
    <div className="glass-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '10px' }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: '700', fontSize: '16px' }}>{match.user.nickname}</div>
          <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
            共同兴趣: {match.common_count || 0} 项
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
            匹配度: {Math.round((match.score || 0) * 100)}%
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px', flexShrink: 0 }}>
          <button
            className={`btn btn-sm ${isFollowingLocal ? 'btn-secondary' : 'btn-ghost'}`}
            onClick={handleFollow}
          >
            {isFollowingLocal ? '✓ 已关注' : '关注'}
          </button>
          <button className="btn btn-sm btn-primary" onClick={() => onStartDm(match.user.id)}>
            私信
          </button>
        </div>
      </div>

      {match.bio_third_view && (
        <div style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.5' }}>
          {match.bio_third_view}
        </div>
      )}

      {match.common_interests && match.common_interests.length > 0 && (
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '4px' }}>
          {match.common_interests.slice(0, 5).map((interest) => (
            <span
              key={interest}
              style={{
                fontSize: '12px',
                padding: '4px 8px',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '4px',
              }}
            >
              {interest}
            </span>
          ))}
          {match.common_interests.length > 5 && (
            <span style={{ fontSize: '12px', padding: '4px 0', color: 'var(--text-muted)' }}>
              +{match.common_interests.length - 5}
            </span>
          )}
        </div>
      )}
    </div>
  )
}

export default function Social({ onStartDm, onOpenMessages }) {
  const [matches, setMatches] = useState([])
  const [followingSet, setFollowingSet] = useState(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [refreshToken, setRefreshToken] = useState('init')

  const loadMatches = async (token = refreshToken) => {
    try {
      setLoading(true)
      const data = await findMatches(20, token)
      setMatches(data.matches || [])
      setError(null)
    } catch (err) {
      console.error('加载匹配用户失败:', err)
      setError(err.message || '加载失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMatches(refreshToken)
  }, [refreshToken])

  if (loading) {
    return (
      <div className="empty-state" style={{ minHeight: '320px' }}>
        <div className="loading-dots"><span /><span /><span /></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="empty-state">
        <p style={{ color: 'var(--text-error)' }}>⚠️ {error}</p>
        <button className="btn btn-primary" onClick={loadMatches} style={{ marginTop: '16px' }}>
          重试
        </button>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div>
        <h2 style={{ marginBottom: '12px' }}>🎯 为你推荐</h2>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px' }}>
          基于兴趣、性格、价值观、沟通风格综合匹配
        </p>
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => setRefreshToken(String(Date.now()))}
        >
          刷新重新匹配
        </button>
      </div>

      {matches.length === 0 ? (
        <div className="empty-state">
          <p style={{ color: 'var(--text-muted)' }}>暂无推荐用户</p>
          <button className="btn btn-primary" onClick={loadMatches} style={{ marginTop: '16px' }}>
            重新加载
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {matches.map((match) => (
            <MatchCard
              key={match.user.id}
              match={match}
              onStartDm={onStartDm}
              isFollowing={followingSet.has(match.user.id)}
              onFollowChange={() => {
                setFollowingSet((prev) => new Set(prev))
              }}
            />
          ))}
        </div>
      )}
    </div>
  )
}
