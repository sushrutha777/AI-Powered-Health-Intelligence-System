'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import type { DrugRecommendationResponse } from '@/types';

export default function DrugsPage() {
  const [condition, setCondition] = useState('');
  const [result, setResult] = useState<DrugRecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!condition.trim()) return;
    setError(''); setLoading(true); setResult(null);
    try {
      const resp = await api.post<DrugRecommendationResponse>('/api/v1/drug/recommend', { condition, top_k: 5 });
      setResult(resp);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally { setLoading(false); }
  };

  return (
    <div className="animate-fade-in">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 8 }}>💊 Drug Recommendations</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 32 }}>Enter a medical condition to get AI-powered drug recommendations.</p>

      <div className="glass-card" style={{ padding: 28, marginBottom: 24 }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: 12 }}>
          <input className="input-field" placeholder="e.g., diabetes, hypertension, depression..." value={condition} onChange={(e) => setCondition(e.target.value)} style={{ flex: 1 }} />
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? <span className="spinner" /> : 'Search'}
          </button>
        </form>
        {error && <p className="input-error" style={{ marginTop: 12 }}>{error}</p>}
      </div>

      {result && result.recommendations.length > 0 && (
        <div className="animate-fade-in">
          <h3 style={{ marginBottom: 16 }}>Results for &ldquo;{result.condition_query}&rdquo; ({result.total_matches} matches)</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {result.recommendations.map((drug, idx) => (
              <div key={idx} className="glass-card" style={{ padding: 24 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                  <div>
                    <h4 style={{ color: 'var(--accent-primary)', marginBottom: 4 }}>{drug.drug_name}</h4>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{drug.condition}</span>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-success)' }}>
                      {(drug.effectiveness_score * 100).toFixed(0)}% match
                    </div>
                    {drug.rating && <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>⭐ {drug.rating}/10</span>}
                  </div>
                </div>
                {drug.review_summary && <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.7, marginBottom: 12 }}>{drug.review_summary}</p>}
                {drug.side_effects.length > 0 && (
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Side effects:</span>
                    {drug.side_effects.map((se, i) => (
                      <span key={i} className="badge badge-moderate" style={{ fontSize: '0.7rem' }}>{se}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
