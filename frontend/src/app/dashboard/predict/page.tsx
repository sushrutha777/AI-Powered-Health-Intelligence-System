'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import type { DiseasePredictionResponse } from '@/types';

const COMMON_SYMPTOMS = [
  'headache', 'fever', 'cough', 'fatigue', 'nausea', 'vomiting',
  'joint_pain', 'muscle_pain', 'breathlessness', 'chest_pain',
  'dizziness', 'skin_rash', 'itching', 'weight_loss', 'sweating',
  'chills', 'back_pain', 'abdominal_pain', 'diarrhoea', 'constipation',
  'high_fever', 'dark_urine', 'yellowing_of_eyes', 'loss_of_appetite',
  'blurred_and_distorted_vision', 'anxiety', 'cold_hands_and_feets',
  'mood_swings', 'restlessness', 'lethargy',
];

export default function PredictPage() {
  const [selected, setSelected] = useState<string[]>([]);
  const [result, setResult] = useState<DiseasePredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const toggleSymptom = (s: string) => {
    setSelected((prev) => prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]);
  };

  const handlePredict = async () => {
    if (selected.length === 0) { setError('Please select at least one symptom'); return; }
    setError(''); setLoading(true); setResult(null);
    try {
      const resp = await api.post<DiseasePredictionResponse>('/api/v1/disease/predict', { symptoms: selected });
      setResult(resp);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 8 }}>
        🔬 Disease Prediction
      </h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 32 }}>
        Select your symptoms and our AI will predict potential diseases.
      </p>

      {/* Symptom Selector */}
      <div className="glass-card" style={{ padding: 28, marginBottom: 24 }}>
        <h4 style={{ marginBottom: 16 }}>Select Symptoms ({selected.length} selected)</h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {COMMON_SYMPTOMS.map((s) => (
            <button
              key={s}
              onClick={() => toggleSymptom(s)}
              style={{
                padding: '8px 16px', borderRadius: 20, border: 'none', cursor: 'pointer',
                fontSize: '0.85rem', fontFamily: 'var(--font-sans)', fontWeight: 500,
                transition: 'all 0.2s ease',
                background: selected.includes(s) ? 'var(--accent-primary)' : 'var(--bg-tertiary)',
                color: selected.includes(s) ? 'white' : 'var(--text-secondary)',
                boxShadow: selected.includes(s) ? '0 0 10px rgba(6, 182, 212, 0.3)' : 'none',
              }}
            >
              {s.replace(/_/g, ' ')}
            </button>
          ))}
        </div>

        {error && <p className="input-error" style={{ marginTop: 16 }}>{error}</p>}

        <button className="btn btn-primary" style={{ marginTop: 24 }} onClick={handlePredict} disabled={loading}>
          {loading ? <span className="spinner" /> : 'Analyze Symptoms →'}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="animate-fade-in">
          {/* Primary Prediction */}
          <div className="glass-card" style={{ padding: 28, marginBottom: 24, borderColor: 'rgba(6, 182, 212, 0.3)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
              <div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 4 }}>Primary Prediction</p>
                <h3 style={{ color: 'var(--accent-primary)' }}>{result.primary_prediction.disease}</h3>
              </div>
              <div style={{
                padding: '8px 16px', borderRadius: 10,
                background: 'rgba(6, 182, 212, 0.1)', fontWeight: 700, fontSize: '1.2rem',
                color: 'var(--accent-primary)',
              }}>
                {(result.primary_prediction.confidence * 100).toFixed(1)}%
              </div>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.7 }}>
              {result.primary_prediction.description}
            </p>
            {/* Confidence Bar */}
            <div style={{ marginTop: 16, background: 'var(--bg-tertiary)', borderRadius: 6, height: 8 }}>
              <div style={{
                height: '100%', borderRadius: 6, background: 'var(--gradient-primary)',
                width: `${result.primary_prediction.confidence * 100}%`, transition: 'width 0.8s ease',
              }} />
            </div>
          </div>

          {/* Differential Diagnoses */}
          {result.differential_diagnoses.length > 0 && (
            <div className="glass-card" style={{ padding: 28 }}>
              <h4 style={{ marginBottom: 16 }}>Differential Diagnoses</h4>
              {result.differential_diagnoses.map((d, idx) => (
                <div key={idx} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '12px 0', borderBottom: idx < result.differential_diagnoses.length - 1 ? '1px solid var(--border-color)' : 'none',
                }}>
                  <div>
                    <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>{d.disease}</span>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: 2 }}>{d.description}</p>
                  </div>
                  <span style={{ color: 'var(--text-secondary)', fontWeight: 600, flexShrink: 0 }}>
                    {(d.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
