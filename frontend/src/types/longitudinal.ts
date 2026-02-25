/**
 * Longitudinal Neuro-Motor Modeling – TypeScript Types
 *
 * Mirrors the backend Pydantic schemas for type-safe frontend consumption.
 */

// ─── Enums ───────────────────────────────────────────────────────────────

export type BiomarkerModality = 'handwriting' | 'voice' | 'dat_scan' | 'composite';

export type ProgressionCategory =
  | 'stable'
  | 'emerging_risk'
  | 'progressive_risk'
  | 'rapid_progression';

export type TrendDirection = 'improving' | 'stable' | 'worsening';

// ─── Core Data ───────────────────────────────────────────────────────────

export interface TimelinePoint {
  id: string;
  modality: BiomarkerModality;
  biomarker: string;
  value: number;
  recorded_at: string; // ISO 8601
}

export interface BiomarkerTrend {
  biomarker: string;
  modality: string;
  slope: number;
  slope_normalised: number | null;
  acceleration: number | null;
  r_squared: number | null;
  p_value: number | null;
  direction: TrendDirection;
  observation_count: number;
  baseline_value: number | null;
  latest_value: number | null;
  window_start: string;
  window_end: string;
}

export interface CrossModalityData {
  agreement_score: number;
  directional_consistency: number;
  pairwise_correlations: Record<string, number> | null;
  modalities_included: string[];
  modality_directions: Record<string, string>;
  modality_slopes: Record<string, number> | null;
  window_start: string;
  window_end: string;
}

export interface RiskAssessment {
  id: string;
  progression_category: ProgressionCategory;
  risk_score: number;
  risk_delta: number | null;
  confidence: number;
  current_probability: number | null;
  avg_slope: number | null;
  avg_acceleration: number | null;
  cross_modality_agreement: number | null;
  months_of_data: number | null;
  clinical_summary: string | null;
  key_findings: string[] | null;
  recommendations: string[] | null;
  trend_details: TrendDetail[] | null;
  computed_at: string;
}

export interface TrendDetail {
  biomarker: string;
  modality: string;
  slope: number;
  slope_normalised: number | null;
  acceleration: number | null;
  direction: TrendDirection;
  r_squared: number | null;
  observations: number;
  baseline: number | null;
  latest: number | null;
}

export interface FullAssessmentData {
  trends: BiomarkerTrend[];
  cross_modality: CrossModalityData | null;
  assessment: RiskAssessment | null;
}

export interface AvailableBiomarker {
  name: string;
  modality: string;
}

// ─── Request types ───────────────────────────────────────────────────────

export interface RecordBiomarkersPayload {
  modality: BiomarkerModality;
  biomarkers: Record<string, number>;
  source_report_id?: string;
  source_analysis_id?: string;
  recorded_at?: string;
  metadata?: Record<string, unknown>;
}

// ─── UI helpers ──────────────────────────────────────────────────────────

export const PROGRESSION_LABELS: Record<ProgressionCategory, string> = {
  stable: 'Stable',
  emerging_risk: 'Emerging Risk',
  progressive_risk: 'Progressive Risk',
  rapid_progression: 'Rapid Progression',
};

export const PROGRESSION_COLORS: Record<ProgressionCategory, string> = {
  stable: '#10b981',           // emerald-500
  emerging_risk: '#f59e0b',    // amber-500
  progressive_risk: '#f97316', // orange-500
  rapid_progression: '#ef4444', // red-500
};

export const DIRECTION_ICONS: Record<TrendDirection, string> = {
  improving: '↗',
  stable: '→',
  worsening: '↘',
};

export const MODALITY_LABELS: Record<string, string> = {
  handwriting: 'Handwriting',
  voice: 'Voice',
  dat_scan: 'DaT Scan',
  composite: 'Composite',
};
