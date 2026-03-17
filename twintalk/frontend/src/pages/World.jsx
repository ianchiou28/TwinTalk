import { useEffect, useMemo, useRef, useState } from 'react'
import Social from './Social'
import {
  deleteDmConversation,
  getDmSuggestion,
  listDmConversations,
  listDmMessages,
  markDmRead,
  sendDmMessage,
  startDmConversation,
} from '../services/api'

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function getAvatarLabel(name) {
  if (!name) return '匿'
  return name.trim().slice(0, 1).toUpperCase()
}

function DmPanel({
  conversations,
  pinnedConversationIds,
  currentConversation,
  messages,
  onOpenConversation,
  onTogglePinConversation,
  onBackToList,
  onSend,
  onSuggest,
  input,
  setInput,
  sending,
  agentReply,
  setAgentReply,
  suggestion,
  suggesting,
  commonCommunities,
  onDelete,
}) {
  const bottomRef = useRef(null)
  const [searchKeyword, setSearchKeyword] = useState('')

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const filteredConversations = useMemo(() => {
    const keyword = searchKeyword.trim().toLowerCase()
    if (!keyword) return conversations

    return conversations.filter((conversation) => {
      const partnerName = (conversation.partner?.nickname || '').toLowerCase()
      const community = (conversation.source_community || '').toLowerCase()
      const preview = (conversation.last_message || '').toLowerCase()
      return partnerName.includes(keyword) || community.includes(keyword) || preview.includes(keyword)
    })
  }, [conversations, searchKeyword])

  const sortedConversations = useMemo(() => {
    const getLastTime = (conversation) => {
      const value = Date.parse(conversation.last_message_at || '')
      return Number.isNaN(value) ? 0 : value
    }

    return [...filteredConversations].sort((a, b) => {
      const pinnedA = pinnedConversationIds.includes(a.id)
      const pinnedB = pinnedConversationIds.includes(b.id)
      if (pinnedA !== pinnedB) return pinnedA ? -1 : 1

      const unreadA = a.unread_count || 0
      const unreadB = b.unread_count || 0
      if (unreadA !== unreadB) return unreadB - unreadA

      return getLastTime(b) - getLastTime(a)
    })
  }, [filteredConversations, pinnedConversationIds])

  const totalUnread = conversations.reduce((acc, conversation) => acc + (conversation.unread_count || 0), 0)

  if (!currentConversation) {
    return (
      <div className="glass-card dm-inbox-shell">
        <div className="dm-inbox-header">
          <div>
            <div className="dm-inbox-title">私信</div>
            <div className="dm-inbox-subtitle">按时间排序展示最近会话，点击进入聊天。</div>
          </div>
        </div>

        <div className="dm-inbox-toolbar">
          <input
            className="dm-inbox-search"
            type="text"
            value={searchKeyword}
            placeholder="搜索联系人 / 消息"
            onChange={(e) => setSearchKeyword(e.target.value)}
          />
          <div className="dm-inbox-stats">{sortedConversations.length} 个会话 · 未读 {totalUnread} · 置顶 {pinnedConversationIds.length}</div>
        </div>

        <div className="dm-inbox-list">
          {sortedConversations.length === 0 ? (
            <div className="empty-state" style={{ flex: 1 }}>
              <div className="empty-icon">✉️</div>
              <h3>{conversations.length === 0 ? '还没有私信' : '没有匹配结果'}</h3>
              <p>{conversations.length === 0 ? '先去推荐用户列表里发起一次私信，会话会出现在这里。' : '试试更换关键词，或清空搜索。'}</p>
            </div>
          ) : (
            sortedConversations.map((conversation) => {
              const partnerName = conversation.partner?.nickname || '未命名'
              const isPinned = pinnedConversationIds.includes(conversation.id)

              return (
                <div key={conversation.id} className="dm-inbox-item-wrap">
                  <button className="dm-inbox-item" onClick={() => onOpenConversation(conversation)} type="button">
                    <div className="dm-inbox-avatar">{getAvatarLabel(partnerName)}</div>
                    <div className="dm-inbox-body">
                      <div className="dm-inbox-row dm-inbox-row-top">
                        <strong>{partnerName}</strong>
                        <span className="dm-inbox-time">{formatTime(conversation.last_message_at)}</span>
                      </div>
                      {conversation.unread_count > 0 && (
                        <div className="dm-inbox-row dm-inbox-row-middle">
                          <span className="dm-inbox-unread">{conversation.unread_count}</span>
                        </div>
                      )}
                      <div className="dm-inbox-preview">{conversation.last_message || '点击进入会话'}</div>
                    </div>
                  </button>
                  <div className="dm-inbox-actions">
                    <button
                      className={`dm-pin-btn ${isPinned ? 'active' : ''}`}
                      onClick={() => onTogglePinConversation(conversation.id)}
                      type="button"
                      title={isPinned ? '取消置顶' : '置顶会话'}
                    >
                      {isPinned ? '置顶中' : '置顶'}
                    </button>
                    <button className="btn btn-sm btn-ghost" onClick={() => onDelete(conversation)} type="button">
                      删除
                    </button>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="glass-card dm-chat-shell" style={{ display: 'flex', flexDirection: 'column', minWidth: 0 }}>
      <div className="dm-chat-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0 }}>
          <button className="btn btn-ghost btn-sm" onClick={onBackToList} type="button">← 返回</button>
          <div className="dm-chat-avatar">{getAvatarLabel(currentConversation.partner?.nickname || '未知用户')}</div>
          <div style={{ minWidth: 0 }}>
            <div className="dm-chat-name">{currentConversation.partner?.nickname || '未知用户'}</div>
          </div>
        </div>
      </div>

      {commonCommunities.length > 0 && (
        <div style={{ marginTop: '10px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {commonCommunities.map((name) => (
            <span key={name} className="interest-tag" style={{ fontSize: '11px' }}>{name}</span>
          ))}
        </div>
      )}

      <div className="chat-messages dm-thread" style={{ flex: 1, overflowY: 'auto' }}>
        {messages.map((msg) => {
          const isPartner = msg.sender_id === currentConversation.partner?.id

          return (
            <div key={msg.id} className={`dm-message-row ${isPartner ? 'partner' : 'self'}`}>
              {isPartner && <div className="dm-message-avatar">{getAvatarLabel(currentConversation.partner?.nickname || '未知用户')}</div>}
              <div className={`chat-bubble ${isPartner ? 'assistant' : 'user'}`}>
                {msg.content}
                <div style={{ fontSize: '10px', opacity: 0.65, marginTop: '5px' }}>
                  {formatTime(msg.created_at)}
                </div>
              </div>
            </div>
          )
        })}
        <div ref={bottomRef} />
      </div>
      <div className="chat-input-bar dm-chat-input-bar">
        <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
          {['🙂', '😂', '👍', '❤️'].map((emoji) => (
            <button
              key={emoji}
              className="btn btn-sm btn-ghost"
              onClick={() => setInput((prev) => `${prev}${emoji}`)}
              type="button"
            >
              {emoji}
            </button>
          ))}
        </div>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入私信内容..."
          disabled={sending}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              onSend()
            }
          }}
        />
        <button className="btn btn-primary" onClick={onSend} disabled={sending || !input.trim()}>
          发送
        </button>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px', flexWrap: 'wrap' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-muted)' }}>
          <input
            type="checkbox"
            checked={agentReply}
            onChange={(e) => setAgentReply(e.target.checked)}
          />
          让对方 Agent 代聊
        </label>
        <button className="btn btn-sm btn-secondary" onClick={onSuggest} disabled={suggesting || !currentConversation}>
          {suggesting ? '生成中...' : '给我一句建议'}
        </button>
        {suggestion && (
          <button className="btn btn-sm btn-ghost" onClick={() => setInput(suggestion)}>
            使用建议
          </button>
        )}
      </div>
      {suggestion && (
        <div style={{ marginTop: '8px', fontSize: '13px', color: 'var(--text-muted)' }}>
          建议：{suggestion}
        </div>
      )}
    </div>
  )
}

