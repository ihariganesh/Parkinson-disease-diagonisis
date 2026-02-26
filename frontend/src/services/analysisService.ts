/**
 * analysisService.ts
 * ─────────────────────────────────────────────────────────
 * Isolated, module-scoped analysis functions.
 * Each function validates ONLY its own input and calls its
 * own backend endpoint. They cannot trigger each other's
 * validation errors.
 */

import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// ── Accepted format constants (single source of truth) ──
const DAT_SCAN_FORMATS = ['image/png', 'image/jpeg', 'image/jpg'];
const VOICE_FORMATS = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/m4a',
    'audio/flac', 'audio/ogg', 'audio/x-wav',
    'audio/wave', 'audio/vnd.wave'];
const WAVE_IMAGE_FORMATS = ['image/png', 'image/jpeg', 'image/jpg'];

// ── Helpers ──────────────────────────────────────────────

function getAuthHeader(): Record<string, string> {
    const token = localStorage.getItem('auth_token');
    if (!token) throw new Error('Authentication required. Please login first.');
    return { Authorization: `Bearer ${token}` };
}

function isDatScanFormat(file: File): boolean {
    return (
        DAT_SCAN_FORMATS.includes(file.type) ||
        /\.(png|jpe?g)$/i.test(file.name)
    );
}

function isVoiceFormat(file: File): boolean {
    return (
        VOICE_FORMATS.some(fmt => file.type.startsWith(fmt)) ||
        file.type.startsWith('audio/') ||
        /\.(wav|mp3|m4a|flac|ogg)$/i.test(file.name)
    );
}

function isWaveImageFormat(file: File): boolean {
    return (
        WAVE_IMAGE_FORMATS.includes(file.type) ||
        /\.(png|jpe?g)$/i.test(file.name)
    );
}

// ── 1. DaT Scan Analysis ─────────────────────────────────

export interface DatScanResult {
    success: boolean;
    result?: {
        prediction: string;
        class: number;
        confidence: number;
        probability_healthy: number;
        probability_parkinson: number;
        risk_level: string;
        interpretation: string;
        recommendations: string[];
        timestamp: string;
    };
    error?: string;
}

/**
 * Validate + analyse DaT Scan files ONLY.
 * Never checks voice or wave/image inputs.
 */
// Minimum slices required — a real DaT scan session always has multiple images.
// This also prevents accidentally uploading a single spiral/wave drawing here.
const DAT_SCAN_MIN_FILES = 5;
const DAT_SCAN_MAX_FILES = 20;

export async function analyze_dat_scan(files: File[]): Promise<DatScanResult> {
    // ── Module-specific validation (DaT Scan ONLY) ──
    if (!files || files.length === 0) {
        throw new Error('Upload DaT Scan image to analyze');
    }

    if (files.length < DAT_SCAN_MIN_FILES) {
        throw new Error(
            `DaT Scan requires at least ${DAT_SCAN_MIN_FILES} scan slice images ` +
            `(you uploaded ${files.length}). ` +
            'Real DaT sessions have 10–20 brain scan slices. ' +
            'If you have a spiral or wave drawing, use the Handwriting / Wave section instead.'
        );
    }

    if (files.length > DAT_SCAN_MAX_FILES) {
        throw new Error(`Maximum ${DAT_SCAN_MAX_FILES} DaT Scan images allowed per analysis.`);
    }

    const invalidFiles = files.filter(f => !isDatScanFormat(f));
    if (invalidFiles.length > 0) {
        throw new Error(
            `Invalid file format: ${invalidFiles.map(f => f.name).join(', ')}. ` +
            'DaT Scan accepts PNG, JPG, JPEG only.'
        );
    }

    // ── Build form data ──
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    const response = await axios.post<DatScanResult>(
        `${BASE_URL}/analysis/dat/analyze`,
        formData,
        {
            headers: {
                'Content-Type': 'multipart/form-data',
                ...getAuthHeader(),
            },
        }
    );

    return response.data;
}

// ── 2. Voice Analysis ─────────────────────────────────────

export interface VoiceResult {
    success: boolean;
    message?: string;
    analysis_result?: {
        prediction?: string;
        confidence?: number;
        probability_healthy?: number;
        probability_parkinson?: number;
        risk_level?: string;
        interpretation?: string;
        recommendations?: string[];
        [key: string]: any;
    };
    error?: string;
}

/**
 * Validate + analyse voice file ONLY.
 * Never checks DaT Scan or wave/image inputs.
 */
export async function analyze_voice(file: File | null): Promise<VoiceResult> {
    // ── Module-specific validation ──
    if (!file) {
        throw new Error('Upload voice sample to analyze');
    }

    if (!isVoiceFormat(file)) {
        throw new Error(
            `Invalid file format: "${file.name}". ` +
            'Voice Analysis accepts WAV, MP3, M4A, FLAC, OGG only.'
        );
    }

    const MAX_SIZE_MB = 50;
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
        throw new Error(`Voice file is too large. Maximum size is ${MAX_SIZE_MB} MB.`);
    }

    // ── Build form data ──
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post<VoiceResult>(
        `${BASE_URL}/analysis/speech/analyze`,
        formData,
        {
            headers: {
                'Content-Type': 'multipart/form-data',
                ...getAuthHeader(),
            },
        }
    );

    return response.data;
}

