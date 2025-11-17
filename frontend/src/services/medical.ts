import { apiClient } from './api';
import type { 
  MedicalData, 
  AnalysisResult, 
  DiagnosisReport, 
  LifestyleSuggestion, 
  PaginatedResponse 
} from '../types';

export class MedicalService {
  async uploadMedicalData(file: File, type: string, metadata?: any, onProgress?: (progress: number) => void) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }

    const response = await apiClient.uploadFile<MedicalData>('/medical/upload', file, onProgress);
    return response;
  }

  async getMedicalData(patientId?: string, type?: string, page = 1, limit = 10) {
    const params = new URLSearchParams();
    if (patientId) params.append('patientId', patientId);
    if (type) params.append('type', type);
    params.append('page', page.toString());
    params.append('limit', limit.toString());

    const response = await apiClient.get<PaginatedResponse<MedicalData>>(`/medical/data?${params}`);
    return response;
  }

  async getMedicalDataById(id: string) {
    const response = await apiClient.get<MedicalData>(`/medical/data/${id}`);
    return response;
  }

  async deleteMedicalData(id: string) {
    const response = await apiClient.delete(`/medical/data/${id}`);
    return response;
  }

  async getAnalysisResult(medicalDataId: string) {
    const response = await apiClient.get<AnalysisResult>(`/medical/analysis/${medicalDataId}`);
    return response;
  }

  async triggerAnalysis(medicalDataId: string) {
    const response = await apiClient.post<AnalysisResult>(`/medical/analyze/${medicalDataId}`);
    return response;
  }

  async getDiagnosisReports(patientId?: string, page = 1, limit = 10) {
    const params = new URLSearchParams();
    if (patientId) params.append('patientId', patientId);
    params.append('page', page.toString());
    params.append('limit', limit.toString());

    const response = await apiClient.get<PaginatedResponse<DiagnosisReport>>(`/medical/reports?${params}`);
    return response;
  }

  async getDiagnosisReportById(id: string) {
    const response = await apiClient.get<DiagnosisReport>(`/medical/reports/${id}`);
    return response;
  }

  async generateDiagnosisReport(patientId: string, medicalDataIds: string[]) {
    const response = await apiClient.post<DiagnosisReport>('/medical/reports/generate', {
      patientId,
      medicalDataIds,
    });
    return response;
  }

  async updateDiagnosisReport(id: string, updates: Partial<DiagnosisReport>) {
    const response = await apiClient.put<DiagnosisReport>(`/medical/reports/${id}`, updates);
    return response;
  }

  async deleteDiagnosisReport(id: string) {
    const response = await apiClient.delete(`/medical/reports/${id}`);
    return response;
  }

  async bulkDeleteDiagnosisReports(reportIds: string[]) {
    const response = await apiClient.post('/medical/reports/bulk-delete', reportIds);
    return response;
  }

  async verifyDiagnosisReport(id: string, doctorNotes?: string) {
    const response = await apiClient.post<DiagnosisReport>(`/medical/reports/${id}/verify`, {
      doctorNotes,
    });
    return response;
  }

  async getLifestyleSuggestions(reportId: string) {
    const response = await apiClient.get<LifestyleSuggestion[]>(`/medical/lifestyle/${reportId}`);
    return response;
  }

  async generateLifestyleSuggestions(reportId: string) {
    const response = await apiClient.post<LifestyleSuggestion[]>(`/medical/lifestyle/generate/${reportId}`);
    return response;
  }

  async getPatientHistory(patientId: string) {
    const response = await apiClient.get<{
      medicalData: MedicalData[];
      reports: DiagnosisReport[];
      suggestions: LifestyleSuggestion[];
    }>(`/medical/patient/${patientId}/history`);
    return response;
  }
}

export const medicalService = new MedicalService();