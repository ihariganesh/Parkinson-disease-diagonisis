import { Link } from "react-router-dom";
import { useAuth } from '../contexts/AuthContext';
import {
  PencilSquareIcon,
  SpeakerWaveIcon,
  HeartIcon,
  DocumentTextIcon,
  ChartBarIcon,
  CloudArrowUpIcon,
  CpuChipIcon,
  ArrowLeftIcon,
} from "@heroicons/react/24/outline";

export default function AnalysisHub() {
  const { state } = useAuth();
  const analysisSteps = [
    {
      step: 1,
      title: "Upload Your Data",
      description: "Securely upload all your medical data for comprehensive analysis",
      icon: CloudArrowUpIcon,
    },
    {
      step: 2,
      title: "AI Processing",
      description: "Our advanced AI analyzes all data types together using multimodal learning",
      icon: CpuChipIcon,
    },
    {
      step: 3,
      title: "Get Results",
      description: "Receive comprehensive diagnosis and Parkinson's stage assessment",
      icon: ChartBarIcon,
    },
  ];

  const dataTypes = [
    {
      id: "handwriting",
      title: "Handwriting Samples",
      description: "Digital drawings of spirals, waves, and writing samples",
      icon: PencilSquareIcon,
      color: "blue",
      examples: ["Spiral drawings", "Wave patterns", "Handwriting samples"],
    },
    {
      id: "voice",
      title: "Voice Recordings",
      description: "Speech patterns and vocal biomarkers analysis",
      icon: SpeakerWaveIcon,
      color: "green",
      examples: ["Speech recordings", "Sustained vowels", "Reading passages"],
    },
    {
      id: "ecg",
      title: "ECG Data",
      description: "Cardiovascular patterns and heart rhythm analysis",
      icon: HeartIcon,
      color: "red",
      examples: ["ECG recordings", "Heart rate data", "Rhythm patterns"],
    },
    // MRI analysis type removed during cleanup
    {
      id: "medical-reports",
      title: "Medical Reports",
      description: "Clinical assessments and doctor evaluations",
      icon: DocumentTextIcon,
      color: "yellow",
      examples: ["UPDRS scores", "Clinical notes", "Lab results"],
    },
  ];

  const getColorClasses = (color: string) => {
    const colors: Record<string, any> = {
      blue: "border-blue-200 bg-blue-50",
      green: "border-green-200 bg-green-50",
      red: "border-red-200 bg-red-50",
      purple: "border-purple-200 bg-purple-50",
      yellow: "border-yellow-200 bg-yellow-50",
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Back Navigation - only show for non-authenticated users */}
      {!state.isAuthenticated && (
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <Link 
              to="/"
              className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeftIcon className="h-5 w-5 mr-2" />
              Back to Home
            </Link>
          </div>
        </div>
      )}

      {/* For authenticated users, show simple back to dashboard link */}
      {state.isAuthenticated && (
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <Link 
              to="/patient"
              className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeftIcon className="h-5 w-5 mr-2" />
              Back to Dashboard
            </Link>
          </div>
        </div>
      )}

      {/* Header Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-8">
        <div className="text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Comprehensive AI Analysis
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-4xl mx-auto">
            Upload all your medical data at once for integrated multimodal analysis. 
            Our AI combines handwriting, voice, and medical reports to provide 
            accurate Parkinson's disease assessment and staging.
          </p>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-white rounded-xl p-8 shadow-sm mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">
            How Our Integrated Analysis Works
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            {analysisSteps.map((step) => (
              <div key={step.step} className="text-center">
                <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white text-xl font-bold">
                  {step.step}
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <step.icon className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {step.title}
                </h3>
                <p className="text-gray-600">
                  {step.description}
                </p>
              </div>
            ))}
          </div>

          <div className="text-center">
            <Link
              to="/upload"
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-4 px-8 rounded-lg text-lg transition duration-200 ease-in-out inline-flex items-center"
            >
              <CloudArrowUpIcon className="h-5 w-5 mr-2" />
              Start Comprehensive Analysis
            </Link>
            <p className="text-sm text-gray-500 mt-2">
              Upload all your medical data for integrated multimodal AI analysis.
            </p>
            
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600 mb-2">Or try our handwriting analysis demo:</p>
              <Link
                to="/handwriting"
                className="text-blue-600 hover:text-blue-800 underline text-sm"
              >
                Quick Handwriting Test →
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Data Types Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-white rounded-xl p-8 shadow-sm">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Supported Data Types for Integrated Analysis
          </h2>
          <p className="text-gray-600 text-center mb-8 max-w-3xl mx-auto">
            Our AI system analyzes all these data types together to provide a comprehensive 
            assessment. The more data you provide, the more accurate the analysis becomes.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {dataTypes.map((dataType) => (
              <div
                key={dataType.id}
                className={`
                  p-6 rounded-lg border-2 transition-all duration-200
                  ${getColorClasses(dataType.color)}
                `}
              >
                <div className="flex items-start space-x-4">
                  <div className={`
                    w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0
                    bg-white shadow-sm
                  `}>
                    <dataType.icon className="h-6 w-6 text-gray-700" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {dataType.title}
                    </h3>
                    <p className="text-sm text-gray-600 mb-3">
                      {dataType.description}
                    </p>
                    <div className="space-y-1">
                      {dataType.examples.map((example, index) => (
                        <div key={index} className="flex items-center text-xs text-gray-500">
                          <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mr-2"></div>
                          {example}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Individual Analysis Demos */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Try Individual Analysis Demos
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Experience our AI-powered analysis tools for individual data types. 
            Perfect for exploring our technology before full multimodal analysis.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Handwriting Analysis Demo */}
          <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                <PencilSquareIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Handwriting Analysis</h3>
                <p className="text-gray-600">Draw spirals to detect motor symptoms</p>
              </div>
            </div>
            <p className="text-gray-600 mb-6">
              Upload spiral drawings or wave patterns to analyze motor control and tremor patterns 
              associated with Parkinson's disease.
            </p>
            <Link
              to="/handwriting"
              className="inline-flex items-center justify-center w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition-colors"
            >
              Try Handwriting Demo
            </Link>
          </div>

          {/* Speech Analysis Demo */}
          <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                <SpeakerWaveIcon className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Speech Analysis</h3>
                <p className="text-gray-600">Analyze voice patterns and speech biomarkers</p>
              </div>
            </div>
            <p className="text-gray-600 mb-6">
              Record your voice or upload audio to detect speech changes like reduced volume, 
              monotone speech, and other vocal symptoms of Parkinson's.
            </p>
            <Link
              to="/speech"
              className="inline-flex items-center justify-center w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-6 rounded-lg transition-colors"
            >
              Try Speech Analysis
            </Link>
          </div>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-8 text-white">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">
              Why Integrated Multimodal Analysis?
            </h2>
            <p className="text-blue-100 mb-8 max-w-4xl mx-auto">
              Parkinson's disease affects multiple body systems. By analyzing all data types together, 
              our AI provides more accurate staging and assessment than any single data source alone.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <ChartBarIcon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Higher Accuracy</h3>
                <p className="text-blue-100">
                  95%+ accuracy through multimodal data fusion and advanced AI models
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CpuChipIcon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Complete Assessment</h3>
                <p className="text-blue-100">
                  Comprehensive analysis of disease stage, progression, and severity
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <DocumentTextIcon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Personalized Insights</h3>
                <p className="text-blue-100">
                  Tailored recommendations based on your complete health profile
                </p>
              </div>
            </div>

            <div className="mt-8">
              {state.isAuthenticated ? (
                <Link
                  to="/upload"
                  className="bg-white text-blue-600 hover:bg-gray-100 font-medium py-3 px-8 rounded-lg text-lg transition duration-200 ease-in-out"
                >
                  Start Your Analysis
                </Link>
              ) : (
                <Link
                  to="/register"
                  className="bg-white text-blue-600 hover:bg-gray-100 font-medium py-3 px-8 rounded-lg text-lg transition duration-200 ease-in-out"
                >
                  Get Full Multimodal Access
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}