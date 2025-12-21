import { useState, useEffect } from "react";
import {
  UserGroupIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ClipboardDocumentListIcon,
  MagnifyingGlassIcon,
  EyeIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import { useAuth } from "../../contexts/AuthContext";
import { LoadingSpinner, Alert } from "../common";
import axios from "axios";

interface Patient {
  id: string;
  patient_id?: string;
  first_name: string;
  last_name: string;
  email: string;
  date_of_birth?: string;
  phone_number?: string;
  address_street?: string;
  address_city?: string;
  address_state?: string;
  gender?: string;
  created_at: string;
  diagnosis_status?: "healthy" | "early_stage" | "moderate_stage" | "advanced_stage";
  last_analysis?: string;
}

interface DiagnosisReport {
  id: string;
  patient_id?: string;
  patient_name?: string;
  final_diagnosis: string;
  confidence: number;
  stage: number;
  multimodal_analysis?: any;
  fusion_score: number;
  doctor_verified: boolean;
  doctor_notes?: string;
  lifestyle_recommendations?: any;
  created_at: string;
  updated_at?: string;
}

interface PatientDetails {
  patient: Patient;
  reports: DiagnosisReport[];
  latestRecommendations: any;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const DoctorDashboard = () => {
  const { state } = useAuth();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [reports, setReports] = useState<DiagnosisReport[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"search" | "reports" | "analytics">("search");
  const [searchTerm, setSearchTerm] = useState("");
  const [patientIdInput, setPatientIdInput] = useState("");
  const [searchedPatient, setSearchedPatient] = useState<PatientDetails | null>(null);
  const [searching, setSearching] = useState(false);

  // Search for patient by ID
  const searchPatientById = async () => {
    if (!patientIdInput.trim()) {
      setError("Please enter a valid Patient ID");
      return;
    }

    setSearching(true);
    setError(null);
    setSearchedPatient(null);

    try {
      const token = state.token;
      
      // Search patient by patient_id (PID-XXXXXX)
      const response = await axios.get(
        `${API_BASE_URL}/doctors/search-patient/${patientIdInput}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      const { patient, reports } = response.data;

      // Get latest recommendations from the most recent report
      let latestRecommendations = null;
      if (reports.length > 0) {
        const sortedReports = reports.sort((a: any, b: any) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        latestRecommendations = sortedReports[0].lifestyle_recommendations;
      }

      setSearchedPatient({
        patient: patient,
        reports: reports,
        latestRecommendations
      });
    } catch (err: any) {
      console.error("Error searching patient:", err);
      if (err.response?.status === 404) {
        setError("Patient not found. Please check the Patient ID.");
      } else if (err.response?.status === 403) {
        setError("You don't have permission to access this patient's data.");
      } else {
        setError("Failed to fetch patient data. Please try again.");
      }
    } finally {
      setSearching(false);
    }
  };

  const clearSearch = () => {
    setSearchedPatient(null);
    setPatientIdInput("");
    setError(null);
  };

  const filteredPatients = patients.filter(
    (patient) =>
      patient.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "text-green-600 bg-green-50";
      case "early_stage":
        return "text-yellow-600 bg-yellow-50";
      case "moderate_stage":
        return "text-orange-600 bg-orange-50";
      case "advanced_stage":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const getReportStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "text-yellow-600 bg-yellow-50";
      case "completed":
        return "text-blue-600 bg-blue-50";
      case "reviewed":
        return "text-green-600 bg-green-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-96">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Doctor Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Welcome back, Dr. {state.user?.first_name} {state.user?.last_name}
        </p>
      </div>

      {error && <Alert type="error" message={error} className="mb-6" />}

      {/* Patient ID Search Section */}
      <div className="mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Search Patient by ID</h2>
          <div className="flex gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Enter Patient ID..."
                value={patientIdInput}
                onChange={(e) => setPatientIdInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && searchPatientById()}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              />
            </div>
            <button
              onClick={searchPatientById}
              disabled={searching || !patientIdInput.trim()}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
            >
              {searching ? (
                <>
                  <LoadingSpinner />
                  Searching...
                </>
              ) : (
                <>
                  <MagnifyingGlassIcon className="h-5 w-5" />
                  Search
                </>
              )}
            </button>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            💡 Tip: Enter the patient's unique ID to access their medical reports and AI recommendations
          </p>
        </div>
      </div>

      {/* Patient Details Section */}
      {searchedPatient && (
        <div className="space-y-6">
          {/* Patient Info Card */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center">
                  <UserGroupIcon className="h-8 w-8 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">
                    {searchedPatient.patient.first_name} {searchedPatient.patient.last_name}
                  </h3>
                  <p className="text-gray-600">Patient ID: {searchedPatient.patient.patient_id || searchedPatient.patient.id}</p>
                </div>
              </div>
              <button
                onClick={clearSearch}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-medium text-gray-900">{searchedPatient.patient.email}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Age</p>
                <p className="font-medium text-gray-900">
                  {searchedPatient.patient.date_of_birth 
                    ? new Date().getFullYear() - new Date(searchedPatient.patient.date_of_birth).getFullYear()
                    : "N/A"}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Phone</p>
                <p className="font-medium text-gray-900">{searchedPatient.patient.phone_number || "N/A"}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Registration Date</p>
                <p className="font-medium text-gray-900">
                  {new Date(searchedPatient.patient.created_at).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Reports</p>
                <p className="font-medium text-gray-900">{searchedPatient.reports.length}</p>
              </div>
            </div>
          </div>

          {/* AI Lifestyle Recommendations */}
          {searchedPatient.latestRecommendations && (
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
              <h3 className="text-xl font-bold text-gray-900 mb-4">🤖 AI Lifestyle Recommendations</h3>
              <div className="space-y-4">
                {searchedPatient.latestRecommendations.exercise && (
                  <div className="bg-white p-4 rounded-lg">
                    <h4 className="font-semibold text-red-600 mb-2">❤️ Exercise</h4>
                    <p className="text-gray-700">{searchedPatient.latestRecommendations.exercise}</p>
                  </div>
                )}
                {searchedPatient.latestRecommendations.diet && (
                  <div className="bg-white p-4 rounded-lg">
                    <h4 className="font-semibold text-green-600 mb-2">🍎 Diet & Nutrition</h4>
                    <p className="text-gray-700">{searchedPatient.latestRecommendations.diet}</p>
                  </div>
                )}
                {searchedPatient.latestRecommendations.sleep && (
                  <div className="bg-white p-4 rounded-lg">
                    <h4 className="font-semibold text-purple-600 mb-2">😴 Sleep & Rest</h4>
                    <p className="text-gray-700">{searchedPatient.latestRecommendations.sleep}</p>
                  </div>
                )}
                {searchedPatient.latestRecommendations.stress_management && (
                  <div className="bg-white p-4 rounded-lg">
                    <h4 className="font-semibold text-blue-600 mb-2">🧘 Stress Management</h4>
                    <p className="text-gray-700">{searchedPatient.latestRecommendations.stress_management}</p>
                  </div>
                )}
                {searchedPatient.latestRecommendations.medical_followup && (
                  <div className="bg-white p-4 rounded-lg">
                    <h4 className="font-semibold text-orange-600 mb-2">🏥 Medical Follow-up</h4>
                    <p className="text-gray-700">{searchedPatient.latestRecommendations.medical_followup}</p>
                  </div>
                )}
              </div>
              <p className="text-sm text-gray-600 mt-4 italic">
                ⚠️ Note: These are AI-generated recommendations. Please use your clinical judgment and consider the patient's complete medical history.
              </p>
            </div>
          )}

          {/* Diagnosis Reports */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              📊 Diagnosis Reports ({searchedPatient.reports.length})
            </h3>
            {searchedPatient.reports.length === 0 ? (
              <p className="text-gray-600 text-center py-8">No diagnosis reports available yet.</p>
            ) : (
              <div className="space-y-4">
                {searchedPatient.reports
                  .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                  .map((report) => (
                    <div key={report.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(report.final_diagnosis)}`}>
                              {report.final_diagnosis.replace("_", " ").toUpperCase()}
                            </span>
                            <span className="text-gray-600">
                              Confidence: <span className="font-semibold">{(report.confidence * 100).toFixed(1)}%</span>
                            </span>
                            <span className="text-gray-600">
                              Stage: <span className="font-semibold">{report.stage}</span>
                            </span>
                          </div>
                          <p className="text-gray-900 mb-2">
                            {report.doctor_verified ? "✅ Verified" : "⏳ Pending Verification"}
                            {report.doctor_notes && ` - ${report.doctor_notes}`}
                          </p>
                          <p className="text-sm text-gray-500">
                            📅 {new Date(report.created_at).toLocaleDateString()} at {new Date(report.created_at).toLocaleTimeString()}
                          </p>
                        </div>
                        <button className="text-blue-600 hover:text-blue-800 font-medium">
                          View Details →
                        </button>
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!searchedPatient && !searching && (
        <div className="bg-white p-12 rounded-lg shadow-sm border text-center">
          <MagnifyingGlassIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Search for a Patient</h3>
          <p className="text-gray-600 mb-6">
            Enter a patient's ID above to view their medical reports and AI-generated lifestyle recommendations.
          </p>
          <div className="bg-blue-50 p-4 rounded-lg max-w-2xl mx-auto">
            <p className="text-sm text-blue-800 font-medium mb-2">💡 Quick Tips:</p>
            <ul className="text-sm text-blue-700 text-left space-y-1">
              <li>• Patient IDs are unique identifiers assigned to each patient</li>
              <li>• You can view all diagnosis reports and their analysis history</li>
              <li>• AI recommendations are based on the latest diagnosis report</li>
              <li>• Use this information to provide better care and follow-up</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default DoctorDashboard;