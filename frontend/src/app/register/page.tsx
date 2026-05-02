'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';

export default function RegisterPage() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      await register({ email, password, full_name: fullName });
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: 24,
      background: 'radial-gradient(ellipse at 30% 50%, rgba(16, 185, 129, 0.06) 0%, transparent 50%), radial-gradient(ellipse at 70% 30%, rgba(8, 145, 178, 0.06) 0%, transparent 50%)',
    }}>
      <div className="glass-card animate-fade-in" style={{ padding: 48, width: '100%', maxWidth: 440 }}>
        <div style={{ textAlign: 'center', marginBottom: 36 }}>
          <span style={{ fontSize: '2.5rem' }}>🏥</span>
          <h2 style={{ marginTop: 12 }}>Create Account</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: 8, fontSize: '0.95rem' }}>
            Join Health Intelligence today
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
            <label className="input-label" htmlFor="reg-name">Full Name</label>
            <input id="reg-name" type="text" className="input-field" placeholder="John Doe"
              value={fullName} onChange={(e) => setFullName(e.target.value)} required />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="reg-email">Email Address</label>
            <input id="reg-email" type="email" className="input-field" placeholder="you@example.com"
              value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="reg-password">Password</label>
            <input id="reg-password" type="password" className="input-field" placeholder="Min 8 characters"
              value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="reg-confirm">Confirm Password</label>
            <input id="reg-confirm" type="password" className="input-field" placeholder="••••••••"
              value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required minLength={8} />
          </div>

          <button type="submit" className="btn btn-primary btn-full" disabled={loading} style={{ marginTop: 8 }}>
            {loading ? <span className="spinner" /> : 'Create Account'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: 24, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Already have an account?{' '}
          <a href="/login" style={{ fontWeight: 600 }}>Sign in</a>
        </p>
      </div>
    </div>
  );
}
