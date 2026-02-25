/**
 * Longitudinal Neuro-Motor Modeling – API Service
 *
 * Wraps all /api/v1/longitudinal endpoints.
 */

import { apiClient } from './api';
import type {
  FullAssessmentData,
  RiskAssessment,
  BiomarkerTrend,
  CrossModalityData,
  TimelinePoint,
  AvailableBiomarker,
  RecordBiomarkersPayload,
} from '../types/longitudinal';

export class LongitudinalService {
  /** Record biomarker readings after an analysis. */
  async recordBiomarkers(payload: RecordBiomarkersPayload) {
    return apiClient.post('/longitudinal/biomarkers', payload);
  }

  /** Run full assessment pipeline and get trends + cross-modality + risk. */
  async runAssessment(windowMonths = 6, currentProbability?: number) {
    const params = new URLSearchParams();
    params.set('window_months', String(windowMonths));
    if (currentProbability !== undefined) {
      params.set('current_probability', String(currentProbability));
    }
    return apiClient.post<FullAssessmentData>(
      `/longitudinal/assess?${params}`,
    );
  }

  /** Latest risk evolution assessment. */
  async getLatestAssessment() {
    return apiClient.get<RiskAssessment | null>('/longitudinal/assessment/latest');
  }

  /** History of risk assessments (for sparkline / history chart). */
  async getAssessmentHistory(limit = 20) {
    return apiClient.get<RiskAssessment[]>(
      `/longitudinal/assessment/history?limit=${limit}`,
    );
  }

  /** Raw biomarker time-series, optionally filtered by biomarker name. */
  async getTimeline(biomarker?: string) {
    const params = biomarker ? `?biomarker=${encodeURIComponent(biomarker)}` : '';
    return apiClient.get<TimelinePoint[]>(`/longitudinal/timeline${params}`);
  }

  /** Get distinct biomarker names available for this patient. */
  async getAvailableBiomarkers() {
    return apiClient.get<AvailableBiomarker[]>('/longitudinal/biomarkers/available');
  }

  /** Latest computed trends. */
  async getLatestTrends() {
    return apiClient.get<BiomarkerTrend[]>('/longitudinal/trends/latest');
  }

  /** Latest cross-modality snapshot. */
  async getLatestCrossModality() {
    return apiClient.get<CrossModalityData | null>('/longitudinal/cross-modality/latest');
  }

  // ─── Doctor endpoints ──────────────────────────────────────────────

  async doctorAssessPatient(patientId: string, windowMonths = 6, currentProbability?: number) {
    const params = new URLSearchParams();
    params.set('window_months', String(windowMonths));
    if (currentProbability !== undefined) {
      params.set('current_probability', String(currentProbability));
    }
    return apiClient.post<FullAssessmentData>(
      `/longitudinal/doctor/assess/${patientId}?${params}`,
    );
  }

  async doctorGetTimeline(patientId: string, biomarker?: string) {
    const params = biomarker ? `?biomarker=${encodeURIComponent(biomarker)}` : '';
    return apiClient.get<TimelinePoint[]>(
      `/longitudinal/doctor/timeline/${patientId}${params}`,
    );
  }

  async doctorGetLatestAssessment(patientId: string) {
    return apiClient.get<RiskAssessment | null>(
      `/longitudinal/doctor/assessment/${patientId}/latest`,
    );
  }
}

export const longitudinalService = new LongitudinalService();
