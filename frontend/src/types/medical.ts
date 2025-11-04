export interface MedicalData {
  id: string;
  patientId: string;
  type: 'handwriting' | 'voice' | 'ecg' | 'mri' | 'doctor_notes';
  fileName: string;
  fileUrl: string;
  fileSize: number;
  uploadedAt: string;
  processedAt?: string;
  analysisResult?: AnalysisResult;
  metadata?: {
    duration?: number; // for voice recordings
    resolution?: string; // for images
    deviceInfo?: string;
    notes?: string;
  };
}

export interface AnalysisResult {
  id: string;
  medicalDataId: string;
  confidence: number;
  prediction: 'healthy' | 'early_stage' | 'moderate_stage' | 'advanced_stage';
  stage?: number; // 0-4 scale
  features?: {
    [key: string]: number;
  };
  modelVersion: string;
  processedAt: string;
}

export interface DiagnosisReport {
  id: string;
  patientId: string;
  doctorId?: string;
  finalDiagnosis: 'healthy' | 'early_stage' | 'moderate_stage' | 'advanced_stage';
  confidence: number;
  stage: number;
  multimodalAnalysis: {
    handwriting?: AnalysisResult;
    voice?: AnalysisResult;
    ecg?: AnalysisResult;
    mri?: AnalysisResult;
    doctorNotes?: AnalysisResult;
  };
  fusionScore: number;
  doctorNotes?: string;
  doctorVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface LifestyleSuggestion {
  id: string;
  reportId: string;
  category: 'exercise' | 'diet' | 'therapy' | 'medication' | 'lifestyle';
  title: string;
  description: string;
  recommendations: string[];
  priority: 'low' | 'medium' | 'high';
  stage: number;
  generatedAt: string;
}

export interface UploadProgress {
  fileName: string;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}