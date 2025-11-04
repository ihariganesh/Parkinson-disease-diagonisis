import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  DocumentTextIcon,
  CloudArrowUpIcon,
  ChartBarIcon,
  HeartIcon,
  // CpuChipIcon, // removed with MRI cleanup
  MicrophoneIcon,
  PencilIcon,
  BeakerIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";
import { useAuth } from "../../contexts/AuthContext";
import { medicalService } from "../../services";
import { LoadingSpinner, Alert } from "../common";
import type { MedicalData, DiagnosisReport } from "../../types";

const dataTypeConfig = {
  handwriting: {
    icon: PencilIcon,
    title: "Handwriting",
    description: "Upload handwriting samples",
    color: "text-purple-600",
    bgColor: "bg-purple-50",
  },
  voice: {
    icon: MicrophoneIcon,
    title: "Voice Recording",
    description: "Upload voice recordings",
    color: "text-green-600",
    bgColor: "bg-green-50",
  },
  ecg: {
    icon: HeartIcon,
    title: "ECG Data",
    description: "Upload ECG readings",
    color: "text-red-600",
    bgColor: "bg-red-50",
  },
  // MRI removed during cleanup
  doctor_notes: {
    icon: DocumentTextIcon,
    title: "Doctor Notes",
    description: "Upload medical reports",
    color: "text-gray-600",
    bgColor: "bg-gray-50",
  },
};

