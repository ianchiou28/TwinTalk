import { useEffect, useMemo, useRef, useState } from 'react'
import { getDmStats, getMyProfile, sendMessage, addMemory, getAlignmentQuestions, submitAlignmentAnswers } from '../services/api'

function LabOverview({ profile, stats, onGoCalibration, fitnessIndex }) {
  const syncRate = fitnessIndex || 50;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '16px', maxWidth: '760px' }}>
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', marginBottom: '12px' }}>
          <h3>构造空间</h3>
        </div>
        <div style={{ fontSize: '15px', marginBottom: '8px' }}>
          拟合度指数：<strong>{syncRate}%</strong>
        </div>
        <div className="progress-bar" style={{ marginBottom: '10px' }}>
          <div className="progress-fill" style={{ width: `${syncRate}%` }} />
        </div>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          {syncRate >= 85
            ? '拟合度较高，建议通过私信场景继续微调“价值观边界”。'
            : '当前拟合度仍可提升，建议补充问卷与关键记忆。'}
        </p>
        <div style={{ marginTop: '10px', fontSize: '13px', color: 'var(--text-secondary)' }}>
          本周你发送私信 {stats.sent_messages_week} 条
        </div>
      </div>
    </div>
  )
}

function CalibrationPanel({ onSynced, onScoreChange }) {
  const [syncing, setSyncing] = useState(false)
  const [memoryInput, setMemoryInput] = useState('')
  const [answers, setAnswers] = useState({})
  const [questions, setQuestions] = useState([])
  const [loadingQs, setLoadingQs] = useState(true)

  useEffect(() => {
    getAlignmentQuestions()
      .then(res => setQuestions(res.questions || []))
      .catch(err => alert("无法加载对齐问题：" + err.message))
      .finally(() => setLoadingQs(false))
  }, [])

  const completed = questions.length > 0 && questions.every((q) => answers[q.id])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', maxWidth: '760px' }}>
      <div className="glass-card">
        <h3 style={{ marginBottom: '8px' }}>同步记忆</h3>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '10px' }}>
          输入一段与你相关的记忆事件或事实，数字分身将把它纳入核心认知中。
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <textarea
            className="form-textarea"
            rows={3}
            placeholder="例如：我非常讨厌香菜，吃火锅一定要点毛肚..."
            value={memoryInput}
            onChange={(e) => setMemoryInput(e.target.value)}
          />
          <button
            className="btn btn-primary"
            disabled={syncing || !memoryInput.trim()}
            onClick={async () => {
              setSyncing(true)
              try {
                await addMemory(memoryInput.trim())
                alert('记忆同步成功！')
                setMemoryInput('')
                onSynced()
              } catch (err) {
                alert(err.message)
              } finally {
                setSyncing(false)
              }
            }}
          >
            {syncing ? '同步中...' : '提交同步'}
          </button>
        </div>
      </div>

      <div className="glass-card">
        <h3 style={{ marginBottom: '8px' }}>人格对齐</h3>
        {loadingQs ? (
          <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>正在生成专属对齐问题...</div>
        ) : (
          <>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {questions.map((q) => (
                <div key={q.id}>
                  <div style={{ fontSize: '13px', marginBottom: '6px' }}>{q.title}</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {(q.options || []).map((opt) => (
                      <button
                        key={opt}
                        className={`btn btn-sm ${answers[q.id] === opt ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => setAnswers((prev) => ({ ...prev, [q.id]: opt }))}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            <button
              className="btn btn-primary"
              style={{ marginTop: '12px' }}
              disabled={!completed || syncing}
              onClick={async () => {
                setSyncing(true)
                try {
                  const payload = questions.map(q => ({
                    title: q.title,
                    choice: answers[q.id]
                  }))
                  await submitAlignmentAnswers(payload)
                  alert('已学习你的决策逻辑')
                  onScoreChange(30)
                  onSynced()
                  setAnswers({})
                  setQuestions([])
                  setLoadingQs(true)
                  getAlignmentQuestions()
                    .then(res => setQuestions(res.questions || []))
                    .finally(() => setLoadingQs(false))
                } catch (err) {
                  alert(err.message)
                } finally {
                  setSyncing(false)
                }
              }}
            >
              提交对齐
            </button>
          </>
        )}
      </div>
    </div>
  )
}

function MirrorPanel() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '嗨，我是你的数字孪生。在这里我们可以进行一场深层自我对谈。最近有什么想梳理的思绪，或是平时不常表现出来的真实想法吗？' }
  ])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [sessionId] = useState(`mirror_${Date.now()}`)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    const text = input.trim()
    if (!text || sending) return
    
    const newMessages = [...messages, { role: 'user', content: text }]
    setMessages(newMessages)
    setInput('')
    setSending(true)
    
    try {
      const data = await sendMessage(text, sessionId, 'mirror_test')
      setMessages([...newMessages, { role: 'assistant', content: data.reply || '...' }])
    } catch (err) {
      setMessages([...newMessages, { role: 'assistant', content: `出错了: ${err.message}` }])
    } finally {
      setSending(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', maxWidth: '760px', height: '600px' }}>
      <div className="glass-card" style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '12px', overflow: 'hidden' }}>
        <div style={{ borderLeft: '5px solid var(--text-primary)', paddingLeft: '12px', flexShrink: 0 }}>
          <h3 style={{ margin: 0 }}>镜像测试（自我对谈）</h3>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: '4px 0 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            与你自己的专属 Agent 聊天。它会主动挖掘你的人格特征并存入你的记忆库。
          </p>
        </div>
        
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px', padding: '10px 0' }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ display: 'flex', gap: '8px', alignItems: 'flex-start', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
              {msg.role === 'assistant' && (
                <div style={{ width: '28px', height: '28px', background: 'var(--text-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', flexShrink: 0, fontFamily: "'Space Mono', monospace", fontWeight: '700', color: 'var(--bg-secondary)' }}>
                  AI
                </div>
              )}
              <div style={{
                background: msg.role === 'assistant' ? 'var(--bg-secondary)' : 'var(--text-primary)',
                color: msg.role === 'assistant' ? 'var(--text-primary)' : 'var(--bg-secondary)',
                padding: '10px 14px',
                border: '1px solid var(--text-primary)',
                fontSize: '14px',
                lineHeight: 1.6,
                maxWidth: '75%',
              }}>
                {msg.content}
              </div>
              {msg.role === 'user' && (
                <div style={{ width: '28px', height: '28px', background: 'var(--accent-danger)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', flexShrink: 0, fontFamily: "'Space Mono', monospace", fontWeight: '700', color: 'var(--bg-secondary)' }}>
                  我
                </div>
              )}
            </div>
          ))}
          {sending && (
            <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start', opacity: 0.7 }}>
              <div style={{ width: '28px', height: '28px', background: 'var(--text-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', flexShrink: 0, color: 'var(--bg-secondary)' }}>AI</div>
              <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--text-primary)', padding: '10px 14px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div className="loading-dots"><span /><span /><span /></div>
                <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>正在思考...</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div style={{ display: 'flex', gap: '8px', flexShrink: 0, paddingTop: '10px', borderTop: '2px solid var(--text-primary)' }}>
          <input
            type="text"
            className="form-input"
            style={{ flex: 1 }}
            placeholder="写点真实的想法..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSend()
            }}
          />
          <button
            className="btn btn-primary"
            onClick={handleSend}
            disabled={sending || !input.trim()}
          >
            发送
          </button>
        </div>
      </div>
    </div>
  )
}

export default function Ego() {
  const [tab, setTab] = useState('lab')
  const [profile, setProfile] = useState(null)
  const [fitnessIndex, setFitnessIndex] = useState(50)
  const [stats, setStats] = useState({ sent_messages_week: 0 })
  const [manualBoost, setManualBoost] = useState(0)

  const reloadProfile = () => {
    Promise.all([getMyProfile(), getDmStats()])
      .then(([profileData, statsData]) => {
        setProfile(profileData.profile || null)
        setFitnessIndex(profileData.fitness_index || 50)
        setStats({ sent_messages_week: statsData.sent_messages_week || 0 })
      })
      .catch(() => {
        setProfile(null)
        setFitnessIndex(50)
        setStats({ sent_messages_week: 0 })
      })
  }

  useEffect(() => {
    reloadProfile()
  }, [])

  const effectiveProfile = useMemo(() => {
    if (!profile) return profile
    return {
      ...profile,
      interests: (profile.interests || []).slice(0, Math.max(0, (profile.interests || []).length + Math.floor(manualBoost / 10))),
    }
  }, [profile, manualBoost])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '4px' }}>
        <button className={`btn ${tab === 'lab' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('lab')}>构造室</button>
        <button className={`btn ${tab === 'calibration' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('calibration')}>画像维系</button>
        <button className={`btn ${tab === 'mirror' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('mirror')}>镜像测试</button>
      </div>

      {tab === 'lab' && (
        <LabOverview
          profile={effectiveProfile}
          stats={stats}
          onGoCalibration={() => setTab('calibration')}
          fitnessIndex={fitnessIndex + manualBoost}
        />
      )}

      {tab === 'calibration' && <CalibrationPanel onSynced={reloadProfile} onScoreChange={(delta) => setManualBoost((v) => v + delta)} />}

      {tab === 'mirror' && <MirrorPanel />}
    </div>
  )
}
