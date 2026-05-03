'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { PredictionHistoryItem } from '@/types';

export default function HistoryPage() {
  const [tab, setTab] = useState<'disease'>('disease');
  const [predictions, setPredictions] = useState<PredictionHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      try {
        const endpoint = '/api/v1/disease/history';
        const resp = await api.get<{ predictions: PredictionHistoryItem[] }>(endpoint);
        setPredictions(resp.predictions);
      } catch {
        setPredictions([]);
      } finally { setLoading(false); }
    };
    fetchHistory();
  }, [tab]);

  return (
    <div className="animate-fade-in">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 8 }}>📋 Prediction History</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 32 }}>Review your past predictions and assessments.</p>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 24, background: 'var(--bg-tertiary)', borderRadius: 10, padding: 4, width: 'fit-content' }}>
        <button onClick={() => setTab('disease')} style={{
          padding: '10px 24px', borderRadius: 8, border: 'none', cursor: 'pointer',
          fontFamily: 'var(--font-sans)', fontWeight: 600, fontSize: '0.9rem',
          background: 'var(--accent-primary)',
          color: 'white', transition: 'all 0.2s ease',
        }}>
          🔬 Disease
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}><div className="spinner spinner-lg" /></div>
      ) : predictions.length === 0 ? (
        <div className="glass-card" style={{ padding: 60, textAlign: 'center' }}>
          <span style={{ fontSize: '3rem' }}>📭</span>
          <p style={{ color: 'var(--text-muted)', marginTop: 16 }}>No predictions yet. Start by making your first {tab} prediction!</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {predictions.map((p) => (
            <div key={p.id} className="glass-card" style={{ padding: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>
                    {(p.result as { primary?: { disease?: string } })?.primary?.disease || 'Unknown'}
                  </span>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: 4 }}>
                    {new Date(p.created_at).toLocaleDateString()} at {new Date(p.created_at).toLocaleTimeString()}
                  </p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  {p.confidence !== null && (
                    <span style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>
                      {(p.confidence * 100).toFixed(1)}%
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
