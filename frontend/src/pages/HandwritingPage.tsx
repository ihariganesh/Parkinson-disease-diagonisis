import { useState } from 'react';
import { Link } from 'react-router-dom';
import { HandwritingUpload, HandwritingResults } from '../components/handwriting';
import { apiClient } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface AnalysisResult {
  id: string;
  prediction: string;
  confidence: number;
  analysis_details?: any;
  drawing_type: string;
  sentence_prompt?: string;
  created_at: string;
  analyzed_at?: string;
  status: string;
  error_message?: string;
}

const HandwritingPage: React.FC = () => {
  const { state } = useAuth();
  const [currentView, setCurrentView] = useState<'upload' | 'results'>('upload');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleUploadComplete = async (uploadResult: any) => {
    setLoading(true);
    
    try {
      // For demo mode, results are immediate
      if (!state.isAuthenticated) {
        setAnalysisResult({
          id: uploadResult.analysis_id,
          prediction: uploadResult.prediction,
          confidence: uploadResult.confidence_score,
          analysis_details: uploadResult.analysis_details,
          drawing_type: uploadResult.drawing_type,
          sentence_prompt: uploadResult.sentence_prompt,
          created_at: uploadResult.created_at,
          status: uploadResult.status
        });
        setCurrentView('results');
        setLoading(false);
        return;
      }

      // For authenticated users, poll for results
      const analysisId = uploadResult.id;
      let attempts = 0;
      const maxAttempts = 30;
      
      const pollResults = async () => {
        try {
          const response = await apiClient.get(`/handwriting/analyses/${analysisId}`);
          
          if (response.success && response.data) {
            const analysis = response.data as any;
            
            if (analysis.status === 'completed') {
              setAnalysisResult({
                id: analysis.id,
                prediction: analysis.prediction,
                confidence: analysis.confidence_score,
                analysis_details: analysis.analysis_details,
                drawing_type: analysis.drawing_type,
                sentence_prompt: analysis.sentence_prompt,
                created_at: analysis.created_at,
                analyzed_at: analysis.analyzed_at,
                status: analysis.status
              });
              setCurrentView('results');
              setLoading(false);
              return;
            } else if (analysis.status === 'failed') {
              setAnalysisResult({
                id: analysis.id,
                prediction: 'error',
                confidence: 0,
                drawing_type: analysis.drawing_type,
                created_at: analysis.created_at,
                status: analysis.status,
                error_message: analysis.error_message
              });
              setCurrentView('results');
              setLoading(false);
              return;
            }
          }
          
          attempts++;
          if (attempts < maxAttempts) {
            setTimeout(pollResults, 1000);
          } else {
            throw new Error('Analysis timeout - please try again later');
          }
        } catch (error) {
          console.error('Error polling results:', error);
          setAnalysisResult({
            id: analysisId,
            prediction: 'error',
            confidence: 0,
            drawing_type: 'unknown',
            created_at: new Date().toISOString(),
            status: 'failed',
            error_message: error instanceof Error ? error.message : 'Analysis failed'
          });
          setCurrentView('results');
          setLoading(false);
        }
      };
      
      pollResults();
    } catch (error) {
      console.error('Upload error:', error);
      setLoading(false);
    }
  };

  const handleBackToUpload = () => {
    setAnalysisResult(null);
    setCurrentView('upload');
  };

  const handleClose = () => {
    if (state.isAuthenticated) {
      window.location.href = '/dashboard';
    } else {
      window.location.href = '/';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Analyzing Your Handwriting
          </h2>
          <p className="text-gray-600">
            Our AI is processing your drawing patterns. This may take a few moments...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Demo Navigation */}
      {!state.isAuthenticated && (
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <Link to="/" className="text-xl font-bold text-blue-600">
                  ParkinsonCare
                </Link>
              </div>
              <div className="flex items-center space-x-4">
                <Link 
                  to="/login" 
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
                >
                  Sign In
                </Link>
                <Link 
                  to="/register" 
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
                >
                  Get Started
                </Link>
              </div>
            </div>
          </div>
        </nav>
      )}

      {/* Demo Mode Banner */}
      {!state.isAuthenticated && (
        <div className="bg-blue-50 border-b border-blue-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    Demo Mode
                  </span>
                </div>
                <p className="ml-3 text-sm text-blue-700">
                  You're using handwriting analysis without an account.{' '}
                  <Link to="/register" className="font-medium underline hover:text-blue-600">
                    Register here
                  </Link>{' '}
                  to save your results and access full features.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'upload' && (
          <HandwritingUpload 
            onUploadComplete={handleUploadComplete}
            onCancel={handleClose}
            isAuthenticated={state.isAuthenticated}
          />
        )}
        
        {currentView === 'results' && analysisResult && (
          <HandwritingResults 
            result={analysisResult}
            onNewAnalysis={handleBackToUpload}
            onClose={handleClose}
          />
        )}
      </div>
    </div>
  );
};

export default HandwritingPage;
