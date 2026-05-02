'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import type { HeartDiseaseResponse } from '@/types';

export default function HeartPage() {
  const [form, setForm] = useState({
    age: '', sex: '1', chest_pain_type: 'typical_angina', resting_bp: '',
    cholesterol: '', fasting_bs: '0', resting_ecg: 'normal', max_hr: '',
    exercise_angina: '0', oldpeak: '', st_slope: 'upsloping',
  });
  const [result, setResult] = useState<HeartDiseaseResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const update = (field: string, value: string) => setForm((p) => ({ ...p, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); setError(''); setLoading(true); setResult(null);
    try {
      const payload = {
        ...form, age: Number(form.age), sex: Number(form.sex),
        resting_bp: Number(form.resting_bp), cholesterol: Number(form.cholesterol),
        fasting_bs: Number(form.fasting_bs), max_hr: Number(form.max_hr),
        exercise_angina: Number(form.exercise_angina), oldpeak: Number(form.oldpeak),
      };
      const resp = await api.post<HeartDiseaseResponse>('/api/v1/heart/assess', payload);
      setResult(resp);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Assessment failed');
    } finally { setLoading(false); }
  };

  const riskColors = { low: '#10b981', moderate: '#f59e0b', high: '#ef4444', critical: '#dc2626' };

  return (
    <div className="animate-fade-in">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 8 }}>❤️ Heart Disease Risk Assessment</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 32 }}>Enter clinical parameters for AI-powered cardiac risk scoring.</p>

      <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1fr' : '1fr', gap: 24 }}>
        {/* Input Form */}
        <div className="glass-card" style={{ padding: 28 }}>
          <form onSubmit={handleSubmit}>
            {error && <div style={{ padding: '12px 16px', borderRadius: 8, marginBottom: 20, background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: 'var(--accent-danger)', fontSize: '0.9rem' }}>{error}</div>}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div className="input-group"><label className="input-label">Age</label><input className="input-field" type="number" value={form.age} onChange={(e) => update('age', e.target.value)} required min={1} max={120} placeholder="55" /></div>
              <div className="input-group"><label className="input-label">Sex</label><select className="input-field" value={form.sex} onChange={(e) => update('sex', e.target.value)}><option value="1">Male</option><option value="0">Female</option></select></div>
              <div className="input-group"><label className="input-label">Chest Pain Type</label><select className="input-field" value={form.chest_pain_type} onChange={(e) => update('chest_pain_type', e.target.value)}><option value="typical_angina">Typical Angina</option><option value="atypical_angina">Atypical Angina</option><option value="non_anginal">Non-Anginal</option><option value="asymptomatic">Asymptomatic</option></select></div>
              <div className="input-group"><label className="input-label">Resting BP (mmHg)</label><input className="input-field" type="number" value={form.resting_bp} onChange={(e) => update('resting_bp', e.target.value)} required min={50} max={250} placeholder="130" /></div>
              <div className="input-group"><label className="input-label">Cholesterol (mg/dl)</label><input className="input-field" type="number" value={form.cholesterol} onChange={(e) => update('cholesterol', e.target.value)} required min={50} max={600} placeholder="220" /></div>
              <div className="input-group"><label className="input-label">Fasting Blood Sugar &gt;120</label><select className="input-field" value={form.fasting_bs} onChange={(e) => update('fasting_bs', e.target.value)}><option value="0">No</option><option value="1">Yes</option></select></div>
              <div className="input-group"><label className="input-label">Resting ECG</label><select className="input-field" value={form.resting_ecg} onChange={(e) => update('resting_ecg', e.target.value)}><option value="normal">Normal</option><option value="st_t_abnormality">ST-T Abnormality</option><option value="lv_hypertrophy">LV Hypertrophy</option></select></div>
              <div className="input-group"><label className="input-label">Max Heart Rate</label><input className="input-field" type="number" value={form.max_hr} onChange={(e) => update('max_hr', e.target.value)} required min={50} max={250} placeholder="150" /></div>
              <div className="input-group"><label className="input-label">Exercise Angina</label><select className="input-field" value={form.exercise_angina} onChange={(e) => update('exercise_angina', e.target.value)}><option value="0">No</option><option value="1">Yes</option></select></div>
              <div className="input-group"><label className="input-label">Oldpeak (ST depression)</label><input className="input-field" type="number" step="0.1" value={form.oldpeak} onChange={(e) => update('oldpeak', e.target.value)} required min={-5} max={10} placeholder="1.5" /></div>
              <div className="input-group" style={{ gridColumn: 'span 2' }}><label className="input-label">ST Slope</label><select className="input-field" value={form.st_slope} onChange={(e) => update('st_slope', e.target.value)}><option value="upsloping">Upsloping</option><option value="flat">Flat</option><option value="downsloping">Downsloping</option></select></div>
            </div>

            <button type="submit" className="btn btn-primary btn-full" style={{ marginTop: 8 }} disabled={loading}>
              {loading ? <span className="spinner" /> : 'Assess Risk →'}
            </button>
          </form>
        </div>

        {/* Results */}
        {result && (
          <div className="animate-slide-right">
            <div className="glass-card" style={{ padding: 28, marginBottom: 24, borderColor: `${riskColors[result.risk_level]}44` }}>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 12 }}>Risk Score</p>
              {/* Circular gauge */}
              <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 20 }}>
                <div style={{
                  width: 140, height: 140, borderRadius: '50%', display: 'flex',
                  alignItems: 'center', justifyContent: 'center', flexDirection: 'column',
                  border: `4px solid ${riskColors[result.risk_level]}`,
                  boxShadow: `0 0 20px ${riskColors[result.risk_level]}33`,
                }}>
                  <span style={{ fontSize: '2rem', fontWeight: 800, color: riskColors[result.risk_level] }}>
                    {(result.risk_score * 100).toFixed(0)}%
                  </span>
                  <span className="badge" style={{
                    background: `${riskColors[result.risk_level]}22`,
                    color: riskColors[result.risk_level], textTransform: 'uppercase',
                  }}>
                    {result.risk_level}
                  </span>
                </div>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.7, textAlign: 'center' }}>
                {result.recommendation}
              </p>
            </div>

            {result.contributing_factors.length > 0 && (
              <div className="glass-card" style={{ padding: 28 }}>
                <h4 style={{ marginBottom: 16 }}>Contributing Factors</h4>
                {result.contributing_factors.map((f, idx) => (
                  <div key={idx} style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                      <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{f.factor}</span>
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{(f.impact * 100).toFixed(0)}%</span>
                    </div>
                    <div style={{ background: 'var(--bg-tertiary)', borderRadius: 4, height: 6 }}>
                      <div style={{ height: '100%', borderRadius: 4, background: riskColors[result.risk_level], width: `${f.impact * 100}%`, transition: 'width 0.8s ease' }} />
                    </div>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: 4 }}>{f.detail}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
