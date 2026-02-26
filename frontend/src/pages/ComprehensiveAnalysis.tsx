/**
 * ComprehensiveAnalysis.tsx
 * ─────────────────────────────────────────────────────────
 * Refactored — each modality (DaT Scan, Voice, Wave/Image)
 * has its own independent:
 *   • State
 *   • Validation (module-scoped, never cross-checks siblings)
 *   • Analyse button   → routed to its dedicated function
 *   • Error display
 *
 * The combined "Analyse All Modalities" button remains for
 * the comprehensive multi-modal fusion path, but uses the
 * same isolated per-modality validation before submission.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CloudArrowUpIcon,
  BeakerIcon,
  PencilSquareIcon,
  MicrophoneIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  DocumentTextIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';

import {
  analyze_dat_scan,
  analyze_voice,
  analyze_wave_image,
  analyze_comprehensive,
  type DatScanResult,
  type VoiceResult,
  type WaveImageResult,
  type ComprehensiveResult,
} from '../services/analysisService';

// ─── Helpers ─────────────────────────────────────────────

function ModuleError({ message }: { message: string }) {
  if (!message) return null;
  return (
    <div className="mt-3 flex items-start gap-2 bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg text-sm">
      <XCircleIcon className="h-4 w-4 mt-0.5 flex-shrink-0" />
      <span>{message}</span>
    </div>
  );
}

function SpinnerButton({
  loading,
  disabled,
  onClick,
  label,
  loadingLabel,
  color = 'indigo',
}: {
  loading: boolean;
  disabled: boolean;
  onClick: () => void;
  label: string;
  loadingLabel?: string;
  color?: 'indigo' | 'pink' | 'purple';
}) {
  const colors: Record<string, string> = {
    indigo: 'bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-500',
    pink: 'bg-pink-600   hover:bg-pink-700   focus:ring-pink-500',
    purple: 'bg-purple-600 hover:bg-purple-700 focus:ring-purple-500',
  };
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`mt-4 w-full py-2.5 px-4 rounded-lg font-semibold text-white text-sm transition flex items-center justify-center gap-2
        ${disabled || loading ? 'bg-gray-300 cursor-not-allowed' : colors[color]}
        focus:outline-none focus:ring-2 focus:ring-offset-2`}
    >
      {loading ? (
        <>
          <ArrowPathIcon className="h-4 w-4 animate-spin" />
          {loadingLabel ?? 'Analyzing…'}
        </>
      ) : (
        label
      )}
    </button>
  );
}

// ─── Component ───────────────────────────────────────────

export default function ComprehensiveAnalysis() {
  const navigate = useNavigate();

  // ── DaT Scan state ──────────────────────────────────────
  const [datFiles, setDatFiles] = useState<File[]>([]);
  const [datPreviews, setDatPreviews] = useState<string[]>([]);
  const [datLoading, setDatLoading] = useState(false);
  const [datError, setDatError] = useState('');
  const [datResult, setDatResult] = useState<DatScanResult | null>(null);

  // ── Voice state ─────────────────────────────────────────
  const [voiceFile, setVoiceFile] = useState<File | null>(null);
  const [voiceLoading, setVoiceLoading] = useState(false);
  const [voiceError, setVoiceError] = useState('');
  const [voiceResult, setVoiceResult] = useState<VoiceResult | null>(null);

  // ── Wave/Image state ────────────────────────────────────
  const [spiralFile, setSpiralFile] = useState<File | null>(null);
  const [waveFile, setWaveFile] = useState<File | null>(null);
  const [spiralPreview, setSpiralPreview] = useState('');
  const [wavePreview, setWavePreview] = useState('');
  const [waveLoading, setWaveLoading] = useState(false);
  const [waveError, setWaveError] = useState('');
  const [waveResult, setWaveResult] = useState<WaveImageResult | null>(null);

  // ── Comprehensive (fusion) state ────────────────────────
  const [compLoading, setCompLoading] = useState(false);
  const [compError, setCompError] = useState('');
  const [compResult, setCompResult] = useState<ComprehensiveResult | null>(null);

  // ── File change handlers ─────────────────────────────────

  const handleDatChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? []);
    setDatFiles(files);
    setDatPreviews(files.map(f => URL.createObjectURL(f)));
    setDatError('');
    setDatResult(null);
  };

  const handleVoiceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setVoiceFile(file);
    setVoiceError('');
    setVoiceResult(null);
  };

  const handleSpiralChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setSpiralFile(file);
    if (file) setSpiralPreview(URL.createObjectURL(file));
    setWaveError('');
    setWaveResult(null);
  };

  const handleWaveChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setWaveFile(file);
    if (file) setWavePreview(URL.createObjectURL(file));
    setWaveError('');
    setWaveResult(null);
  };

  // ── Isolated analyse functions ───────────────────────────

  /** DaT Scan → analyze_dat_scan() — never checks voice or wave */
  const handleAnalyzeDat = async () => {
    setDatError('');
    setDatLoading(true);
    try {
      const res = await analyze_dat_scan(datFiles);
      setDatResult(res);
    } catch (err: any) {
      setDatError(err.response?.data?.detail ?? err.message ?? 'DaT Scan analysis failed.');
    } finally {
      setDatLoading(false);
    }
  };

  /** Voice → analyze_voice() — never checks DaT or wave/image inputs */
  const handleAnalyzeVoice = async () => {
    setVoiceError('');
    setVoiceLoading(true);
    try {
      const res = await analyze_voice(voiceFile);
      setVoiceResult(res);
    } catch (err: any) {
      setVoiceError(err.response?.data?.detail ?? err.message ?? 'Voice analysis failed.');
    } finally {
      setVoiceLoading(false);
    }
  };

  /** Wave/Image → analyze_wave_image() — never checks DaT or voice inputs */
  const handleAnalyzeWaveImage = async () => {
    setWaveError('');
    setWaveLoading(true);
    try {
      const res = await analyze_wave_image(spiralFile, waveFile);
      setWaveResult(res);
    } catch (err: any) {
      setWaveError(err.response?.data?.detail ?? err.message ?? 'Wave/Image analysis failed.');
    } finally {
      setWaveLoading(false);
    }
  };

  /** Full fusion — uses analyze_comprehensive() with per-modality validation */
  const handleAnalyzeAll = async () => {
    setCompError('');
    setCompLoading(true);
    try {
      const res = await analyze_comprehensive({
        datScans: datFiles,
        spiralImage: spiralFile,
        waveImage: waveFile,
        voiceFile,
      });
      setCompResult(res);
    } catch (err: any) {
      setCompError(err.response?.data?.detail ?? err.message ?? 'Comprehensive analysis failed.');
    } finally {
      setCompLoading(false);
    }
  };

  // ── Reset ────────────────────────────────────────────────

  const handleReset = () => {
    setDatFiles([]); setDatPreviews([]); setDatError(''); setDatResult(null);
    setVoiceFile(null); setVoiceError(''); setVoiceResult(null);
    setSpiralFile(null); setWaveFile(null);
    setSpiralPreview(''); setWavePreview('');
    setWaveError(''); setWaveResult(null);
    setCompError(''); setCompResult(null);
  };

  // ── Utilities ────────────────────────────────────────────

  const diagnosisColor = (d: string) =>
    d.toLowerCase().includes('parkinson')
      ? 'text-red-600 bg-red-50 border-red-200'
      : 'text-green-600 bg-green-50 border-green-200';

  const anyUploaded = datFiles.length > 0 || !!voiceFile || !!spiralFile || !!waveFile;

  // ─────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">

        {/* ── Header ── */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Comprehensive Parkinson's Analysis
          </h1>
          <p className="text-lg text-gray-600">
            Multi-modal AI-powered diagnosis — analyse each modality independently or run all together.
          </p>
          <div className="mt-4 inline-flex items-center px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg">
            <ExclamationTriangleIcon className="h-5 w-5 text-blue-600 mr-2" />
            <span className="text-sm text-blue-800">
              Clinical research tool • Not for primary diagnosis • Requires physician confirmation
            </span>
          </div>
        </div>

        {/* ── Three Module Cards ── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">

          {/* ─ DaT Scan Card ─ */}
          <div className="bg-white rounded-xl shadow-md p-6 border-2 border-indigo-100 flex flex-col">
            <div className="flex items-center mb-3">
              <BeakerIcon className="h-6 w-6 text-indigo-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">DaT Scan</h3>
              <span className="ml-auto text-xs bg-indigo-100 text-indigo-800 px-2 py-1 rounded">
                50% weight
              </span>
            </div>

            {/* ── Requirement notice ── */}
            <div className="mb-3 flex items-start gap-2 bg-indigo-50 border border-indigo-200 rounded-lg px-3 py-2 text-xs text-indigo-800">
              <ExclamationTriangleIcon className="h-4 w-4 mt-0.5 flex-shrink-0 text-indigo-500" />
              <span>
                <strong>Requires 5–20 brain scan slices.</strong> Each slice is a separate image file from a DaT scan session.
                <br />
                <span className="text-indigo-600 font-medium">Spiral / wave drawings belong in the Handwriting / Wave section.</span>
              </span>
            </div>

            <label className="block">
              <div
                className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition ${datFiles.length > 0 && datFiles.length < 5
                  ? 'border-orange-400 bg-orange-50'
                  : datFiles.length >= 5
                    ? 'border-indigo-400 bg-indigo-50'
                    : 'border-gray-300 hover:border-indigo-400'
                  }`}
              >
                <CloudArrowUpIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <span className="text-sm text-gray-600">
                  {datFiles.length === 0
                    ? 'Click to upload DaT Scan slices'
                    : `${datFiles.length} slice${datFiles.length > 1 ? 's' : ''} selected`}
                </span>
                <p className="text-xs text-gray-400 mt-1">PNG, JPG, JPEG — min 5, max 20 files</p>
                <input
                  id="dat-scan-input"
                  type="file"
                  multiple
                  accept=".png,.jpg,.jpeg"
                  onChange={handleDatChange}
                  className="hidden"
                />
              </div>
            </label>

            {/* File count warning */}
            {datFiles.length > 0 && datFiles.length < 5 && (
              <div className="mt-2 flex items-center gap-2 bg-orange-50 border border-orange-300 text-orange-800 px-3 py-2 rounded-lg text-xs">
                <ExclamationTriangleIcon className="h-4 w-4 flex-shrink-0" />
                <span>
                  Only <strong>{datFiles.length}</strong> file{datFiles.length > 1 ? 's' : ''} selected. DaT Scan needs at least <strong>5 slices</strong>.
                  If this is a spiral or wave image, upload it in the <strong>Handwriting / Wave</strong> section on the right.
                </span>
              </div>
            )}

            {/* File count OK badge */}
            {datFiles.length >= 5 && (
              <div className="mt-2 flex items-center gap-2 bg-green-50 border border-green-200 text-green-800 px-3 py-2 rounded-lg text-xs">
                <CheckCircleIcon className="h-4 w-4 flex-shrink-0" />
                <span>{datFiles.length} slices ready — good to analyze.</span>
              </div>
            )}

            {datPreviews.length > 0 && (
              <div className="mt-3 grid grid-cols-4 gap-1">
                {datPreviews.slice(0, 8).map((src, i) => (
                  <img key={i} src={src} alt={`scan-${i}`}
                    className={`w-full h-14 object-cover rounded border ${datFiles.length < 5 ? 'border-orange-200 opacity-70' : 'border-indigo-100'
                      }`} />
                ))}
                {datPreviews.length > 8 && (
                  <div className="col-span-4 text-xs text-gray-400 text-center mt-1">
                    +{datPreviews.length - 8} more
                  </div>
                )}
              </div>
            )}

            <ModuleError message={datError} />

            {/* DaT Scan → analyze_dat_scan() — disabled if fewer than 5 files */}
            <SpinnerButton
              loading={datLoading}
              disabled={datFiles.length < 5}
              onClick={handleAnalyzeDat}
              label={datFiles.length === 0 ? 'Upload at least 5 scan slices' : datFiles.length < 5 ? `Need ${5 - datFiles.length} more slice${5 - datFiles.length > 1 ? 's' : ''}` : 'Analyze DaT Scan'}
              loadingLabel="Analyzing…"
              color="indigo"
            />

            {/* DaT inline result */}
            {datResult?.result && (
              <div className="mt-3 p-3 bg-indigo-50 rounded-lg text-sm border border-indigo-200">
                <p className="font-semibold text-indigo-900">{datResult.result.prediction}</p>
                <p className="text-gray-600">Confidence: {(datResult.result.confidence * 100).toFixed(1)}%</p>
                <p className="text-gray-600">Risk: {datResult.result.risk_level}</p>
              </div>
            )}
          </div>

          {/* ─ Wave / Image Card ─ */}
          <div className="bg-white rounded-xl shadow-md p-6 border-2 border-purple-100 flex flex-col">
            <div className="flex items-center mb-3">
              <PencilSquareIcon className="h-6 w-6 text-purple-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Handwriting / Wave</h3>
              <span className="ml-auto text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                25% weight
              </span>
            </div>
            <p className="text-sm text-gray-500 mb-3">
              Upload spiral and/or wave drawing (PNG / JPG / JPEG only).
            </p>

            {/* Spiral upload */}
            <label className="block mb-3">
              <span className="text-xs text-gray-500 mb-1 block">Spiral Drawing</span>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-3 text-center cursor-pointer hover:border-purple-400 transition">
                <CloudArrowUpIcon className="h-5 w-5 text-gray-400 mx-auto mb-1" />
                <span className="text-xs text-gray-600">
                  {spiralFile ? spiralFile.name : 'Upload spiral image'}
                </span>
                <input
                  id="spiral-input"
                  type="file"
                  accept=".png,.jpg,.jpeg"
                  onChange={handleSpiralChange}
                  className="hidden"
                />
              </div>
            </label>
            {spiralPreview && (
              <img src={spiralPreview} alt="Spiral preview"
                className="w-full h-24 object-cover rounded mb-2" />
            )}

            {/* Wave upload */}
            <label className="block">
              <span className="text-xs text-gray-500 mb-1 block">Wave Drawing</span>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-3 text-center cursor-pointer hover:border-purple-400 transition">
                <CloudArrowUpIcon className="h-5 w-5 text-gray-400 mx-auto mb-1" />
                <span className="text-xs text-gray-600">
                  {waveFile ? waveFile.name : 'Upload wave image'}
                </span>
                <input
                  id="wave-image-input"
                  type="file"
                  accept=".png,.jpg,.jpeg"
                  onChange={handleWaveChange}
                  className="hidden"
                />
              </div>
            </label>
            {wavePreview && (
              <img src={wavePreview} alt="Wave preview"
                className="w-full h-24 object-cover rounded mt-2" />
            )}

            <ModuleError message={waveError} />

            {/* Wave/Image → analyze_wave_image() */}
            <SpinnerButton
              loading={waveLoading}
              disabled={!spiralFile && !waveFile}
              onClick={handleAnalyzeWaveImage}
              label="Analyze Wave / Image"
              color="purple"
            />

            {/* Wave inline result */}
            {waveResult?.success && (
              <div className="mt-3 p-3 bg-purple-50 rounded-lg text-sm border border-purple-200">
                <p className="font-semibold text-purple-900">
                  {waveResult.prediction ?? 'Result received'}
                </p>
                {waveResult.confidence !== undefined && (
                  <p className="text-gray-600">
                    Confidence: {(waveResult.confidence * 100).toFixed(1)}%
                  </p>
                )}
              </div>
            )}
          </div>

          {/* ─ Voice Card ─ */}
          <div className="bg-white rounded-xl shadow-md p-6 border-2 border-pink-100 flex flex-col">
            <div className="flex items-center mb-3">
              <MicrophoneIcon className="h-6 w-6 text-pink-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Voice Analysis</h3>
              <span className="ml-auto text-xs bg-pink-100 text-pink-800 px-2 py-1 rounded">
                25% weight
              </span>
            </div>
            <p className="text-sm text-gray-500 mb-3">
              Upload a voice recording (WAV / MP3 / M4A / FLAC / OGG).
            </p>

            <label className="block flex-1">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center cursor-pointer hover:border-pink-400 transition">
                <CloudArrowUpIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <span className="text-sm text-gray-600">
                  {voiceFile ? voiceFile.name : 'Click to upload voice sample'}
                </span>
                <p className="text-xs text-gray-400 mt-1">WAV, MP3, M4A, FLAC, OGG</p>
                <input
                  id="voice-input"
                  type="file"
                  accept="audio/*"
                  onChange={handleVoiceChange}
                  className="hidden"
                />
              </div>
            </label>

            {voiceFile && (
              <div className="mt-2 flex items-center gap-2 text-sm text-pink-700 bg-pink-50 px-3 py-2 rounded">
                <CheckCircleIcon className="h-4 w-4" />
                <span className="truncate">{voiceFile.name}</span>
              </div>
            )}

            <ModuleError message={voiceError} />

            {/* Voice → analyze_voice() */}
            <SpinnerButton
              loading={voiceLoading}
              disabled={!voiceFile}
              onClick={handleAnalyzeVoice}
              label="Analyze Voice"
              color="pink"
            />

            {/* Voice inline result */}
            {voiceResult?.success && voiceResult.analysis_result && (
              <div className="mt-3 p-3 bg-pink-50 rounded-lg text-sm border border-pink-200">
                <p className="font-semibold text-pink-900">
                  {voiceResult.analysis_result.prediction ?? 'Analysis complete'}
                </p>
                {voiceResult.analysis_result.confidence !== undefined && (
                  <p className="text-gray-600">
                    Confidence: {(voiceResult.analysis_result.confidence * 100).toFixed(1)}%
                  </p>
                )}
                {voiceResult.analysis_result.risk_level && (
                  <p className="text-gray-600">
                    Risk: {voiceResult.analysis_result.risk_level}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* ── Combined Action Bar ── */}
        <div className="flex flex-wrap items-center justify-center gap-4 mb-8">
          <button
            onClick={handleAnalyzeAll}
            disabled={compLoading || !anyUploaded || (datFiles.length > 0 && datFiles.length < 5)}
            className="px-8 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700
              disabled:bg-gray-300 disabled:cursor-not-allowed transition flex items-center gap-2"
          >
            {compLoading ? (
              <>
                <ArrowPathIcon className="h-5 w-5 animate-spin" />
                Analyzing All…
              </>
            ) : (
              'Analyze All Modalities (Fusion)'
            )}
          </button>
          <button
            onClick={handleReset}
            className="px-8 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition"
          >
            Reset All
          </button>
        </div>

        {/* Comprehensive error */}
        {compError && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-start gap-2">
            <XCircleIcon className="h-5 w-5 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold">Error:</p>
              <p>{compError}</p>
            </div>
          </div>
        )}

        {/* ── Comprehensive Results ── */}
        {compResult && (
          <div className="space-y-6">

            {/* Overall Diagnosis */}
            <div className={`bg-white rounded-lg shadow-lg p-8 border-2 ${diagnosisColor(compResult.fusion_results.final_diagnosis)}`}>
              <h2 className="text-2xl font-bold mb-4">Overall Diagnosis (Fusion)</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Diagnosis</p>
                  <p className="text-3xl font-bold">{compResult.fusion_results.final_diagnosis}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Modality Agreement</p>
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-4 mr-3">
                      <div
                        className="bg-green-600 h-4 rounded-full"
                        style={{ width: `${compResult.fusion_results.agreement_score * 100}%` }}
                      />
                    </div>
                    <span className="font-bold">
                      {(compResult.fusion_results.agreement_score * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Per-modality Results */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {compResult.modality_results.dat && (
                <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-indigo-500">
                  <h3 className="text-lg font-semibold mb-3 flex items-center">
                    <BeakerIcon className="h-5 w-5 mr-2 text-indigo-600" /> DaT Scan
                  </h3>
                  {compResult.modality_results.dat.error ? (
                    <p className="text-red-600 text-sm">{compResult.modality_results.dat.error}</p>
                  ) : (
                    <>
                      <p className="text-2xl font-bold mb-1">{compResult.modality_results.dat.prediction}</p>
                      <p className="text-sm text-gray-600">
                        Probability: {((compResult.modality_results.dat.probability ?? 0) * 100).toFixed(1)}%
                      </p>
                      <p className="text-sm text-gray-600">
                        Confidence: {((compResult.modality_results.dat.confidence ?? 0) * 100).toFixed(1)}%
                      </p>
                    </>
                  )}
                </div>
              )}
              {compResult.modality_results.handwriting && (
                <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
                  <h3 className="text-lg font-semibold mb-3 flex items-center">
                    <PencilSquareIcon className="h-5 w-5 mr-2 text-purple-600" /> Handwriting
                  </h3>
                  {compResult.modality_results.handwriting.error ? (
                    <p className="text-red-600 text-sm">{compResult.modality_results.handwriting.error}</p>
                  ) : (
                    <>
                      <p className="text-2xl font-bold mb-1">{compResult.modality_results.handwriting.prediction}</p>
                      <p className="text-sm text-gray-600">
                        Probability: {((compResult.modality_results.handwriting.probability ?? 0) * 100).toFixed(1)}%
                      </p>
                      <p className="text-sm text-gray-600">
                        Confidence: {((compResult.modality_results.handwriting.confidence ?? 0) * 100).toFixed(1)}%
                      </p>
                    </>
                  )}
                </div>
              )}
              {compResult.modality_results.voice && (
                <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-pink-500">
                  <h3 className="text-lg font-semibold mb-3 flex items-center">
                    <MicrophoneIcon className="h-5 w-5 mr-2 text-pink-600" /> Voice
                  </h3>
                  {compResult.modality_results.voice.error ? (
                    <p className="text-red-600 text-sm">{compResult.modality_results.voice.error}</p>
                  ) : (
                    <>
                      <p className="text-2xl font-bold mb-1">{compResult.modality_results.voice.prediction}</p>
                      <p className="text-sm text-gray-600">
                        Probability: {((compResult.modality_results.voice.probability ?? 0) * 100).toFixed(1)}%
                      </p>
                      <p className="text-sm text-gray-600">
                        Confidence: {((compResult.modality_results.voice.confidence ?? 0) * 100).toFixed(1)}%
                      </p>
                    </>
                  )}
                </div>
              )}
            </div>

            {/* Clinical Interpretation */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">Clinical Interpretation</h3>
              <p className="text-gray-700 leading-relaxed">{compResult.clinical_interpretation}</p>
            </div>

            {/* Recommendations */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">Recommendations</h3>
              <ul className="space-y-2">
                {compResult.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start">
                    <CheckCircleIcon className="h-5 w-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Saved badge */}
            {compResult.saved_to_database && compResult.report_id && (
              <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg shadow-lg p-8 text-center">
                <DocumentTextIcon className="h-16 w-16 text-white mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-white mb-3">Analysis Complete & Saved!</h3>
                <p className="text-indigo-100 mb-6">
                  Your comprehensive diagnosis report has been saved to your medical records.
                </p>
                <button
                  onClick={() => navigate('/reports')}
                  className="bg-white text-indigo-600 hover:bg-gray-100 font-bold py-3 px-8 rounded-lg transition inline-flex items-center text-lg shadow-lg"
                >
                  <DocumentTextIcon className="h-6 w-6 mr-2" />
                  View Full Report
                </button>
              </div>
            )}

            {/* Not-saved notice */}
            {compResult.saved_to_database === false && (
              <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-6">
                <div className="flex items-start">
                  <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600 mr-3 mt-0.5 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-yellow-900 mb-1">Report Not Saved</h3>
                    <p className="text-sm text-yellow-800">
                      The analysis completed but the report could not be saved.
                      {compResult.save_error && ` Error: ${compResult.save_error}`}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Disclaimer */}
            <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-yellow-900 mb-3 flex items-center">
                <ExclamationTriangleIcon className="h-6 w-6 mr-2" />
                Important Medical Disclaimer
              </h3>
              <div className="text-sm text-yellow-800 space-y-1">
                <p>⚠️ This analysis is a <strong>research tool and screening aid</strong>, not a medical diagnosis.</p>
                <p>✓ <strong>DO:</strong> Use as supplementary information for clinical decision-making.</p>
                <p>✗ <strong>DO NOT:</strong> Use as the sole basis for diagnosis or treatment decisions.</p>
                <p className="font-semibold pt-1">
                  Always consult a qualified neurologist for proper clinical diagnosis and treatment.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
