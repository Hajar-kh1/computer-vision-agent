// TEMP chat popup — floating widget that talks to the backend agent
// (POST /api/v1/chat). Same agent + tools as Open WebUI.

import { useEffect, useRef, useState } from 'react'
import { chat } from './api.js'

export default function ChatPopup() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    if (bottomRef.current) bottomRef.current.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading, open])

  const send = async () => {
    const text = input.trim()
    if (!text || loading) return
    setMessages((m) => [...m, { role: 'user', content: text }])
    setInput('')
    setLoading(true)
    setError(null)
    try {
      const res = await chat(text)
      setMessages((m) => [...m, { role: 'assistant', content: res.reply }])
    } catch (err) {
      setError(err.message || 'Agent failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {open && (
        <div className="chat-popup">
          <div className="chat-popup-header">
            <span>Package Damage Assistant</span>
            <button className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">×</button>
          </div>
          <div className="chat-popup-body">
            {messages.length === 0 && !loading && (
              <p className="chat-hint">
                Ask about predictions, statistics or the model — e.g. "Show me the latest two predictions".
              </p>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`chat-msg chat-${m.role}`}>{m.content}</div>
            ))}
            {loading && <div className="chat-msg chat-assistant chat-typing">…</div>}
            {error && <p className="error">{error}</p>}
            <div ref={bottomRef} />
          </div>
          <div className="chat-popup-input">
            <input
              value={input}
              placeholder="Ask the agent…"
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send()}
              disabled={loading}
            />
            <button onClick={send} disabled={!input.trim() || loading}>Send</button>
          </div>
        </div>
      )}
      <button className="chat-fab" onClick={() => setOpen((v) => !v)} aria-label="Toggle chat">
        {open ? '×' : '💬'}
      </button>
    </>
  )
}
