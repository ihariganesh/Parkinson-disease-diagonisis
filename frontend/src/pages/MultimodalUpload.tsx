import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  PencilSquareIcon,
  SpeakerWaveIcon,
  HeartIcon,
  // CpuChipIcon, // removed with MRI cleanup
  DocumentTextIcon,
  CloudArrowUpIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowLeftIcon,
} from '@heroicons/react/24/outline';

interface UploadedFile {
  file: File;
  type: string;
  preview?: string;
}

export default function MultimodalUpload() {
  const { state } = useAuth();
  const [uploadedFiles, setUploadedFiles] = useState<Record<string, UploadedFile[]>>({
    handwriting: [],
    voice: [],
    ecg: [],
    // mri: [], // removed during cleanup
    reports: []
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);

  const dataTypes = [
    {
      id: 'handwriting',
      title: 'Handwriting Samples',
      description: 'Upload spiral drawings, wave patterns, or handwriting samples',
      icon: PencilSquareIcon,
      color: 'blue',
      acceptedFormats: '.png, .jpg, .jpeg, .pdf',
      multiple: true,
      required: true,
    },
    {
      id: 'voice',
      title: 'Voice Recordings',
      description: 'Upload speech recordings or vocal exercises',
      icon: SpeakerWaveIcon,
      color: 'green',
      acceptedFormats: '.mp3, .wav, .m4a',
      multiple: true,
      required: false,
    },
    {
      id: 'ecg',
      title: 'ECG Data',
      description: 'Upload ECG recordings or heart rhythm data',
      icon: HeartIcon,
      color: 'red',
      acceptedFormats: '.pdf, .csv, .txt, .xml',
      multiple: true,
      required: false,
    },
    // MRI scan type removed during cleanup
    {
      id: 'reports',
      title: 'Medical Reports',
      description: 'Upload doctor reports, lab results, or clinical assessments',
      icon: DocumentTextIcon,
      color: 'yellow',
      acceptedFormats: '.pdf, .doc, .docx, .txt',
      multiple: true,
      required: false,
    },
  ];

  const getColorClasses = (color: string) => {
    const colors: Record<string, any> = {
      blue: 'border-blue-200 bg-blue-50',
      green: 'border-green-200 bg-green-50',
      red: 'border-red-200 bg-red-50',
      purple: 'border-purple-200 bg-purple-50',
      yellow: 'border-yellow-200 bg-yellow-50',
    };
    return colors[color] || colors.blue;
  };

  const handleFileUpload = (dataTypeId: string, files: FileList | null) => {
    if (!files) return;

    const newFiles: UploadedFile[] = Array.from(files).map(file => ({
      file,
      type: dataTypeId,
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
    }));

    setUploadedFiles(prev => ({
      ...prev,
      [dataTypeId]: [...prev[dataTypeId], ...newFiles]
    }));
  };

  const removeFile = (dataTypeId: string, index: number) => {
    setUploadedFiles(prev => ({
      ...prev,
      [dataTypeId]: prev[dataTypeId].filter((_, i) => i !== index)
    }));
  };

  const hasRequiredFiles = () => {
    return uploadedFiles.handwriting.length > 0;
  };

  const getTotalFileCount = () => {
    return Object.values(uploadedFiles).flat().length;
  };

  const handleAnalysis = async () => {
    if (!hasRequiredFiles()) return;

    setIsAnalyzing(true);
    
    // Simulate analysis - replace with actual API call
    try {
      // For now, just use the handwriting analysis API as a demo
      if (uploadedFiles.handwriting.length > 0) {
        const formData = new FormData();
        formData.append('file', uploadedFiles.handwriting[0].file);
        formData.append('drawing_type', 'spiral');

        const response = await fetch('http://localhost:8000/api/v1/handwriting/demo/upload', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          console.log('Analysis result:', result);
          setAnalysisComplete(true);
        }
      }
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (analysisComplete) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-2xl mx-auto text-center p-8">
          <CheckCircleIcon className="h-16 w-16 text-green-500 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Analysis Complete!</h1>
          <p className="text-lg text-gray-600 mb-8">
            Your multimodal analysis has been processed successfully. In a real implementation, 
            this would show comprehensive results from all your uploaded data.
          </p>
          <div className="space-x-4">
            <Link to={state.isAuthenticated ? "/patient" : "/analysis"} className="btn-primary">
              {state.isAuthenticated ? "Back to Dashboard" : "Start New Analysis"}
            </Link>
            <Link to="/" className="btn-secondary">
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

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
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Comprehensive Multimodal Upload
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Upload all your medical data for integrated AI analysis. The more data you provide, 
            the more accurate your Parkinson's assessment will be.
          </p>
        </div>
      </div>

      {/* Upload Sections */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {dataTypes.map((dataType) => {
            const fileCount = uploadedFiles[dataType.id].length;
            const hasFiles = fileCount > 0;

            return (
              <div
                key={dataType.id}
                className={`p-6 rounded-xl border-2 ${getColorClasses(dataType.color)} transition-all duration-200`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center shadow-sm">
                      <dataType.icon className="h-5 w-5 text-gray-700" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 flex items-center">
                        {dataType.title}
                        {dataType.required && <span className="text-red-500 ml-1">*</span>}
                      </h3>
                      <p className="text-sm text-gray-600">{dataType.description}</p>
                    </div>
                  </div>
                  {hasFiles && (
                    <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                      {fileCount} file{fileCount > 1 ? 's' : ''}
                    </span>
                  )}
                </div>

                <div className="space-y-3">
                  <div>
                    <label className="block">
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-gray-400 transition-colors cursor-pointer">
                        <CloudArrowUpIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                        <span className="text-sm text-gray-600">
                          Click to upload or drag and drop
                        </span>
                        <p className="text-xs text-gray-500 mt-1">
                          {dataType.acceptedFormats}
                        </p>
                      </div>
                      <input
                        type="file"
                        className="hidden"
                        multiple={dataType.multiple}
                        accept={dataType.acceptedFormats}
                        onChange={(e) => handleFileUpload(dataType.id, e.target.files)}
                      />
                    </label>
                  </div>

                  {/* Display uploaded files */}
                  {uploadedFiles[dataType.id].length > 0 && (
                    <div className="space-y-2">
                      {uploadedFiles[dataType.id].map((uploadedFile, index) => (
                        <div key={index} className="flex items-center justify-between bg-white p-3 rounded-lg shadow-sm">
                          <div className="flex items-center space-x-3">
                            {uploadedFile.preview && (
                              <img src={uploadedFile.preview} alt="Preview" className="w-8 h-8 object-cover rounded" />
                            )}
                            <div>
                              <p className="text-sm font-medium text-gray-900 truncate max-w-xs">
                                {uploadedFile.file.name}
                              </p>
                              <p className="text-xs text-gray-500">
                                {(uploadedFile.file.size / 1024 / 1024).toFixed(2)} MB
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={() => removeFile(dataType.id, index)}
                            className="text-red-500 hover:text-red-700 text-sm"
                          >
                            Remove
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Analysis Section */}
        <div className="mt-8 bg-white rounded-xl p-8 shadow-sm">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Ready for Analysis?</h2>
            
            {!hasRequiredFiles() ? (
              <div className="flex items-center justify-center space-x-2 text-amber-600 mb-6">
                <ExclamationTriangleIcon className="h-5 w-5" />
                <span>Please upload at least one handwriting sample to continue</span>
              </div>
            ) : (
              <div className="mb-6">
                <p className="text-gray-600 mb-2">
                  {getTotalFileCount()} file{getTotalFileCount() > 1 ? 's' : ''} uploaded and ready for analysis
                </p>
                <div className="flex items-center justify-center space-x-2 text-green-600">
                  <CheckCircleIcon className="h-5 w-5" />
                  <span>All requirements met</span>
                </div>
              </div>
            )}

            <button
              onClick={handleAnalysis}
              disabled={!hasRequiredFiles() || isAnalyzing}
              className={`
                py-4 px-8 rounded-lg text-lg font-medium transition duration-200 ease-in-out
                ${hasRequiredFiles() && !isAnalyzing
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }
              `}
            >
              {isAnalyzing ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Analyzing...</span>
                </div>
              ) : (
                'Start Comprehensive Analysis'
              )}
            </button>

            <p className="text-sm text-gray-500 mt-4">
              Your data will be processed using our advanced multimodal AI models for comprehensive Parkinson's assessment.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}