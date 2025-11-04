// HandwritingResults component
import { CheckCircle, AlertTriangle, Activity, TrendingUp, Info } from 'lucide-react';

interface AnalysisResult {
  id: string;
  prediction: string;
  confidence: number;
  analysis_details?: {
    smoothness?: number;
    tremor_ratio?: number;
    pressure_variation?: number;
    contour_count?: number;
  };
  drawing_type: string;
  sentence_prompt?: string;
  created_at: string;
  analyzed_at?: string;
  status: string;
}

interface HandwritingResultsProps {
  result: AnalysisResult;
  onClose: () => void;
  onNewAnalysis: () => void;
}

const HandwritingResults: React.FC<HandwritingResultsProps> = ({ 
  result, 
  onClose, 
  onNewAnalysis 
}) => {
  const isHealthy = result.prediction === 'healthy';
  const confidencePercentage = Math.round(result.confidence * 100);

  const getResultColor = () => {
    if (isHealthy) {
      return result.confidence > 0.8 ? 'green' : 'yellow';
    } else {
      return result.confidence > 0.8 ? 'red' : 'orange';
    }
  };

  const getResultIcon = () => {
    const color = getResultColor();
    switch (color) {
      case 'green':
        return <CheckCircle className="w-8 h-8 text-green-600" />;
      case 'yellow':
        return <Info className="w-8 h-8 text-yellow-600" />;
      case 'orange':
        return <AlertTriangle className="w-8 h-8 text-orange-600" />;
      case 'red':
        return <AlertTriangle className="w-8 h-8 text-red-600" />;
      default:
        return <Activity className="w-8 h-8 text-gray-600" />;
    }
  };

  const getResultMessage = () => {
    if (isHealthy) {
      if (result.confidence > 0.8) {
        return "Your handwriting patterns appear normal with no significant indicators of Parkinson's disease.";
      } else {
        return "Your handwriting appears mostly normal, but some minor irregularities were detected. Consider consulting a healthcare professional if you have concerns.";
      }
    } else {
      if (result.confidence > 0.8) {
        return "Your handwriting shows patterns that may be associated with Parkinson's disease. We strongly recommend consulting with a neurologist for proper evaluation.";
      } else {
        return "Some patterns in your handwriting suggest possible tremor or motor control variations. Consider discussing these results with a healthcare professional.";
      }
    }
  };

  const getConfidenceBarColor = () => {
    const color = getResultColor();
    switch (color) {
      case 'green': return 'bg-green-500';
      case 'yellow': return 'bg-yellow-500';
      case 'orange': return 'bg-orange-500';
      case 'red': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Handwriting Analysis Results
        </h2>
        <p className="text-gray-600">
          Analysis completed for {result.drawing_type} drawing
        </p>
      </div>

      {/* Main Result Card */}
      <div className="bg-white border border-gray-200 rounded-xl p-8 mb-6 shadow-sm">
        <div className="flex items-center justify-center mb-6">
          {getResultIcon()}
        </div>

        <div className="text-center mb-6">
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            {isHealthy ? 'Normal Patterns Detected' : 'Irregular Patterns Detected'}
          </h3>
          <p className="text-gray-600 text-lg leading-relaxed">
            {getResultMessage()}
          </p>
        </div>

        {/* Confidence Score */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">
              Confidence Level
            </span>
            <span className="text-sm font-bold text-gray-900">
              {confidencePercentage}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full ${getConfidenceBarColor()}`}
              style={{ width: `${confidencePercentage}%` }}
            />
          </div>
        </div>

        {/* Analysis Details */}
        {result.analysis_details && (
          <div className="border-t border-gray-200 pt-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">
              Detailed Analysis
            </h4>
            <div className="grid md:grid-cols-2 gap-4">
              {result.analysis_details.smoothness !== undefined && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-4 h-4 text-blue-600" />
                    <span className="font-medium text-gray-900">Smoothness</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900 mb-1">
                    {(result.analysis_details.smoothness * 100).toFixed(1)}%
                  </div>
                  <p className="text-sm text-gray-600">
                    Measures how smooth and continuous your drawing strokes are
                  </p>
                </div>
              )}

              {result.analysis_details.tremor_ratio !== undefined && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="w-4 h-4 text-orange-600" />
                    <span className="font-medium text-gray-900">Tremor Level</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900 mb-1">
                    {(result.analysis_details.tremor_ratio * 100).toFixed(1)}%
                  </div>
                  <p className="text-sm text-gray-600">
                    Indicates irregularities or shaking in your drawing
                  </p>
                </div>
              )}

              {result.analysis_details.pressure_variation !== undefined && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="w-4 h-4 text-purple-600" />
                    <span className="font-medium text-gray-900">Pressure Variation</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900 mb-1">
                    {(result.analysis_details.pressure_variation * 100).toFixed(1)}%
                  </div>
                  <p className="text-sm text-gray-600">
                    Shows how consistent your writing pressure is
                  </p>
                </div>
              )}

              {result.analysis_details.contour_count !== undefined && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Info className="w-4 h-4 text-gray-600" />
                    <span className="font-medium text-gray-900">Drawing Complexity</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900 mb-1">
                    {result.analysis_details.contour_count}
                  </div>
                  <p className="text-sm text-gray-600">
                    Number of distinct drawing segments detected
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Important Disclaimer */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
        <div className="flex items-start gap-3">
          <Info className="w-6 h-6 text-blue-600 mt-0.5 flex-shrink-0" />
          <div>
            <h4 className="font-semibold text-blue-900 mb-2">
              Important Medical Disclaimer
            </h4>
            <p className="text-blue-800 text-sm leading-relaxed">
              This analysis is for screening purposes only and should not be used as a substitute 
              for professional medical diagnosis. If you have concerns about Parkinson's disease 
              or any neurological symptoms, please consult with a qualified healthcare professional 
              or neurologist for proper evaluation and diagnosis.
            </p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={onNewAnalysis}
          className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Try Another Drawing
        </button>
        <button
          onClick={onClose}
          className="px-8 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
        >
          Back to Dashboard
        </button>
      </div>

      {/* Analysis Metadata */}
      <div className="mt-8 text-center text-sm text-gray-500">
        <p>
          Analysis completed on {new Date(result.analyzed_at || result.created_at).toLocaleString()}
        </p>
        {result.sentence_prompt && (
          <p className="mt-1">
            Sentence prompt: "{result.sentence_prompt}"
          </p>
        )}
      </div>
    </div>
  );
};

export default HandwritingResults;