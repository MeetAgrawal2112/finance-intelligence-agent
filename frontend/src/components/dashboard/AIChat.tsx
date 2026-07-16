import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Trash2 } from 'lucide-react'
import { useNLQ } from '../../hooks/useNLQ'
import { format } from 'date-fns'

const SUGGESTIONS = [
  "Is mahine mera total kharch kitna hai?",
  "Kitna save kar sakta hoon?",
  "Koi suspicious transaction hai?",
  "Next month forecast kya hai?",
  "Dining pe kitna kharch hua?",
]

export default function AIChat() {
  const { messages, sendMessage, isLoading, clearChat } = useNLQ()
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = () => {
    if (!input.trim()) return
    sendMessage(input.trim())
    setInput('')
  }

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', height: '500px', padding: 0, overflow: 'hidden' }}>

      {/* Header */}
      <div style={{
        padding: '1rem 1.25rem',
        borderBottom: '1px solid #f1f5f9',
        display: 'flex', alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{
            width: '32px', height: '32px', background: '#f0f9ff',
            borderRadius: '0.5rem', display: 'flex',
            alignItems: 'center', justifyContent: 'center',
          }}>
            <Bot size={18} color="#0284c7" />
          </div>
          <div>
            <p style={{ margin: 0, fontWeight: 600, fontSize: '0.875rem', color: '#0f172a' }}>
              Finance AI
            </p>
            <p style={{ margin: 0, fontSize: '0.7rem', color: '#22c55e' }}>
              ● Online
            </p>
          </div>
        </div>
        <button
          onClick={clearChat}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8' }}
          title="Clear chat"
        >
          <Trash2 size={16} />
        </button>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {messages.map(msg => (
          <div
            key={msg.id}
            style={{
              display: 'flex',
              gap: '0.5rem',
              flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
            }}
          >
            {/* Avatar */}
            <div style={{
              width: '28px', height: '28px', flexShrink: 0,
              borderRadius: '50%',
              background: msg.role === 'user' ? '#0284c7' : '#f0f9ff',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              {msg.role === 'user'
                ? <User size={14} color="white" />
                : <Bot size={14} color="#0284c7" />
              }
            </div>

            {/* Bubble */}
            <div style={{
              maxWidth: '75%',
              padding: '0.625rem 0.875rem',
              borderRadius: msg.role === 'user'
                ? '1rem 0.25rem 1rem 1rem'
                : '0.25rem 1rem 1rem 1rem',
              background: msg.role === 'user' ? '#0284c7' : '#f8fafc',
              border: msg.role === 'assistant' ? '1px solid #f1f5f9' : 'none',
            }}>
              {msg.isLoading ? (
                <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                  <div style={{ width: '6px', height: '6px', background: '#94a3b8', borderRadius: '50%', animation: 'bounce 1s infinite' }} />
                  <div style={{ width: '6px', height: '6px', background: '#94a3b8', borderRadius: '50%', animation: 'bounce 1s infinite 0.2s' }} />
                  <div style={{ width: '6px', height: '6px', background: '#94a3b8', borderRadius: '50%', animation: 'bounce 1s infinite 0.4s' }} />
                </div>
              ) : (
                <p style={{
                  margin: 0,
                  fontSize: '0.8rem',
                  lineHeight: 1.6,
                  color: msg.role === 'user' ? 'white' : '#374151',
                  whiteSpace: 'pre-wrap',
                }}>
                  {msg.content}
                </p>
              )}
              <p style={{
                margin: '4px 0 0',
                fontSize: '0.65rem',
                color: msg.role === 'user' ? 'rgba(255,255,255,0.6)' : '#cbd5e1',
                textAlign: msg.role === 'user' ? 'right' : 'left',
              }}>
                {format(msg.timestamp, 'HH:mm')}
              </p>
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div style={{ padding: '0 1rem 0.5rem', display: 'flex', gap: '0.375rem', flexWrap: 'wrap' }}>
          {SUGGESTIONS.map(s => (
            <button
              key={s}
              onClick={() => { sendMessage(s) }}
              style={{
                background: '#f0f9ff', border: '1px solid #bae6fd',
                borderRadius: '2rem', padding: '0.25rem 0.625rem',
                fontSize: '0.7rem', color: '#0284c7', cursor: 'pointer',
              }}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div style={{
        padding: '0.75rem 1rem',
        borderTop: '1px solid #f1f5f9',
        display: 'flex', gap: '0.5rem',
      }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Kuch bhi poochho apne finances ke baare mein..."
          disabled={isLoading}
          style={{
            flex: 1, padding: '0.625rem 0.875rem',
            borderRadius: '2rem', border: '1px solid #e2e8f0',
            fontSize: '0.8rem', outline: 'none',
            background: '#f8fafc',
          }}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          style={{
            width: '36px', height: '36px', borderRadius: '50%',
            background: '#0284c7', border: 'none', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            opacity: (isLoading || !input.trim()) ? 0.5 : 1,
          }}
        >
          {isLoading
            ? <Loader2 size={16} color="white" className="animate-spin" />
            : <Send size={16} color="white" />
          }
        </button>
      </div>
    </div>
  )
}