import type { DiagnosisReport } from '../../types';
import { XMarkIcon, ArrowDownTrayIcon, ShareIcon } from '@heroicons/react/24/outline';
import { useEffect } from 'react';

interface ReportDetailsModalProps {
  report: DiagnosisReport;
  onClose: () => void;
  onExport: (reportId: string) => void;
  onShare: (reportId: string) => void;
}

const ReportDetailsModal = ({ report, onClose, onExport, onShare }: ReportDetailsModalProps) => {
  useEffect(() => {
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  const getStageColor = (stage: number) => {
    if (stage === 0) return { bg: 'bg-green-50', text: 'text-green-700', badge: 'bg-green-100' };
    if (stage === 1) return { bg: 'bg-yellow-50', text: 'text-yellow-700', badge: 'bg-yellow-100' };
    if (stage === 2) return { bg: 'bg-orange-50', text: 'text-orange-700', badge: 'bg-orange-100' };
    return { bg: 'bg-red-50', text: 'text-red-700', badge: 'bg-red-100' };
  };

  const getDiagnosisLabel = (diagnosis: string) => {
    const labels: Record<string, string> = {
      healthy: 'Healthy - No PD',
      early_pd: 'Early Stage PD',
      moderate_pd: 'Moderate Stage PD',
      advanced_pd: 'Advanced Stage PD',
    };
    return labels[diagnosis] || diagnosis;
  };

  const stageColor = getStageColor(report.stage);

  // Parse multimodal analysis if it's a string
  const multimodalAnalysis =
    typeof report.multimodalAnalysis === 'string'
      ? JSON.parse(report.multimodalAnalysis)
      : report.multimodalAnalysis;

  // Calculate metrics from multimodal analysis
  const calculateMetrics = () => {
    if (!multimodalAnalysis) return null;

    const datConfidence = multimodalAnalysis.dat_scan?.confidence || 0;
    const handwritingConfidence = multimodalAnalysis.handwriting?.confidence || 0;
    const voiceConfidence = multimodalAnalysis.voice?.confidence || 0;

    const avgConfidence = (datConfidence + handwritingConfidence + voiceConfidence) / 3;
    
    // Calculate which modality needs most improvement
    const confidences = [
      { name: 'DaT Scan', value: datConfidence, icon: '🧠' },
      { name: 'Handwriting', value: handwritingConfidence, icon: '✍️' },
      { name: 'Voice', value: voiceConfidence, icon: '🎤' }
    ];
    
    const lowestConfidence = confidences.reduce((min, curr) => 
      curr.value < min.value ? curr : min
    );

    return {
      avgConfidence,
      lowestConfidence,
      needsImprovement: avgConfidence < 0.7
    };
  };

  const metrics = calculateMetrics();

  // Generate personalized recommendations
  const getRecommendations = (): Array<{
    priority: 'high' | 'medium' | 'low';
    title: string;
    description: string;
    action: string;
  }> => {
    if (!metrics) return [];
    
    const recommendations: Array<{
      priority: 'high' | 'medium' | 'low';
      title: string;
      description: string;
      action: string;
    }> = [];

    // Low overall confidence
    if (metrics.avgConfidence < 0.7) {
      recommendations.push({
        priority: 'high',
        title: 'Improve Data Quality',
        description: `Your overall confidence is ${(metrics.avgConfidence * 100).toFixed(0)}%. Retaking tests with better quality data can increase confidence to 70%+.`,
        action: 'Retake all tests with optimal conditions'
      });
    }

    // Focus on weakest modality
    if (metrics.lowestConfidence.value < 0.6) {
      const tips: Record<string, string> = {
        'DaT Scan': 'Get a professional clinical DaT scan from an imaging center for higher quality results.',
        'Handwriting': 'Draw spirals and waves on clean white paper, scan at 300 DPI, and submit multiple samples.',
        'Voice': 'Record in a quiet room with a good microphone. Say "Aaaaah" for 15 seconds, 3-5 times.'
      };

      recommendations.push({
        priority: 'high',
        title: `Focus on ${metrics.lowestConfidence.icon} ${metrics.lowestConfidence.name}`,
        description: `This modality has the lowest confidence at ${(metrics.lowestConfidence.value * 100).toFixed(0)}%. ${tips[metrics.lowestConfidence.name] || 'Improve data quality.'}`,
        action: `Improve ${metrics.lowestConfidence.name} quality`
      });
    }

    // General recommendations
    if (report.confidence < 0.6) {
      recommendations.push({
        priority: 'medium',
        title: 'Schedule Professional Evaluation',
        description: 'Consider consulting with a neurologist for a comprehensive clinical assessment.',
        action: 'Book appointment with neurologist'
      });
    }

    recommendations.push({
      priority: 'low',
      title: 'Monitor Over Time',
      description: 'Retake tests monthly to track any changes and establish baseline patterns.',
      action: 'Set reminder for monthly retest'
    });

    return recommendations;
  };

  const recommendations = getRecommendations();

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          onClick={onClose}
        />

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                📋 Comprehensive Diagnosis Report
              </h2>
              <button
                onClick={onClose}
                className="text-white hover:text-gray-200 transition-colors"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            <p className="text-sm text-blue-100 mt-1">Report ID: #{report.id}</p>
          </div>

          {/* Content */}
          <div className="px-6 py-6 max-h-[70vh] overflow-y-auto">
            {/* Report Info */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Report Date</p>
                <p className="text-lg font-semibold text-gray-900">
                  {new Date(report.createdAt).toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Verification Status</p>
                <p className="text-lg font-semibold text-gray-900">
                  {report.doctorVerified ? (
                    <span className="text-green-600">✓ Doctor Verified</span>
                  ) : (
                    <span className="text-yellow-600">⏳ Pending Review</span>
                  )}
                </p>
              </div>
            </div>

            {/* Diagnosis Result */}
            <div className={`p-6 rounded-lg border-2 ${stageColor.bg} mb-6`}>
              <h3 className="text-lg font-bold text-gray-900 mb-4">Final Diagnosis</h3>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-gray-600 mb-2">Diagnosis</p>
                  <p className={`text-2xl font-bold ${stageColor.text}`}>
                    {getDiagnosisLabel(report.finalDiagnosis)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-2">Stage</p>
                  <span
                    className={`inline-block px-4 py-2 rounded-full text-xl font-bold ${stageColor.badge} ${stageColor.text}`}
                  >
                    Stage {report.stage}
                  </span>
                </div>
              </div>

              {/* Confidence Score */}
              <div className="mt-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-gray-700">Overall Confidence</p>
                  <p className="text-lg font-bold text-gray-900">
                    {(report.confidence * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="w-full bg-gray-300 rounded-full h-4">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-indigo-600 h-4 rounded-full transition-all duration-500"
                    style={{ width: `${report.confidence * 100}%` }}
                  />
                </div>
              </div>

              {/* Fusion Score */}
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-gray-700">Multimodal Fusion Score</p>
                  <p className="text-lg font-bold text-gray-900">
                    {(report.fusionScore * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="w-full bg-gray-300 rounded-full h-4">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-pink-600 h-4 rounded-full transition-all duration-500"
                    style={{ width: `${report.fusionScore * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Multimodal Analysis Breakdown */}
            <div className="mb-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                Multimodal Analysis Breakdown
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* DaT Scan */}
                <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-indigo-900">🧠 DaT Scan</h4>
                    <span className="text-xs bg-indigo-200 text-indigo-800 px-2 py-1 rounded">
                      50% Weight
                    </span>
                  </div>
                  {multimodalAnalysis?.dat_scan ? (
                    <div className="space-y-2">
                      <div>
                        <p className="text-xs text-gray-600">Confidence</p>
                        <p className="text-lg font-bold text-indigo-700">
                          {(multimodalAnalysis.dat_scan.confidence * 100).toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Prediction</p>
                        <p className="text-sm font-medium text-gray-900">
                          {multimodalAnalysis.dat_scan.prediction || 'N/A'}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No DaT scan data available</p>
                  )}
                </div>

                {/* Handwriting */}
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-purple-900">✍️ Handwriting</h4>
                    <span className="text-xs bg-purple-200 text-purple-800 px-2 py-1 rounded">
                      25% Weight
                    </span>
                  </div>
                  {multimodalAnalysis?.handwriting ? (
                    <div className="space-y-2">
                      <div>
                        <p className="text-xs text-gray-600">Confidence</p>
                        <p className="text-lg font-bold text-purple-700">
                          {(multimodalAnalysis.handwriting.confidence * 100).toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Prediction</p>
                        <p className="text-sm font-medium text-gray-900">
                          {multimodalAnalysis.handwriting.prediction || 'N/A'}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No handwriting data available</p>
                  )}
                </div>

                {/* Voice */}
                <div className="bg-pink-50 border border-pink-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-pink-900">🎤 Voice</h4>
                    <span className="text-xs bg-pink-200 text-pink-800 px-2 py-1 rounded">
                      25% Weight
                    </span>
                  </div>
                  {multimodalAnalysis?.voice ? (
                    <div className="space-y-2">
                      <div>
                        <p className="text-xs text-gray-600">Confidence</p>
                        <p className="text-lg font-bold text-pink-700">
                          {(multimodalAnalysis.voice.confidence * 100).toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Prediction</p>
                        <p className="text-sm font-medium text-gray-900">
                          {multimodalAnalysis.voice.prediction || 'N/A'}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No voice data available</p>
                  )}
                </div>
              </div>
            </div>

            {/* Doctor's Notes */}
            {report.doctorNotes && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="text-lg font-bold text-blue-900 mb-2">Doctor's Notes</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{report.doctorNotes}</p>
              </div>
            )}

            {/* Personalized Recommendations */}
            {recommendations.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                  💡 Personalized Recommendations
                </h3>
                <div className="space-y-3">
                  {recommendations.map((rec, index) => {
                    const priorityColors = {
                      high: 'border-red-200 bg-red-50',
                      medium: 'border-yellow-200 bg-yellow-50',
                      low: 'border-blue-200 bg-blue-50'
                    };
                    const priorityBadges = {
                      high: 'bg-red-100 text-red-700',
                      medium: 'bg-yellow-100 text-yellow-700',
                      low: 'bg-blue-100 text-blue-700'
                    };
                    const priorityLabels = {
                      high: '🔴 High Priority',
                      medium: '🟡 Medium Priority',
                      low: '🟢 Low Priority'
                    };

                    return (
                      <div
                        key={index}
                        className={`border rounded-lg p-4 ${priorityColors[rec.priority]}`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-semibold text-gray-900">{rec.title}</h4>
                          <span className={`text-xs px-2 py-1 rounded ${priorityBadges[rec.priority]}`}>
                            {priorityLabels[rec.priority]}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 mb-2">{rec.description}</p>
                        <div className="flex items-center gap-2 text-xs text-gray-600">
                          <span>📋 Action:</span>
                          <span className="font-medium">{rec.action}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
                
                {/* Quick Tips */}
                <div className="mt-4 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-4">
                  <h4 className="font-semibold text-indigo-900 mb-2">🎯 Quick Tips to Improve Your Results</h4>
                  <ul className="text-sm text-gray-700 space-y-1">
                    <li>• <strong>Voice:</strong> Use a good microphone in a quiet room, record "Aaaaah" for 15 seconds</li>
                    <li>• <strong>Handwriting:</strong> Draw naturally on white paper, scan at 300 DPI</li>
                    <li>• <strong>DaT Scan:</strong> Request professional imaging from your doctor</li>
                    <li>• <strong>Timing:</strong> Test in the morning when well-rested for consistency</li>
                  </ul>
                </div>
              </div>
            )}

            {/* Medical Disclaimer */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-xs text-yellow-800">
                <strong>⚠️ Medical Disclaimer:</strong> This report is generated by AI and should
                be used for informational purposes only. Please consult with a qualified healthcare
                professional for proper diagnosis and treatment.
              </p>
            </div>
          </div>

          {/* Footer Actions */}
          <div className="bg-gray-50 px-6 py-4 flex items-center justify-between border-t">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Close
            </button>
            <div className="flex gap-3">
              <button
                onClick={() => onExport(report.id)}
                className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <ArrowDownTrayIcon className="h-5 w-5" />
                Download PDF
              </button>
              <button
                onClick={() => onShare(report.id)}
                className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                <ShareIcon className="h-5 w-5" />
                Share
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportDetailsModal;
