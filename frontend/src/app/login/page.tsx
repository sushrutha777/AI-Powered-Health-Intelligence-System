'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login({ email, password });
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: 24, position: 'relative',
      background: 'radial-gradient(ellipse at 30% 50%, rgba(6, 182, 212, 0.06) 0%, transparent 50%), radial-gradient(ellipse at 70% 30%, rgba(139, 92, 246, 0.06) 0%, transparent 50%)',
    }}>
      <div className="glass-card animate-fade-in" style={{ padding: 48, width: '100%', maxWidth: 440 }}>
        <div style={{ textAlign: 'center', marginBottom: 36 }}>
          <span style={{ fontSize: '2.5rem' }}>🏥</span>
          <h2 style={{ marginTop: 12 }}>Welcome Back</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: 8, fontSize: '0.95rem' }}>
            Sign in to your Health Intelligence account
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          {error && (
            <div style={{
              padding: '12px 16px', borderRadius: 8, marginBottom: 20,
              background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)',
              color: 'var(--accent-danger)', fontSize: '0.9rem',
            }}>
              {error}
            </div>
          )}

          <div className="input-group">
            <label className="input-label" htmlFor="login-email">Email Address</label>
            <input
              id="login-email"
              type="email"
              className="input-field"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="login-password">Password</label>
            <input
              id="login-password"
              type="password"
              className="input-field"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-full"
            disabled={loading}
            style={{ marginTop: 8 }}
          >
            {loading ? <span className="spinner" /> : 'Sign In'}
          </button>
        </form>

        <p style={{
          textAlign: 'center', marginTop: 24,
          color: 'var(--text-secondary)', fontSize: '0.9rem',
        }}>
          Don&apos;t have an account?{' '}
          <a href="/register" style={{ fontWeight: 600 }}>Create one</a>
        </p>
      </div>
    </div>
  );
}
