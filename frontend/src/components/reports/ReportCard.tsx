import type { DiagnosisReport } from '../../types';
import {
  CheckCircleIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  EyeIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';

interface ReportCardProps {
  report: DiagnosisReport;
  onView: (report: DiagnosisReport) => void;
  onExport: (reportId: string) => void;
  onShare: (reportId: string) => void;
  onDelete: (reportId: string) => void;
}

const ReportCard = ({ report, onView, onExport, onShare, onDelete }: ReportCardProps) => {
  // Get stage color
  const getStageColor = (stage: number) => {
    if (stage === 0) return { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' };
    if (stage === 1) return { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200' };
    if (stage === 2) return { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200' };
    return { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' };
  };

  // Get diagnosis label
  const getDiagnosisLabel = (diagnosis: string) => {
    const labels: Record<string, string> = {
      healthy: 'Healthy',
      early_pd: 'Early PD',
      moderate_pd: 'Moderate PD',
      advanced_pd: 'Advanced PD',
    };
    return labels[diagnosis] || diagnosis;
  };

  const stageColor = getStageColor(report.stage);
  const confidencePercentage = (report.confidence * 100).toFixed(1);

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white p-4">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-semibold flex items-center gap-2">
              📋 Diagnosis Report
              {report.doctorVerified && (
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-500 rounded text-xs">
                  <CheckCircleIcon className="h-4 w-4" />
                  Verified
                </span>
              )}
            </h3>
            <p className="text-sm text-blue-100 mt-1">
              ID: #{report.id.substring(0, 8)}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-blue-100">Created</p>
            <p className="text-sm font-medium">
              {new Date(report.createdAt).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              })}
            </p>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="p-4 space-y-4">
        {/* Diagnosis Result */}
        <div className={`p-3 rounded-lg border ${stageColor.bg} ${stageColor.border}`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Diagnosis</span>
            <span className={`text-lg font-bold ${stageColor.text}`}>
              {getDiagnosisLabel(report.finalDiagnosis)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Stage</span>
            <span className={`px-3 py-1 rounded-full text-sm font-bold ${stageColor.bg} ${stageColor.text}`}>
              Stage {report.stage}
            </span>
          </div>
        </div>

        {/* Confidence Score */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Confidence Score</span>
            <span className="text-sm font-bold text-gray-900">{confidencePercentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-blue-500 to-indigo-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${confidencePercentage}%` }}
            />
          </div>
        </div>

        {/* Multimodal Analysis Summary */}
        {report.multimodalAnalysis && (
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-700">Analysis Breakdown</p>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-indigo-50 rounded p-2">
                <p className="text-xs text-gray-600">DaT Scan</p>
                <p className="text-sm font-bold text-indigo-700">50%</p>
              </div>
              <div className="bg-purple-50 rounded p-2">
                <p className="text-xs text-gray-600">Handwriting</p>
                <p className="text-sm font-bold text-purple-700">25%</p>
              </div>
              <div className="bg-pink-50 rounded p-2">
                <p className="text-xs text-gray-600">Voice</p>
                <p className="text-sm font-bold text-pink-700">25%</p>
              </div>
            </div>
          </div>
        )}

        {/* Fusion Score */}
        {report.fusionScore && (
          <div className="bg-gray-50 rounded p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Fusion Score</span>
              <span className="text-lg font-bold text-gray-900">
                {(report.fusionScore * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        )}

        {/* Doctor Notes */}
        {report.doctorNotes && (
          <div className="bg-blue-50 border border-blue-200 rounded p-3">
            <p className="text-xs font-medium text-blue-700 mb-1">Doctor's Notes</p>
            <p className="text-sm text-gray-700 line-clamp-2">{report.doctorNotes}</p>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="bg-gray-50 px-4 py-3 border-t border-gray-200 flex items-center justify-between gap-2">
        <button
          onClick={() => onView(report)}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <EyeIcon className="h-4 w-4" />
          View Details
        </button>
        <button
          onClick={() => onExport(report.id)}
          className="px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          title="Download PDF"
        >
          <ArrowDownTrayIcon className="h-5 w-5" />
        </button>
        <button
          onClick={() => onShare(report.id)}
          className="px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          title="Share Report"
        >
          <ShareIcon className="h-5 w-5" />
        </button>
        <button
          onClick={() => onDelete(report.id)}
          className="px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
          title="Delete Report"
        >
          <TrashIcon className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
};

export default ReportCard;
