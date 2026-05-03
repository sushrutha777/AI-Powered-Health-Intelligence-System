'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { useEffect } from 'react';

const FEATURES = [
  {
    icon: '🔬',
    title: 'Disease Prediction',
    description: 'AI-powered symptom analysis using RandomForest to predict potential diseases with confidence scores.',
    gradient: 'linear-gradient(135deg, #06b6d4, #3b82f6)',
  },
  {
    icon: '💊',
    title: 'Drug Recommendations',
    description: 'NLP-based drug matching using TF-IDF and cosine similarity for personalized recommendations.',
    gradient: 'linear-gradient(135deg, #10b981, #06b6d4)',
  },
  {
    icon: '🤖',
    title: 'Medical AI Chatbot',
    description: 'RAG-powered chatbot with FAISS retrieval and LLM generation for medical guidance.',
    gradient: 'linear-gradient(135deg, #8b5cf6, #ec4899)',
  },
];

export default function LandingPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  return (
    <div style={{ minHeight: '100vh', position: 'relative', overflow: 'hidden' }}>
      {/* Background Effects */}
      <div style={{
        position: 'fixed', inset: 0, zIndex: 0,
        background: 'radial-gradient(ellipse at 20% 50%, rgba(6, 182, 212, 0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(139, 92, 246, 0.08) 0%, transparent 50%), radial-gradient(ellipse at 50% 80%, rgba(16, 185, 129, 0.05) 0%, transparent 50%)',
      }} />

      {/* Navigation */}
      <nav style={{
        position: 'relative', zIndex: 10, display: 'flex', justifyContent: 'space-between',
        alignItems: 'center', padding: '20px 40px', maxWidth: 1200, margin: '0 auto',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: '1.8rem' }}>🏥</span>
          <span style={{ fontSize: '1.2rem', fontWeight: 700 }} className="text-gradient">
            Health Intelligence
          </span>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="btn btn-ghost" onClick={() => router.push('/login')}>Sign In</button>
          <button className="btn btn-primary" onClick={() => router.push('/register')}>Get Started</button>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{
        position: 'relative', zIndex: 10, textAlign: 'center',
        padding: '80px 24px 40px', maxWidth: 900, margin: '0 auto',
      }}>
        <div className="animate-fade-in">
          <div style={{
            display: 'inline-block', padding: '6px 16px', borderRadius: 9999,
            background: 'rgba(6, 182, 212, 0.1)', border: '1px solid rgba(6, 182, 212, 0.2)',
            fontSize: '0.85rem', color: 'var(--accent-primary)', marginBottom: 24,
          }}>
            ✨ AI-Powered Healthcare Intelligence
          </div>
          <h1 style={{ fontSize: '3.5rem', fontWeight: 800, lineHeight: 1.15, marginBottom: 24 }}>
            Your Health, Powered by{' '}
            <span className="text-gradient">Artificial Intelligence</span>
          </h1>
          <p style={{
            fontSize: '1.2rem', color: 'var(--text-secondary)',
            maxWidth: 600, margin: '0 auto 40px', lineHeight: 1.7,
          }}>
            Advanced machine learning models for disease prediction,
            drug recommendations, and an intelligent medical chatbot — all in one platform.
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 16 }}>
            <button className="btn btn-primary btn-lg" onClick={() => router.push('/register')}>
              Start Free →
            </button>
            <button className="btn btn-secondary btn-lg" onClick={() => router.push('/login')}>
              Sign In
            </button>
          </div>
        </div>
      </section>

      {/* Feature Cards */}
      <section style={{
        position: 'relative', zIndex: 10,
        padding: '60px 24px 100px', maxWidth: 1200, margin: '0 auto',
      }}>
        <div className="grid-cols-2" style={{ maxWidth: 1000, margin: '0 auto' }}>
          {FEATURES.map((feature, idx) => (
            <div
              key={idx}
              className="glass-card animate-fade-in"
              style={{
                padding: 32, animationDelay: `${idx * 0.1}s`,
                animationFillMode: 'both',
              }}
            >
              <div style={{
                width: 56, height: 56, borderRadius: 16, display: 'flex',
                alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem',
                background: feature.gradient, marginBottom: 20,
                boxShadow: '0 4px 15px rgba(0,0,0,0.3)',
              }}>
                {feature.icon}
              </div>
              <h3 style={{ marginBottom: 12, fontSize: '1.2rem' }}>{feature.title}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.7 }}>
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
