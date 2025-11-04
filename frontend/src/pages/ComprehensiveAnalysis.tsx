import React, { useState } from 'react';
import { 
  CloudArrowUpIcon, 
  BeakerIcon, 
  PencilSquareIcon, 
  MicrophoneIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import axios from 'axios';

interface ModalityResult {
  prediction?: string;
  probability?: number;
  confidence?: number;
  error?: string;
}

interface FusionResults {
  final_diagnosis: string;
  final_probability: number;
  confidence: number;
  confidence_level: string;
  agreement_score: number;
  modalities_used: string[];
  weights_applied: Record<string, number>;
}

interface AnalysisResult {
  timestamp: string;
  patient_id?: string;
  modalities_analyzed: string[];
  modality_results: {
    dat?: ModalityResult;
    handwriting?: ModalityResult;
    voice?: ModalityResult;
  };
  fusion_results: FusionResults;
  clinical_interpretation: string;
  recommendations: string[];
}

export default function ComprehensiveAnalysis() {
  // File states
  const [datScans, setDatScans] = useState<File[]>([]);
  const [spiralImage, setSpiralImage] = useState<File | null>(null);
  const [waveImage, setWaveImage] = useState<File | null>(null);
  const [voiceFile, setVoiceFile] = useState<File | null>(null);

  // Preview URLs
  const [datPreviews, setDatPreviews] = useState<string[]>([]);
  const [spiralPreview, setSpiralPreview] = useState<string>('');
  const [wavePreview, setWavePreview] = useState<string>('');

  // Analysis states
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string>('');

  // File handlers
  const handleDatScanUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setDatScans(files);
      
      // Create previews
      const previews = files.map(file => URL.createObjectURL(file));
      setDatPreviews(previews);
    }
  };

  const handleSpiralUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSpiralImage(file);
      setSpiralPreview(URL.createObjectURL(file));
    }
  };

  const handleWaveUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setWaveImage(file);
      setWavePreview(URL.createObjectURL(file));
    }
  };

  const handleVoiceUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setVoiceFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    // Validate at least one modality
    if (!datScans.length && !spiralImage && !waveImage && !voiceFile) {
      setError('Please upload at least one modality (DaT scan, handwriting, or voice)');
      return;
    }

    setIsAnalyzing(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();

      // Add DaT scans
      if (datScans.length > 0) {
        datScans.forEach((file) => {
          formData.append('dat_scans', file);
        });
      }

      // Add handwriting images
      if (spiralImage) {
        formData.append('handwriting_spiral', spiralImage);
      }
      if (waveImage) {
        formData.append('handwriting_wave', waveImage);
      }

      // Add voice file
      if (voiceFile) {
        formData.append('voice_recording', voiceFile);
      }

      const token = localStorage.getItem('auth_token');
      const response = await axios.post(
        'http://localhost:8000/api/v1/analysis/multimodal/comprehensive',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`
          }
        }
      );

      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setDatScans([]);
    setSpiralImage(null);
    setWaveImage(null);
    setVoiceFile(null);
    setDatPreviews([]);
    setSpiralPreview('');
    setWavePreview('');
    setResult(null);
    setError('');
  };

  const getConfidenceColor = (level: string) => {
    switch (level) {
      case 'High': return 'text-green-600 bg-green-100';
      case 'Moderate': return 'text-yellow-600 bg-yellow-100';
      case 'Low': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getDiagnosisColor = (diagnosis: string) => {
    return diagnosis.includes('Parkinson') 
      ? 'text-red-600 bg-red-50 border-red-200' 
      : 'text-green-600 bg-green-50 border-green-200';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Comprehensive Parkinson's Analysis
          </h1>
          <p className="text-lg text-gray-600">
            Multi-modal AI-powered diagnosis combining DaT scan, handwriting, and voice analysis
          </p>
          <div className="mt-4 inline-flex items-center px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg">
            <ExclamationTriangleIcon className="h-5 w-5 text-blue-600 mr-2" />
            <span className="text-sm text-blue-800">
              Clinical research tool • Not for primary diagnosis • Requires physician confirmation
            </span>
          </div>
        </div>

        {/* Upload Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* DaT Scan Upload */}
          <div className="bg-white rounded-lg shadow-md p-6 border-2 border-indigo-100">
            <div className="flex items-center mb-4">
              <BeakerIcon className="h-6 w-6 text-indigo-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">DaT Scan</h3>
              <span className="ml-auto text-xs bg-indigo-100 text-indigo-800 px-2 py-1 rounded">
                50% weight
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Upload 12-16 brain scan images
            </p>
            <label className="block">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center cursor-pointer hover:border-indigo-400 transition">
                <CloudArrowUpIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <span className="text-sm text-gray-600">
                  {datScans.length > 0 ? `${datScans.length} scans uploaded` : 'Click to upload'}
                </span>
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleDatScanUpload}
                  className="hidden"
                />
              </div>
            </label>
            {datPreviews.length > 0 && (
              <div className="mt-3 grid grid-cols-4 gap-2">
                {datPreviews.slice(0, 8).map((preview, idx) => (
                  <img
                    key={idx}
                    src={preview}
                    alt={`Scan ${idx + 1}`}
                    className="w-full h-16 object-cover rounded border"
                  />
                ))}
              </div>
            )}
          </div>

          {/* Handwriting Upload */}
          <div className="bg-white rounded-lg shadow-md p-6 border-2 border-purple-100">
            <div className="flex items-center mb-4">
              <PencilSquareIcon className="h-6 w-6 text-purple-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Handwriting</h3>
              <span className="ml-auto text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                25% weight
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Upload spiral and/or wave drawings
            </p>
            
            {/* Spiral */}
            <label className="block mb-3">
              <span className="text-xs text-gray-500 mb-1 block">Spiral Drawing</span>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-3 text-center cursor-pointer hover:border-purple-400 transition">
                <CloudArrowUpIcon className="h-6 w-6 text-gray-400 mx-auto mb-1" />
                <span className="text-xs text-gray-600">
                  {spiralImage ? spiralImage.name : 'Upload spiral'}
                </span>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleSpiralUpload}
                  className="hidden"
                />
              </div>
            </label>
            {spiralPreview && (
              <img src={spiralPreview} alt="Spiral" className="w-full h-24 object-cover rounded mb-3" />
            )}

            {/* Wave */}
            <label className="block">
              <span className="text-xs text-gray-500 mb-1 block">Wave Drawing</span>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-3 text-center cursor-pointer hover:border-purple-400 transition">
                <CloudArrowUpIcon className="h-6 w-6 text-gray-400 mx-auto mb-1" />
                <span className="text-xs text-gray-600">
                  {waveImage ? waveImage.name : 'Upload wave'}
                </span>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleWaveUpload}
                  className="hidden"
                />
              </div>
            </label>
            {wavePreview && (
              <img src={wavePreview} alt="Wave" className="w-full h-24 object-cover rounded mt-2" />
            )}
          </div>

          {/* Voice Upload */}
          <div className="bg-white rounded-lg shadow-md p-6 border-2 border-pink-100">
            <div className="flex items-center mb-4">
              <MicrophoneIcon className="h-6 w-6 text-pink-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Voice Analysis</h3>
              <span className="ml-auto text-xs bg-pink-100 text-pink-800 px-2 py-1 rounded">
                25% weight
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Upload voice recording (WAV/MP3)
            </p>
            <label className="block">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center cursor-pointer hover:border-pink-400 transition">
                <CloudArrowUpIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <span className="text-sm text-gray-600">
                  {voiceFile ? voiceFile.name : 'Click to upload'}
                </span>
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleVoiceUpload}
                  className="hidden"
                />
              </div>
            </label>
            {voiceFile && (
              <div className="mt-3 p-2 bg-pink-50 rounded flex items-center">
                <CheckCircleIcon className="h-5 w-5 text-pink-600 mr-2" />
                <span className="text-sm text-gray-700 truncate">{voiceFile.name}</span>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-center gap-4 mb-8">
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing || (!datScans.length && !spiralImage && !waveImage && !voiceFile)}
            className="px-8 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition flex items-center"
          >
            {isAnalyzing ? (
              <>
                <ArrowPathIcon className="animate-spin h-5 w-5 mr-2" />
                Analyzing...
              </>
            ) : (
              'Analyze All Modalities'
            )}
          </button>
          <button
            onClick={handleReset}
            className="px-8 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition"
          >
            Reset
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-8">
            <p className="font-semibold">Error:</p>
            <p>{error}</p>
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className="space-y-6">
            {/* Overall Diagnosis */}
            <div className={`bg-white rounded-lg shadow-lg p-8 border-2 ${getDiagnosisColor(result.fusion_results.final_diagnosis)}`}>
              <h2 className="text-2xl font-bold mb-4">Overall Diagnosis</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Diagnosis</p>
                  <p className="text-3xl font-bold">{result.fusion_results.final_diagnosis}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Confidence Level</p>
                  <span className={`inline-block px-4 py-2 rounded-lg font-semibold text-lg ${getConfidenceColor(result.fusion_results.confidence_level)}`}>
                    {result.fusion_results.confidence_level} ({(result.fusion_results.confidence * 100).toFixed(1)}%)
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">PD Probability</p>
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-4 mr-3">
                      <div
                        className="bg-indigo-600 h-4 rounded-full"
                        style={{ width: `${result.fusion_results.final_probability * 100}%` }}
                      />
                    </div>
                    <span className="font-bold">{(result.fusion_results.final_probability * 100).toFixed(1)}%</span>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Modality Agreement</p>
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-4 mr-3">
                      <div
                        className="bg-green-600 h-4 rounded-full"
                        style={{ width: `${result.fusion_results.agreement_score * 100}%` }}
                      />
                    </div>
                    <span className="font-bold">{(result.fusion_results.agreement_score * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Individual Modality Results */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {result.modality_results.dat && (
                <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-indigo-500">
                  <h3 className="text-lg font-semibold mb-3 flex items-center">
                    <BeakerIcon className="h-5 w-5 mr-2 text-indigo-600" />
                    DaT Scan
                  </h3>
                  {result.modality_results.dat.error ? (
                    <p className="text-red-600 text-sm">{result.modality_results.dat.error}</p>
                  ) : (
                    <>
                      <p className="text-2xl font-bold mb-2">{result.modality_results.dat.prediction}</p>
                      <p className="text-sm text-gray-600">
                        Probability: {((result.modality_results.dat.probability || 0) * 100).toFixed(1)}%
                      </p>
                      <p className="text-sm text-gray-600">
                        Confidence: {((result.modality_results.dat.confidence || 0) * 100).toFixed(1)}%
                      </p>
                    </>
                  )}
                </div>
              )}

              {result.modality_results.handwriting && (
                <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
                  <h3 className="text-lg font-semibold mb-3 flex items-center">
                    <PencilSquareIcon className="h-5 w-5 mr-2 text-purple-600" />
                    Handwriting
                  </h3>
                  {result.modality_results.handwriting.error ? (
                    <p className="text-red-600 text-sm">{result.modality_results.handwriting.error}</p>
                  ) : (
                    <>
                      <p className="text-2xl font-bold mb-2">{result.modality_results.handwriting.prediction}</p>
                      <p className="text-sm text-gray-600">
                        Probability: {((result.modality_results.handwriting.probability || 0) * 100).toFixed(1)}%
                      </p>
                      <p className="text-sm text-gray-600">
                        Confidence: {((result.modality_results.handwriting.confidence || 0) * 100).toFixed(1)}%
                      </p>
                    </>
                  )}
                </div>
              )}

              {result.modality_results.voice && (
                <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-pink-500">
                  <h3 className="text-lg font-semibold mb-3 flex items-center">
                    <MicrophoneIcon className="h-5 w-5 mr-2 text-pink-600" />
                    Voice
                  </h3>
                  {result.modality_results.voice.error ? (
                    <p className="text-red-600 text-sm">{result.modality_results.voice.error}</p>
                  ) : (
                    <>
                      <p className="text-2xl font-bold mb-2">{result.modality_results.voice.prediction}</p>
                      <p className="text-sm text-gray-600">
                        Probability: {((result.modality_results.voice.probability || 0) * 100).toFixed(1)}%
                      </p>
                      <p className="text-sm text-gray-600">
                        Confidence: {((result.modality_results.voice.confidence || 0) * 100).toFixed(1)}%
                      </p>
                    </>
                  )}
                </div>
              )}
            </div>

            {/* Clinical Interpretation */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">Clinical Interpretation</h3>
              <p className="text-gray-700 leading-relaxed">{result.clinical_interpretation}</p>
            </div>

            {/* Recommendations */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">Recommendations</h3>
              <ul className="space-y-2">
                {result.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start">
                    <CheckCircleIcon className="h-5 w-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Important Disclaimer */}
            <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-yellow-900 mb-3 flex items-center">
                <ExclamationTriangleIcon className="h-6 w-6 mr-2" />
                Important Medical Disclaimer
              </h3>
              <div className="text-sm text-yellow-800 space-y-2">
                <p>
                  ⚠️ This analysis is a <strong>research tool and screening aid</strong>, not a medical diagnosis.
                </p>
                <p>
                  ✓ <strong>DO:</strong> Use this as supplementary information for clinical decision-making
                </p>
                <p>
                  ✗ <strong>DO NOT:</strong> Use this as the sole basis for diagnosis or treatment decisions
                </p>
                <p className="font-semibold pt-2">
                  Always consult with a qualified neurologist for proper clinical diagnosis and treatment.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
