'use client';

import { useAuth } from '@/lib/auth';

const QUICK_ACTIONS = [
  { href: '/dashboard/predict', icon: '🔬', title: 'Predict Disease', desc: 'Analyze symptoms', gradient: 'linear-gradient(135deg, #06b6d4, #3b82f6)' },
  { href: '/dashboard/heart', icon: '❤️', title: 'Heart Assessment', desc: 'Check heart risk', gradient: 'linear-gradient(135deg, #ef4444, #f59e0b)' },
  { href: '/dashboard/drugs', icon: '💊', title: 'Find Drugs', desc: 'Get recommendations', gradient: 'linear-gradient(135deg, #10b981, #06b6d4)' },
  { href: '/dashboard/chat', icon: '🤖', title: 'AI Chatbot', desc: 'Ask medical questions', gradient: 'linear-gradient(135deg, #8b5cf6, #ec4899)' },
];

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="animate-fade-in">
      {/* Welcome Header */}
      <div style={{ marginBottom: 40 }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 700 }}>
          Welcome back, <span className="text-gradient">{user?.full_name?.split(' ')[0]}</span>
        </h1>
        <p style={{ color: 'var(--text-secondary)', marginTop: 8, fontSize: '1.05rem' }}>
          Your AI-powered health intelligence dashboard
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid-cols-4" style={{ marginBottom: 40 }}>
        {[
          { label: 'Disease Predictions', value: '—', icon: '🔬', color: '#06b6d4' },
          { label: 'Heart Assessments', value: '—', icon: '❤️', color: '#ef4444' },
          { label: 'Drug Searches', value: '—', icon: '💊', color: '#10b981' },
          { label: 'Chat Sessions', value: '—', icon: '💬', color: '#8b5cf6' },
        ].map((stat, idx) => (
          <div key={idx} className="glass-card" style={{ padding: 24 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 8 }}>{stat.label}</p>
                <p style={{ fontSize: '2rem', fontWeight: 700, color: stat.color }}>{stat.value}</p>
              </div>
              <span style={{ fontSize: '1.5rem' }}>{stat.icon}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <h3 style={{ marginBottom: 20, fontWeight: 600 }}>Quick Actions</h3>
      <div className="grid-cols-2" style={{ marginBottom: 40 }}>
        {QUICK_ACTIONS.map((action, idx) => (
          <a
            key={idx}
            href={action.href}
            className="glass-card"
            style={{
              padding: 28, display: 'flex', gap: 20, alignItems: 'center',
              textDecoration: 'none', color: 'inherit',
            }}
          >
            <div style={{
              width: 56, height: 56, borderRadius: 14, display: 'flex',
              alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem',
              background: action.gradient, flexShrink: 0,
            }}>
              {action.icon}
            </div>
            <div>
              <h4 style={{ marginBottom: 4 }}>{action.title}</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{action.desc}</p>
            </div>
          </a>
        ))}
      </div>

      {/* System Status */}
      <h3 style={{ marginBottom: 20, fontWeight: 600 }}>System Status</h3>
      <div className="glass-card" style={{ padding: 24 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {[
            { name: 'API Server', status: 'Online', color: 'var(--accent-success)' },
            { name: 'Disease Model (RandomForest)', status: 'Ready', color: 'var(--accent-success)' },
            { name: 'Heart Model (LightGBM)', status: 'Ready', color: 'var(--accent-success)' },
            { name: 'RAG Pipeline (FAISS + LLM)', status: 'Ready', color: 'var(--accent-success)' },
            { name: 'MLflow Tracking', status: 'Connected', color: 'var(--accent-success)' },
          ].map((service, idx) => (
            <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.9rem' }}>{service.name}</span>
              <span className="badge" style={{
                background: `${service.color}22`, color: service.color,
              }}>
                ● {service.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