export default function PatientDashboard() {
  const { state } = useAuth();
  const navigate = useNavigate();
  const [recentData, setRecentData] = useState<MedicalData[]>([]);
  const [recentReports, setRecentReports] = useState<DiagnosisReport[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const [dataResponse, reportsResponse] = await Promise.all([
        medicalService.getMedicalData(undefined, undefined, 1, 5),
        medicalService.getDiagnosisReports(undefined, 1, 3),
      ]);

      if (dataResponse.success && dataResponse.data) {
        setRecentData(dataResponse.data.items);
      }

      if (reportsResponse.success && reportsResponse.data) {
        setRecentReports(reportsResponse.data.items);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load dashboard data"
      );
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {state.user?.first_name}
        </h1>
        <p className="mt-2 text-gray-600">
          Monitor your health data and track your progress
        </p>
      </div>

      {error && (
        <Alert
          type="error"
          message={error}
          onClose={() => setError("")}
          className="mb-6"
        />
      )}

      {/* Comprehensive Analysis Section */}
      <div className="mb-8">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-8 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">
                Comprehensive AI Analysis
              </h2>
              <p className="text-blue-100 mb-4 max-w-2xl">
                Upload all your medical data at once for integrated multimodal analysis. 
                Our AI combines handwriting, voice, and medical reports to provide 
                accurate Parkinson's assessment and staging.
              </p>
              <button
                onClick={() => navigate("/multimodal-upload")}
                className="bg-white text-blue-600 hover:bg-gray-100 font-medium py-3 px-6 rounded-lg transition duration-200 ease-in-out inline-flex items-center"
              >
                <CloudArrowUpIcon className="h-5 w-5 mr-2" />
                Start Comprehensive Analysis
              </button>
            </div>
            <div className="hidden lg:block">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white bg-opacity-20 rounded-lg p-4 text-center">
                  <PencilIcon className="h-8 w-8 mx-auto mb-2" />
                  <span className="text-sm">Handwriting</span>
                </div>
                <div className="bg-white bg-opacity-20 rounded-lg p-4 text-center">
                  <MicrophoneIcon className="h-8 w-8 mx-auto mb-2" />
                  <span className="text-sm">Voice</span>
                </div>
                <div className="bg-white bg-opacity-20 rounded-lg p-4 text-center">
                  <DocumentTextIcon className="h-8 w-8 mx-auto mb-2" />
                  <span className="text-sm">Reports</span>
                </div>
                {/* MRI section removed during cleanup */}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Analysis Access */}
      <div className="mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Comprehensive & Individual Analysis Tools
            </h3>
            <p className="text-gray-600">
              Access our AI-powered analysis features for complete health assessment.
            </p>
          </div>
          
          {/* Comprehensive Analysis - Featured */}
          <div className="mb-6 p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border-2 border-indigo-300">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center mb-2">
                  <SparklesIcon className="h-6 w-6 text-indigo-600 mr-2" />
                  <h4 className="text-xl font-bold text-gray-900">Comprehensive Multi-Modal Analysis</h4>
                  <span className="ml-3 px-3 py-1 bg-indigo-600 text-white text-xs font-bold rounded-full">
                    RECOMMENDED
                  </span>
                </div>
                <p className="text-gray-700 mb-2">
                  Complete Parkinson's assessment combining DaT scan, handwriting, and voice analysis for maximum accuracy
                </p>
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <span className="flex items-center">
                    <BeakerIcon className="h-4 w-4 mr-1" />
                    DaT Scan (50%)
                  </span>
                  <span className="flex items-center">
                    <PencilIcon className="h-4 w-4 mr-1" />
                    Handwriting (25%)
                  </span>
                  <span className="flex items-center">
                    <MicrophoneIcon className="h-4 w-4 mr-1" />
                    Voice (25%)
                  </span>
                </div>
              </div>
              <button
                onClick={() => navigate("/comprehensive")}
                className="ml-6 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold py-3 px-6 rounded-lg transition duration-200 ease-in-out inline-flex items-center shadow-lg"
              >
                <SparklesIcon className="h-5 w-5 mr-2" />
                Start Comprehensive Analysis
              </button>
            </div>
          </div>
          
          {/* Individual Analysis Tools */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Individual Analysis Tools</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Handwriting Analysis */}
              <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg border border-purple-200">
                <div>
                  <h5 className="font-medium text-gray-900 mb-1">Handwriting Analysis</h5>
                  <p className="text-sm text-gray-600">Draw spirals to detect motor symptoms</p>
                </div>
                <button
                  onClick={() => navigate("/handwriting")}
                  className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200 ease-in-out inline-flex items-center"
                >
                  <PencilIcon className="h-4 w-4 mr-2" />
                  Analyze Now
                </button>
              </div>

              {/* Speech Analysis */}
              <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
                <div>
                  <h5 className="font-medium text-gray-900 mb-1">Speech Analysis</h5>
                  <p className="text-sm text-gray-600">Analyze voice patterns and biomarkers</p>
                </div>
                <button
                  onClick={() => navigate("/speech")}
                  className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200 ease-in-out inline-flex items-center"
                >
                  <MicrophoneIcon className="h-4 w-4 mr-2" />
                  Analyze Now
                </button>
              </div>

              {/* DaT Scan Analysis */}
              <div className="flex items-center justify-between p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                <div>
                  <h5 className="font-medium text-gray-900 mb-1">DaT Scan Analysis</h5>
                  <p className="text-sm text-gray-600">AI analysis of dopamine transporter scans</p>
                </div>
                <button
                  onClick={() => navigate("/dat")}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200 ease-in-out inline-flex items-center"
                >
                  <BeakerIcon className="h-4 w-4 mr-2" />
                  Analyze Now
                </button>
              </div>

              {/* MRI Analysis removed during cleanup */}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Uploads */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-xl font-semibold text-gray-900">
              Recent Uploads
            </h2>
          </div>
          <div className="space-y-4">
            {recentData.length === 0 ? (
              <div className="text-center py-8">
                <CloudArrowUpIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No data uploaded yet</p>
                <button
                  onClick={() => navigate("/multimodal-upload")}
                  className="btn-primary mt-4"
                >
                  Start Comprehensive Analysis
                </button>
              </div>
            ) : (
              recentData.map((data) => {
                const config =
                  dataTypeConfig[data.type as keyof typeof dataTypeConfig];
                const IconComponent = config?.icon || DocumentTextIcon;

                return (
                  <div
                    key={data.id}
                    className="flex items-center p-3 bg-gray-50 rounded-lg"
                  >
                    <div
                      className={`p-2 rounded-lg ${
                        config?.bgColor || "bg-gray-100"
                      }`}
                    >
                      <IconComponent
                        className={`h-5 w-5 ${
                          config?.color || "text-gray-600"
                        }`}
                      />
                    </div>
                    <div className="ml-3 flex-1">
                      <p className="text-sm font-medium text-gray-900">
                        {data.fileName}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(data.uploadedAt).toLocaleDateString()}
                      </p>
                    </div>
                    {data.analysisResult && (
                      <div className="ml-3">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Analyzed
                        </span>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Recent Reports */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-xl font-semibold text-gray-900">
              Recent Reports
            </h2>
          </div>
          <div className="space-y-4">
            {recentReports.length === 0 ? (
              <div className="text-center py-8">
                <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No reports generated yet</p>
                <p className="text-sm text-gray-400 mt-2">
                  Upload medical data to generate your first comprehensive analysis report
                </p>
              </div>
            ) : (
              recentReports.map((report) => (
                <div
                  key={report.id}
                  className="p-4 border border-gray-200 rounded-lg"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">
                        Diagnosis Report
                      </h3>
                      <p className="text-xs text-gray-500">
                        {new Date(report.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          report.finalDiagnosis === "healthy"
                            ? "bg-green-100 text-green-800"
                            : report.finalDiagnosis === "early_stage"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {report.finalDiagnosis.replace("_", " ")}
                      </span>
                      {report.doctorVerified && (
                        <p className="text-xs text-green-600 mt-1">
                          Doctor verified
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="flex justify-between text-sm">
                      <span>Confidence:</span>
                      <span className="font-medium">
                        {Math.round(report.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Health Tips */}
      <div className="mt-8">
        <div className="card">
          <div className="card-header">
            <h2 className="text-xl font-semibold text-gray-900">Health Tips</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <h3 className="font-medium text-blue-900 mb-2">
                Regular Monitoring
              </h3>
              <p className="text-sm text-blue-700">
                Upload your data regularly to track changes and get more
                accurate assessments.
              </p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <h3 className="font-medium text-green-900 mb-2">Stay Active</h3>
              <p className="text-sm text-green-700">
                Regular exercise can help improve motor symptoms and overall
                well-being.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