export default function World() {
  const [tab, setTab] = useState('lobby')

  const [conversations, setConversations] = useState([])
  const [currentConversation, setCurrentConversation] = useState(null)
  const [messages, setMessages] = useState([])
  const [commonCommunities, setCommonCommunities] = useState([])
  const [dmInput, setDmInput] = useState('')
  const [dmSending, setDmSending] = useState(false)
  const [agentReply, setAgentReply] = useState(false)
  const [suggestion, setSuggestion] = useState('')
  const [suggesting, setSuggesting] = useState(false)
  const [pinnedConversationIds, setPinnedConversationIds] = useState([])

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem('dm_pinned_conversations')
      if (!saved) return
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed)) {
        setPinnedConversationIds(parsed.filter((id) => typeof id === 'number'))
      }
    } catch (error) {
      console.error('load pinned conversations failed', error)
    }
  }, [])

  useEffect(() => {
    window.localStorage.setItem('dm_pinned_conversations', JSON.stringify(pinnedConversationIds))
  }, [pinnedConversationIds])
  const refreshConversations = async (keepCurrent = true) => {
    const data = await listDmConversations()
    setConversations(data.conversations || [])

    if (keepCurrent && currentConversation) {
      const updated = (data.conversations || []).find((item) => item.id === currentConversation.id)
      if (updated) {
        setCurrentConversation(updated)
      }
    }
  }

  const openConversation = async (conv) => {
    setCurrentConversation(conv)
    try {
      const [msgData] = await Promise.all([
        listDmMessages(conv.id),
        markDmRead(conv.id).catch(() => {}),
      ])
      setMessages(msgData.messages || [])
      setSuggestion('')
      setCommonCommunities([])
      refreshConversations().catch(() => {})
    } catch (e) {
      console.error('openConversation error', e)
    }
  }

  const handleStartDm = async (targetUserId, sourceCommunity) => {
    try {
      const data = await startDmConversation(targetUserId, sourceCommunity)
      const newConversation = data.conversation
      
      // 先更新当前对话
      setCurrentConversation(newConversation)
      setTab('messages')
      
      // 然后刷新会话列表和消息
      const [msgData] = await Promise.all([
        listDmMessages(newConversation.id),
        refreshConversations(),
      ])
      setMessages(msgData.messages || [])
      setCommonCommunities([])
    } catch (e) {
      console.error('startDm error', e)
    }
  }

  const openMessageInbox = () => {
    setTab('messages')
    setCurrentConversation(null)
    setMessages([])
    setSuggestion('')
    setCommonCommunities([])
    refreshConversations(false).catch(console.error)
  }

  const handleSendDm = async () => {
    const content = dmInput.trim()
    if (!content || !currentConversation || dmSending) return

    setDmSending(true)
    setDmInput('')
    try {
      // Return immediately after user's message is saved; render it right away
      await sendDmMessage(currentConversation.id, content, agentReply)
      const conv = currentConversation
      const msgData = await listDmMessages(conv.id)
      setMessages(msgData.messages || [])
      refreshConversations().catch(() => {})

      // If agent reply is enabled, poll once after a delay to fetch the reply
      if (agentReply) {
        setTimeout(async () => {
          try {
            const laterData = await listDmMessages(conv.id)
            setMessages(laterData.messages || [])
            refreshConversations().catch(() => {})
          } catch (_) {}
        }, 3500)
      }
    } finally {
      setDmSending(false)
    }
  }

  const handleSuggest = async () => {
    if (!currentConversation || suggesting) return
    setSuggesting(true)
    try {
      const data = await getDmSuggestion(currentConversation.id)
      setSuggestion(data.suggestion?.text || '')
    } catch (e) {
      console.error('suggest dm error', e)
      setSuggestion('')
    } finally {
      setSuggesting(false)
    }
  }

  const handleDeleteConversation = async (conversation) => {
    await deleteDmConversation(conversation.id)
    setPinnedConversationIds((prev) => prev.filter((id) => id !== conversation.id))
    if (currentConversation?.id === conversation.id) {
      setCurrentConversation(null)
      setMessages([])
      setCommonCommunities([])
    }
    await refreshConversations()
  }

  const handleTogglePinConversation = (conversationId) => {
    setPinnedConversationIds((prev) => {
      if (prev.includes(conversationId)) {
        return prev.filter((id) => id !== conversationId)
      }
      return [conversationId, ...prev]
    })
  }

  useEffect(() => {
    listDmConversations()
      .then((convData) => setConversations(convData.conversations || []))
      .catch(console.error)
  }, [])

  const unreadCount = conversations.reduce((acc, c) => acc + (c.unread_count || 0), 0)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '4px' }}>
        <button className={`btn ${tab === 'lobby' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('lobby')}>推荐用户</button>
        <button className={`btn ${tab === 'messages' ? 'btn-primary' : 'btn-secondary'}`} onClick={openMessageInbox}>
          私信入口
          {unreadCount > 0 && <span className="card-badge">{unreadCount}</span>}
        </button>
      </div>

      {tab === 'lobby' && <Social onStartDm={handleStartDm} onOpenMessages={openMessageInbox} />}
      {tab === 'messages' && (
        <DmPanel
          conversations={conversations}
          pinnedConversationIds={pinnedConversationIds}
          currentConversation={currentConversation}
          messages={messages}
          onOpenConversation={openConversation}
          onTogglePinConversation={handleTogglePinConversation}
          onBackToList={openMessageInbox}
          onSuggest={handleSuggest}
          input={dmInput}
          setInput={setDmInput}
          sending={dmSending}
          agentReply={agentReply}
          setAgentReply={setAgentReply}
          suggestion={suggestion}
          suggesting={suggesting}
          onSend={handleSendDm}
          commonCommunities={commonCommunities}
          onDelete={handleDeleteConversation}
        />
      )}
    </div>
  )
}
