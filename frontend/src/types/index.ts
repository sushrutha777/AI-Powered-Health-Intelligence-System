/**
 * Shared TypeScript types for the Health Intelligence System frontend.
 */

// ── Auth ──────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
}

// ── Disease Prediction ────────────────────────────────────────────

export interface DiseaseSymptomInput {
  symptoms: string[];
}

export interface DiseasePredictionResult {
  disease: string;
  confidence: number;
  description: string;
  precautions: string[];
}

export interface DiseasePredictionResponse {
  prediction_id: string;
  primary_prediction: DiseasePredictionResult;
  differential_diagnoses: DiseasePredictionResult[];
  model_version: string | null;
  timestamp: string;
}

// ── Heart Disease ─────────────────────────────────────────────────

export interface HeartDiseaseInput {
  age: number;
  sex: number;
  chest_pain_type: string;
  resting_bp: number;
  cholesterol: number;
  fasting_bs: number;
  resting_ecg: string;
  max_hr: number;
  exercise_angina: number;
  oldpeak: number;
  st_slope: string;
}

export interface ContributingFactor {
  factor: string;
  impact: number;
  detail: string;
}

export interface HeartDiseaseResponse {
  prediction_id: string;
  risk_score: number;
  risk_level: 'low' | 'moderate' | 'high' | 'critical';
  contributing_factors: ContributingFactor[];
  recommendation: string;
  model_version: string | null;
  timestamp: string;
}

// ── Drug Recommendation ───────────────────────────────────────────

export interface DrugRecommendationInput {
  condition: string;
  symptoms?: string[];
  top_k?: number;
}

export interface DrugRecommendation {
  drug_name: string;
  condition: string;
  effectiveness_score: number;
  rating: number | null;
  review_summary: string | null;
  side_effects: string[];
}

export interface DrugRecommendationResponse {
  condition_query: string;
  recommendations: DrugRecommendation[];
  total_matches: number;
}

// ── Chat ──────────────────────────────────────────────────────────

export interface SourceCitation {
  title: string;
  content_snippet: string;
  relevance_score: number;
}

export interface ChatMessageInput {
  message: string;
  session_id?: string;
}

export interface ChatMessageResponse {
  session_id: string;
  message_id: string;
  content: string;
  sources: SourceCitation[];
  timestamp: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceCitation[];
  created_at: string;
}

export interface ChatSession {
  id: string;
  title: string;
  message_count: number;
  created_at: string;
}

export interface PredictionHistoryItem {
  id: string;
  prediction_type: string;
  input_data: Record<string, unknown>;
  result: Record<string, unknown>;
  confidence: number | null;
  created_at: string;
}
