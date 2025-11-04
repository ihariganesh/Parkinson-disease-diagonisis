import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { SpeechAnalysis } from '../components/speech';
import {
  ArrowLeftIcon,
  SpeakerWaveIcon,
} from '@heroicons/react/24/outline';

export default function SpeechAnalysisPage() {
  const { state } = useAuth();

  const handleAnalysisComplete = (result: any) => {
    console.log('Speech analysis completed:', result);
    // Could redirect to results page or show success message
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Back Navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link 
            to={state.isAuthenticated ? "/patient" : "/analysis"}
            className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Back to {state.isAuthenticated ? "Dashboard" : "Analysis Hub"}
          </Link>
        </div>
      </div>

      {/* Header */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-6">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="bg-blue-100 p-3 rounded-full">
              <SpeakerWaveIcon className="h-8 w-8 text-blue-600" />
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Speech Analysis for Parkinson's Detection
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Our advanced speech analysis uses artificial intelligence to detect subtle changes in voice patterns
            that may indicate Parkinson's disease. Record your voice or upload an audio file to get started.
          </p>
        </div>
      </div>

      {/* Instructions */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 mb-8">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-blue-900 mb-3">Instructions for Best Results</h2>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-800">
            <div>
              <h3 className="font-medium mb-2">Recording Guidelines:</h3>
              <ul className="space-y-1">
                <li>• Record in a quiet environment</li>
                <li>• Speak clearly and naturally</li>
                <li>• Record for at least 10-15 seconds</li>
                <li>• Use a good quality microphone if possible</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium mb-2">What to Say:</h3>
              <ul className="space-y-1">
                <li>• Sustained vowels: "Ahhh", "Ehhh", "Ohhh"</li>
                <li>• Read a short passage or paragraph</li>
                <li>• Count from 1 to 20</li>
                <li>• Speak naturally about your day</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Speech Analysis Component */}
      <SpeechAnalysis onAnalysisComplete={handleAnalysisComplete} />

      {/* Disclaimer */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-yellow-900 mb-2">Important Disclaimer</h3>
          <p className="text-sm text-yellow-800">
            This speech analysis tool is for research and educational purposes only. It is not a substitute for 
            professional medical diagnosis. The results should not be used as the sole basis for medical decisions. 
            Please consult with a qualified healthcare professional for proper diagnosis and treatment of any 
            health concerns.
          </p>
        </div>
      </div>
    </div>
  );
}