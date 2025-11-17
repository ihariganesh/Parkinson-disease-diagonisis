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

      {/* Main Comprehensive Analysis Section */}
      <div className="mb-8">
        <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 rounded-2xl p-10 text-white shadow-2xl">
          <div className="grid lg:grid-cols-2 gap-8 items-center">
            {/* Left Side - CTA */}
            <div>
              <div className="flex items-center mb-4">
                <SparklesIcon className="h-10 w-10 mr-3" />
                <h2 className="text-3xl font-bold">
                  Comprehensive AI Analysis
                </h2>
              </div>
              <p className="text-blue-100 mb-6 text-lg leading-relaxed">
                Upload all your medical data at once for integrated multimodal analysis. 
                Our AI combines <strong>handwriting, voice, and medical reports</strong> to provide 
                accurate Parkinson's assessment and staging with AI-powered lifestyle recommendations.
              </p>
              <div className="space-y-3 mb-6">
                <div className="flex items-center space-x-3">
                  <div className="bg-white bg-opacity-20 rounded-full p-2">
                    <BeakerIcon className="h-5 w-5" />
                  </div>
                  <span className="text-white">DaT Scan Analysis</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="bg-white bg-opacity-20 rounded-full p-2">
                    <PencilIcon className="h-5 w-5" />
                  </div>
                  <span className="text-white">Handwriting Pattern Detection</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="bg-white bg-opacity-20 rounded-full p-2">
                    <MicrophoneIcon className="h-5 w-5" />
                  </div>
                  <span className="text-white">Voice Biomarker Analysis</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="bg-white bg-opacity-20 rounded-full p-2">
                    <DocumentTextIcon className="h-5 w-5" />
                  </div>
                  <span className="text-white">AI-Powered Report & Recommendations</span>
                </div>
              </div>
              <button
                onClick={() => navigate("/comprehensive")}
                className="bg-white text-indigo-700 hover:bg-gray-100 font-bold py-4 px-8 rounded-xl transition duration-200 ease-in-out inline-flex items-center shadow-xl text-lg"
              >
                <CloudArrowUpIcon className="h-6 w-6 mr-3" />
                Start Comprehensive Analysis
              </button>
            </div>
            
            {/* Right Side - Visual Grid */}
            <div className="hidden lg:block">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-6 text-center transform hover:scale-105 transition-transform">
                  <PencilIcon className="h-12 w-12 mx-auto mb-3" />
                  <span className="text-base font-medium">Handwriting</span>
                  <p className="text-xs text-blue-100 mt-2">25% Weight</p>
                </div>
                <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-6 text-center transform hover:scale-105 transition-transform">
                  <MicrophoneIcon className="h-12 w-12 mx-auto mb-3" />
                  <span className="text-base font-medium">Voice</span>
                  <p className="text-xs text-blue-100 mt-2">25% Weight</p>
                </div>
                <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-6 text-center transform hover:scale-105 transition-transform col-span-2">
                  <DocumentTextIcon className="h-12 w-12 mx-auto mb-3" />
                  <span className="text-base font-medium">Reports</span>
                  <p className="text-xs text-blue-100 mt-2">Complete Diagnosis & AI Recommendations</p>
                </div>
              </div>
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
                  onClick={() => navigate("/comprehensive")}
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
