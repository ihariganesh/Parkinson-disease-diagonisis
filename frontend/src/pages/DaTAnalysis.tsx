import React, { useState, useCallback } from 'react';
import { Upload, Brain, AlertCircle, CheckCircle, FileImage, X, Loader2 } from 'lucide-react';
import axios from 'axios';

interface PredictionResult {
  prediction: string;
  class: number;
  confidence: number;
  probability_healthy: number;
  probability_parkinson: number;
  risk_level: string;
  interpretation: string;
  recommendations: string[];
  timestamp: string;
}

interface AnalysisResponse {
  success: boolean;
  result?: PredictionResult;
  error?: string;
  message?: string;
}

const DaTAnalysis: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  // Handle file selection
  const handleFileChange = useCallback((selectedFiles: FileList | null) => {
    if (!selectedFiles) return;

    const fileArray = Array.from(selectedFiles);
    const imageFiles = fileArray.filter(file => 
      file.type.startsWith('image/')
    );

    if (imageFiles.length === 0) {
      setError('Please select valid image files (PNG, JPG, JPEG)');
      return;
    }

    // Limit to 20 files
    if (imageFiles.length > 20) {
      setError('Maximum 20 files allowed. Please select fewer files.');
      return;
    }

    setFiles(imageFiles);
    setError(null);
    setResult(null);

    // Generate previews
    const previewUrls: string[] = [];
    imageFiles.forEach(file => {
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target?.result) {
          previewUrls.push(e.target.result as string);
          if (previewUrls.length === imageFiles.length) {
            setPreviews(previewUrls);
          }
        }
      };
      reader.readAsDataURL(file);
    });
  }, []);

  // Handle drag and drop
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files);
    }
  }, [handleFileChange]);

  // Remove file
  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
    setPreviews(prev => prev.filter((_, i) => i !== index));
  };

  // Submit for analysis
  const handleAnalyze = async () => {
    if (files.length === 0) {
      setError('Please select at least one scan image');
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      const token = localStorage.getItem('auth_token'); // Fixed: use 'auth_token' instead of 'token'
      
      if (!token) {
        setError('Authentication required. Please login first.');
        setUploading(false);
        return;
      }

      const response = await axios.post<AnalysisResponse>(
        'http://localhost:8000/api/v1/analysis/dat/analyze',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.data.success && response.data.result) {
        setResult(response.data.result);
      } else {
        setError(response.data.error || 'Analysis failed');
      }
    } catch (err: any) {
      console.error('Analysis error:', err);
      
      if (err.response?.status === 401) {
        setError('Authentication failed. Please login to continue.');
        // Optionally redirect to login after a delay
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      } else {
        setError(
          err.response?.data?.detail || 
          err.response?.data?.message ||
          'Failed to analyze scans. Please try again.'
        );
      }
    } finally {
      setUploading(false);
    }
  };

  // Get risk level color
  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'moderate':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'high':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  // Get prediction color
  const getPredictionColor = (prediction: string) => {
    return prediction.toLowerCase() === 'healthy' 
      ? 'text-green-600' 
      : 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center gap-3 mb-2">
            <Brain className="w-8 h-8 text-indigo-600" />
            <h1 className="text-3xl font-bold text-gray-800">DaT Scan Analysis</h1>
          </div>
          <p className="text-gray-600">
            Upload DaT (Dopamine Transporter) scan images for AI-powered Parkinson's Disease detection
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upload Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Upload Scan Images</h2>
            
            {/* Drop Zone */}
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive 
                  ? 'border-indigo-500 bg-indigo-50' 
                  : 'border-gray-300 hover:border-indigo-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                id="file-upload"
                multiple
                accept="image/*"
                onChange={(e) => handleFileChange(e.target.files)}
                className="hidden"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center"
              >
                <Upload className="w-12 h-12 text-indigo-600 mb-4" />
                <p className="text-lg font-medium text-gray-700 mb-2">
                  Drop files here or click to browse
                </p>
                <p className="text-sm text-gray-500">
                  Support: PNG, JPG, JPEG (Max 20 files)
                </p>
              </label>
            </div>

            {/* File Previews */}
            {files.length > 0 && (
              <div className="mt-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">
                  Selected Files ({files.length})
                </h3>
                <div className="grid grid-cols-4 gap-3 max-h-64 overflow-y-auto">
                  {previews.map((preview, index) => (
                    <div key={index} className="relative group">
                      <img
                        src={preview}
                        alt={`Scan ${index + 1}`}
                        className="w-full h-20 object-cover rounded border border-gray-200"
                      />
                      <button
                        onClick={() => removeFile(index)}
                        className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="w-3 h-3" />
                      </button>
                      <div className="text-xs text-gray-500 mt-1 truncate">
                        {files[index].name}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Analyze Button */}
            <button
              onClick={handleAnalyze}
              disabled={files.length === 0 || uploading}
              className={`w-full mt-6 py-3 px-4 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2 ${
                files.length === 0 || uploading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
              }`}
            >
              {uploading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Brain className="w-5 h-5" />
                  Analyze Scans
                </>
              )}
            </button>

            {/* Error Message */}
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}
          </div>

          {/* Results Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Analysis Results</h2>
            
            {!result && !uploading && (
              <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                <FileImage className="w-16 h-16 mb-4" />
                <p className="text-center">
                  Upload and analyze scan images to see results
                </p>
              </div>
            )}

            {uploading && (
              <div className="flex flex-col items-center justify-center h-64">
                <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mb-4" />
                <p className="text-gray-600">Analyzing scan images...</p>
              </div>
            )}

            {result && (
              <div className="space-y-4">
                {/* Prediction */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600">Prediction:</span>
                    <span className={`text-2xl font-bold ${getPredictionColor(result.prediction)}`}>
                      {result.prediction}
                    </span>
                  </div>
                  
                  {/* Confidence */}
                  <div className="mb-3">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Confidence:</span>
                      <span className="font-semibold text-gray-800">
                        {(result.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full transition-all"
                        style={{ width: `${result.confidence * 100}%` }}
                      />
                    </div>
                  </div>

                  {/* Risk Level */}
                  <div className={`border rounded-lg p-3 ${getRiskColor(result.risk_level)}`}>
                    <div className="flex items-center gap-2">
                      {result.risk_level.toLowerCase() === 'low' ? (
                        <CheckCircle className="w-5 h-5" />
                      ) : (
                        <AlertCircle className="w-5 h-5" />
                      )}
                      <span className="font-semibold">
                        Risk Level: {result.risk_level}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Probabilities */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">
                    Class Probabilities
                  </h3>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">Healthy:</span>
                        <span className="font-semibold text-green-600">
                          {(result.probability_healthy * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${result.probability_healthy * 100}%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">Parkinson's:</span>
                        <span className="font-semibold text-red-600">
                          {(result.probability_parkinson * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-red-500 h-2 rounded-full"
                          style={{ width: `${result.probability_parkinson * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Clinical Interpretation */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">
                    Clinical Interpretation
                  </h3>
                  <p className="text-sm text-gray-600">{result.interpretation}</p>
                </div>

                {/* Recommendations */}
                {result.recommendations && result.recommendations.length > 0 && (
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">
                      Recommendations
                    </h3>
                    <ul className="space-y-2">
                      {result.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                          <span className="text-indigo-600 font-bold">•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Timestamp */}
                <div className="text-xs text-gray-400 text-center">
                  Analysis completed: {new Date(result.timestamp).toLocaleString()}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Information */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p className="font-semibold mb-1">Important Information:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Upload 10-20 sequential DaT scan slices for best results</li>
                <li>Images should be in PNG, JPG, or JPEG format</li>
                <li>This is an AI-assisted screening tool and should not replace clinical diagnosis</li>
                <li>Always consult with a qualified neurologist for proper diagnosis</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DaTAnalysis;
