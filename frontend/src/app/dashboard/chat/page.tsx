'use client';

import { useState, useRef, useEffect } from 'react';
import { api } from '@/lib/api';
import type { ChatMessageResponse, ChatMessage } from '@/types';

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput('');

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(), role: 'user', content: userMsg, created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const resp = await api.post<ChatMessageResponse>('/api/v1/chat/message', {
        message: userMsg, session_id: sessionId,
      });
      setSessionId(resp.session_id);

      const assistantMessage: ChatMessage = {
        id: resp.message_id, role: 'assistant', content: resp.content,
        sources: resp.sources, created_at: resp.timestamp,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      setMessages((prev) => [...prev, {
        id: crypto.randomUUID(), role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        created_at: new Date().toISOString(),
      }]);
    } finally { setLoading(false); }
  };

  const handleNewChat = () => { setMessages([]); setSessionId(null); };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 64px)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 700 }}>🤖 Medical AI Chatbot</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>RAG-powered medical guidance with source citations</p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={handleNewChat}>+ New Chat</button>
      </div>

      {/* Messages */}
      <div className="glass-card" style={{ flex: 1, padding: 24, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 20 }}>
        {messages.length === 0 && (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 16, color: 'var(--text-muted)' }}>
            <span style={{ fontSize: '3rem' }}>🤖</span>
            <p>Ask me any medical question. I&apos;ll provide answers grounded in medical knowledge.</p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
            <div style={{
              maxWidth: '75%', padding: '14px 18px', borderRadius: 16,
              background: msg.role === 'user' ? 'var(--gradient-primary)' : 'var(--bg-tertiary)',
              color: msg.role === 'user' ? 'white' : 'var(--text-primary)',
              borderBottomRightRadius: msg.role === 'user' ? 4 : 16,
              borderBottomLeftRadius: msg.role === 'user' ? 16 : 4,
            }}>
              <p style={{ fontSize: '0.95rem', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--border-color)' }}>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 6 }}>📚 Sources:</p>
                  {msg.sources.map((s, i) => (
                    <div key={i} style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 4 }}>
                      <strong>{s.title}</strong> — {s.content_snippet.substring(0, 100)}...
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <div style={{ padding: '14px 18px', borderRadius: 16, background: 'var(--bg-tertiary)', borderBottomLeftRadius: 4 }}>
              <div className="spinner" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
        <input
          className="input-field"
          placeholder="Ask a medical question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          disabled={loading}
          style={{ flex: 1 }}
        />
        <button className="btn btn-primary" onClick={handleSend} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}