// ── 3. Wave/Image Analysis ────────────────────────────────

export interface WaveImageResult {
    success: boolean;
    prediction?: string;
    confidence?: number;
    analysis_details?: any;
    error?: string;
}

/**
 * Validate + analyse wave/handwriting image ONLY.
 * Never checks DaT Scan or voice inputs.
 */
export async function analyze_wave_image(
    spiralFile: File | null,
    waveFile: File | null
): Promise<WaveImageResult> {
    // ── Module-specific validation ──
    if (!spiralFile && !waveFile) {
        throw new Error('Upload wave image to analyze');
    }

    const filesToCheck = [spiralFile, waveFile].filter(Boolean) as File[];
    const invalidFiles = filesToCheck.filter(f => !isWaveImageFormat(f));
    if (invalidFiles.length > 0) {
        throw new Error(
            `Invalid file format: ${invalidFiles.map(f => f.name).join(', ')}. ` +
            'Wave/Image Analysis accepts PNG, JPG, JPEG only.'
        );
    }

    // ── Build form data ──
    const formData = new FormData();
    if (spiralFile) formData.append('handwriting_spiral', spiralFile);
    if (waveFile) formData.append('handwriting_wave', waveFile);

    // Use the multimodal endpoint with only handwriting data
    const token = localStorage.getItem('auth_token');
    if (!token) throw new Error('Authentication required. Please login first.');

    const response = await axios.post<any>(
        `${BASE_URL}/analysis/multimodal/comprehensive`,
        formData,
        {
            headers: {
                'Content-Type': 'multipart/form-data',
                Authorization: `Bearer ${token}`,
            },
        }
    );

    const data = response.data;
    const handwritingResult = data?.modality_results?.handwriting;

    return {
        success: true,
        prediction: handwritingResult?.prediction ?? data?.fusion_results?.final_diagnosis,
        confidence: handwritingResult?.confidence ?? data?.fusion_results?.confidence,
        analysis_details: data,
    };
}

// ── 4. Full Comprehensive Analysis (all modalities) ───────

export interface ComprehensiveResult {
    timestamp: string;
    patient_id?: string;
    modalities_analyzed: string[];
    modality_results: {
        dat?: { prediction?: string; probability?: number; confidence?: number; error?: string };
        handwriting?: { prediction?: string; probability?: number; confidence?: number; error?: string };
        voice?: { prediction?: string; probability?: number; confidence?: number; error?: string };
    };
    fusion_results: {
        final_diagnosis: string;
        final_probability: number;
        confidence: number;
        confidence_level: string;
        agreement_score: number;
        modalities_used: string[];
        weights_applied: Record<string, number>;
    };
    clinical_interpretation: string;
    recommendations: string[];
    report_id?: string;
    saved_to_database?: boolean;
    save_error?: string;
}

/**
 * Run comprehensive multi‑modal analysis.
 * Requires at least one modality to be supplied.
 * Each modality is optional but independently validated before submission.
 */
export async function analyze_comprehensive(params: {
    datScans?: File[];
    spiralImage?: File | null;
    waveImage?: File | null;
    voiceFile?: File | null;
}): Promise<ComprehensiveResult> {
    const { datScans = [], spiralImage, waveImage, voiceFile } = params;

    // ── Require at least one modality ──
    if (!datScans.length && !spiralImage && !waveImage && !voiceFile) {
        throw new Error(
            'Please upload at least one modality (DaT scan, handwriting image, or voice recording).'
        );
    }

    // ── Validate each supplied modality independently ──
    if (datScans.length) {
        if (datScans.length < DAT_SCAN_MIN_FILES) {
            throw new Error(
                `DaT Scan requires at least ${DAT_SCAN_MIN_FILES} scan slice images. ` +
                `If you are trying to analyze a spiral or wave drawing, please upload it in the Handwriting / Wave section instead.`
            );
        }
        if (datScans.length > DAT_SCAN_MAX_FILES) {
            throw new Error(`Maximum ${DAT_SCAN_MAX_FILES} DaT Scan images allowed.`);
        }
        const bad = datScans.filter(f => !isDatScanFormat(f));
        if (bad.length) throw new Error(`DaT Scan — invalid format: ${bad.map(f => f.name).join(', ')}`);
    }
    if (spiralImage && !isWaveImageFormat(spiralImage)) {
        throw new Error(`Spiral image — invalid format: ${spiralImage.name}`);
    }
    if (waveImage && !isWaveImageFormat(waveImage)) {
        throw new Error(`Wave image — invalid format: ${waveImage.name}`);
    }
    if (voiceFile && !isVoiceFormat(voiceFile)) {
        throw new Error(`Voice file — invalid format: ${voiceFile.name}`);
    }

    const formData = new FormData();
    datScans.forEach(f => formData.append('dat_scans', f));
    if (spiralImage) formData.append('handwriting_spiral', spiralImage);
    if (waveImage) formData.append('handwriting_wave', waveImage);
    if (voiceFile) formData.append('voice_recording', voiceFile);

    const response = await axios.post<ComprehensiveResult>(
        `${BASE_URL}/analysis/multimodal/comprehensive`,
        formData,
        {
            headers: {
                'Content-Type': 'multipart/form-data',
                ...getAuthHeader(),
            },
        }
    );

    return response.data;
}
