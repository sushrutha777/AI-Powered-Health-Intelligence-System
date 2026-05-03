'use client';

import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { useEffect } from 'react';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: '📊' },
  { href: '/dashboard/predict', label: 'Disease Prediction', icon: '🔬' },
  { href: '/dashboard/drugs', label: 'Drug Recommendations', icon: '💊' },
  { href: '/dashboard/chat', label: 'AI Chatbot', icon: '🤖' },
  { href: '/dashboard/history', label: 'History', icon: '📋' },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="spinner spinner-lg" />
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <aside style={{
        width: 'var(--sidebar-width)', flexShrink: 0,
        background: 'var(--bg-secondary)', borderRight: '1px solid var(--border-color)',
        display: 'flex', flexDirection: 'column', position: 'fixed',
        top: 0, left: 0, bottom: 0, zIndex: 50,
      }}>
        {/* Logo */}
        <div style={{
          padding: '24px 20px', display: 'flex', alignItems: 'center', gap: 12,
          borderBottom: '1px solid var(--border-color)',
        }}>
          <span style={{ fontSize: '1.5rem' }}>🏥</span>
          <span style={{ fontSize: '1rem', fontWeight: 700 }} className="text-gradient">
            Health Intelligence
          </span>
        </div>

        {/* Navigation */}
        <nav style={{ flex: 1, padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: 4 }}>
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href;
            return (
              <a
                key={item.href}
                href={item.href}
                style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  padding: '12px 16px', borderRadius: 10,
                  fontSize: '0.9rem', fontWeight: isActive ? 600 : 400,
                  color: isActive ? 'var(--accent-primary)' : 'var(--text-secondary)',
                  background: isActive ? 'rgba(6, 182, 212, 0.1)' : 'transparent',
                  transition: 'all 0.2s ease', textDecoration: 'none',
                }}
              >
                <span style={{ fontSize: '1.1rem' }}>{item.icon}</span>
                {item.label}
              </a>
            );
          })}
        </nav>

        {/* User section */}
        <div style={{
          padding: '16px 16px', borderTop: '1px solid var(--border-color)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ overflow: 'hidden' }}>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {user?.full_name}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {user?.email}
            </div>
          </div>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => { logout(); router.push('/'); }}
            title="Sign out"
            style={{ flexShrink: 0, fontSize: '1rem' }}
          >
            🚪
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main style={{
        flex: 1, marginLeft: 'var(--sidebar-width)',
        padding: '32px 40px', minHeight: '100vh',
        background: 'var(--bg-primary)',
      }}>
        {children}
      </main>
    </div>
  );
}
