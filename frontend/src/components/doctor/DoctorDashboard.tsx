import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  UserGroupIcon,
  ChartBarIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
  ChatBubbleLeftRightIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClipboardDocumentCheckIcon,
  DocumentTextIcon,
} from "@heroicons/react/24/outline";
import { CheckCircleIcon as CheckCircleSolid } from "@heroicons/react/24/solid";
import { useAuth } from "../../contexts/AuthContext";
import { LoadingSpinner, Alert } from "../common";
import axios from "axios";
import GenericMessaging from "../common/GenericMessaging";

interface Patient {
  id: string;
  patient_id?: string;
  first_name: string;
  last_name: string;
  email: string;
  date_of_birth?: string;
  phone_number?: string;
  created_at: string;
  diagnosis_status?: string;
}

interface DiagnosisReport {
  id: string;
  patient_id?: string;
  final_diagnosis: string;
  confidence: number;
  stage: number;
  multimodal_analysis?: any;
  fusion_score?: number;
  doctor_verified: boolean;
  doctor_notes?: string;
  created_at: string;
  updated_at?: string;
}

interface PatientDetails {
  patient: Patient;
  reports: DiagnosisReport[];
  latestRecommendations: any;
}

interface AnalyticsData {
  total_patients: number;
  total_reports: number;
  pending_reports: number;
  recent_uploads: number;
}

interface PendingReport extends DiagnosisReport {
  patient_name: string;
  patient_pid?: string;
}

interface PatientRequest {
  id: string;
  patient_id: string;
  patient_pid?: string;
  patient_name: string;
  patient_email: string;
  message?: string;
  requested_at: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const stageLabels: Record<number, { label: string; color: string; bg: string }> = {
  0: { label: "Healthy", color: "text-green-700", bg: "bg-green-100" },
  1: { label: "Early Stage", color: "text-yellow-700", bg: "bg-yellow-100" },
  2: { label: "Moderate", color: "text-orange-700", bg: "bg-orange-100" },
  3: { label: "Advanced", color: "text-red-700", bg: "bg-red-100" },
  4: { label: "Severe", color: "text-red-900", bg: "bg-red-200" },
};

const DoctorDashboard = () => {
  const { state } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const initialTab = location.hash
    ? (location.hash.replace("#", "") as "search" | "patients" | "analytics" | "pending" | "messages" | "requests")
    : "search";
  const [activeTab, setActiveTab] = useState<"search" | "patients" | "analytics" | "pending" | "messages" | "requests">(initialTab);

  useEffect(() => {
    if (location.hash) {
      const hashTab = location.hash.replace("#", "") as typeof activeTab;
      if (["search", "patients", "analytics", "pending", "messages", "requests"].includes(hashTab)) {
        setActiveTab(hashTab);
      }
    }
  }, [location.hash]);

  const handleTabChange = (tabId: typeof activeTab) => {
    setActiveTab(tabId);
    navigate(`/doctor/dashboard#${tabId}`, { replace: true });
  };

  // State
  const [patients, setPatients] = useState<Patient[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const [patientIdInput, setPatientIdInput] = useState("");
  const [searchedPatient, setSearchedPatient] = useState<PatientDetails | null>(null);
  const [searching, setSearching] = useState(false);

  const [patientsLoading, setPatientsLoading] = useState(false);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);

  const [pendingReports, setPendingReports] = useState<PendingReport[]>([]);
  const [pendingLoading, setPendingLoading] = useState(false);

  const [patientRequests, setPatientRequests] = useState<PatientRequest[]>([]);
  const [requestsLoading, setRequestsLoading] = useState(false);

  // Verify modal state
  const [verifyingReport, setVerifyingReport] = useState<DiagnosisReport | PendingReport | null>(null);
  const [verifyNotes, setVerifyNotes] = useState("");
  const [verifyLoading, setVerifyLoading] = useState(false);

  // Expanded report detail
  const [expandedReportId, setExpandedReportId] = useState<string | null>(null);

  useEffect(() => {
    if (activeTab === "patients" && patients.length === 0) fetchPatients();
    else if (activeTab === "analytics" && !analytics) fetchAnalytics();
    else if (activeTab === "pending" && pendingReports.length === 0) fetchPendingReports();
    else if (activeTab === "requests" && patientRequests.length === 0) fetchRequests();
  }, [activeTab]);

  const fetchPatients = async () => {
    setPatientsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/doctors/patients`, {
        headers: { Authorization: `Bearer ${state.token}` },
      });
      setPatients(response.data);
    } catch {
      setError("Failed to fetch patients.");
    } finally {
      setPatientsLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    setAnalyticsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/doctors/analytics`, {
        headers: { Authorization: `Bearer ${state.token}` },
      });
      setAnalytics(response.data);
    } catch {
      setError("Failed to fetch analytics.");
    } finally {
      setAnalyticsLoading(false);
    }
  };

  const fetchPendingReports = async () => {
    setPendingLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/doctors/reports/pending`, {
        headers: { Authorization: `Bearer ${state.token}` },
      });
      setPendingReports(response.data);
    } catch {
      setError("Failed to fetch pending reports.");
    } finally {
      setPendingLoading(false);
    }
  };

  const fetchRequests = async () => {
    setRequestsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/doctors/requests`, {
        headers: { Authorization: `Bearer ${state.token}` },
      });
      setPatientRequests(response.data);
    } catch {
      setError("Failed to fetch patient requests.");
    } finally {
      setRequestsLoading(false);
    }
  };

  const handleRequestAction = async (reqId: string, action: "approve" | "reject") => {
    try {
      await axios.post(`${API_BASE_URL}/doctors/requests/${reqId}/${action}`, {}, {
        headers: { Authorization: `Bearer ${state.token}` },
      });
      setSuccessMsg(`Patient request ${action}d successfully`);
      setPatientRequests((prev) => prev.filter((r) => r.id !== reqId));
      if (action === "approve") {
        fetchPatients(); // refresh patient list
      }
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch {
      setError(`Failed to ${action} request.`);
    }
  };

  const searchPatientById = async () => {
    if (!patientIdInput.trim()) {
      setError("Please enter a valid Patient ID");
      return;
    }
    setSearching(true);
    setError(null);
    setSearchedPatient(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/doctors/search-patient/${patientIdInput}`, {
        headers: { Authorization: `Bearer ${state.token}` },
      });
      const { patient, reports } = response.data;
      setSearchedPatient({ patient, reports, latestRecommendations: null });
    } catch (err: any) {
      if (err.response?.status === 404) setError("Patient not found. Please check the Patient ID.");
      else setError("Failed to fetch patient data.");
    } finally {
      setSearching(false);
    }
  };

  const handleVerifyReport = async (reportId: string) => {
    setVerifyLoading(true);
    try {
      await axios.post(
        `${API_BASE_URL}/doctors/reports/${reportId}/verify`,
        JSON.stringify(verifyNotes || null),
        {
          headers: {
            Authorization: `Bearer ${state.token}`,
            "Content-Type": "application/json",
          },
        }
      );
      setSuccessMsg("Report verified successfully!");
      setVerifyingReport(null);
      setVerifyNotes("");

      // Refresh data
      if (searchedPatient) {
        setSearchedPatient({
          ...searchedPatient,
          reports: searchedPatient.reports.map((r) =>
            r.id === reportId ? { ...r, doctor_verified: true, doctor_notes: verifyNotes } : r
          ),
        });
      }
      if (pendingReports.length > 0) {
        setPendingReports(pendingReports.filter((r) => r.id !== reportId));
      }
      // Refresh analytics
      if (analytics) {
        setAnalytics({ ...analytics, pending_reports: Math.max(0, analytics.pending_reports - 1) });
      }
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch {
      setError("Failed to verify report.");
    } finally {
      setVerifyLoading(false);
    }
  };

  const renderStage = (stage: number) => {
    const info = stageLabels[stage] || { label: `Stage ${stage}`, color: "text-gray-700", bg: "bg-gray-100" };
    return (
      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${info.color} ${info.bg}`}>
        {info.label}
      </span>
    );
  };

  /* ─── Report Card ─────────────────────────────────────────── */
  const ReportCard = ({
    report,
    patientLabel,
    showVerify = true,
  }: {
    report: DiagnosisReport | PendingReport;
    patientLabel?: string;
    showVerify?: boolean;
  }) => {
    const isExpanded = expandedReportId === report.id;
    return (
      <div
        className={`bg-white rounded-xl border transition-all duration-200 ${report.doctor_verified ? "border-green-200" : "border-amber-200"
          } hover:shadow-md`}
      >
        {/* Card Header */}
        <div
          className="p-5 cursor-pointer"
          onClick={() => setExpandedReportId(isExpanded ? null : report.id)}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {patientLabel && (
                <p className="text-sm text-gray-500 mb-1 font-medium">{patientLabel}</p>
              )}
              <div className="flex items-center gap-3 mb-2">
                <h4 className="text-lg font-bold text-gray-900 capitalize">
                  {report.final_diagnosis.replace(/_/g, " ")}
                </h4>
                {renderStage(report.stage)}
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>Confidence: <b className="text-gray-800">{(report.confidence * 100).toFixed(1)}%</b></span>
                {report.fusion_score !== undefined && (
                  <span>Fusion Score: <b className="text-gray-800">{(report.fusion_score * 100).toFixed(1)}%</b></span>
                )}
                <span>{new Date(report.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            {/* Verified badge */}
            <div className="flex items-center gap-2">
              {report.doctor_verified ? (
                <span className="flex items-center gap-1 px-3 py-1.5 bg-green-50 border border-green-200 text-green-700 rounded-full text-xs font-semibold">
                  <CheckCircleSolid className="h-4 w-4" /> Verified
                </span>
              ) : (
                <span className="flex items-center gap-1 px-3 py-1.5 bg-amber-50 border border-amber-200 text-amber-700 rounded-full text-xs font-semibold">
                  <ExclamationTriangleIcon className="h-4 w-4" /> Pending
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Expanded Details */}
        {isExpanded && (
          <div className="border-t border-gray-100 p-5 bg-gray-50/60 space-y-4 animate-fadeIn">
            {/* Multimodal Analysis */}
            {report.multimodal_analysis && Object.keys(report.multimodal_analysis).length > 0 && (
              <div>
                <h5 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                  <DocumentTextIcon className="h-5 w-5 text-blue-600" />
                  Multimodal Analysis
                </h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {Object.entries(report.multimodal_analysis).map(([key, value]: [string, any]) => (
                    <div key={key} className="bg-white p-3 rounded-lg border border-gray-200">
                      <div className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-1">
                        {key.replace(/_/g, " ")}
                      </div>
                      {typeof value === "object" ? (
                        <div className="text-sm text-gray-700 space-y-0.5">
                          {Object.entries(value).map(([k, v]) => (
                            <div key={k} className="flex justify-between">
                              <span className="capitalize text-gray-500">{k.replace(/_/g, " ")}</span>
                              <span className="font-medium">
                                {typeof v === "number" ? (v * 100).toFixed(1) + "%" : String(v)}
                              </span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-sm font-medium text-gray-700">
                          {typeof value === "number" ? (value * 100).toFixed(1) + "%" : String(value)}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Doctor Notes */}
            {report.doctor_notes && (
              <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                <h5 className="font-semibold text-blue-800 text-sm mb-1">Doctor's Notes</h5>
                <p className="text-blue-700 text-sm">{report.doctor_notes}</p>
              </div>
            )}

            {/* Verify Button */}
            {showVerify && !report.doctor_verified && (
              <div className="pt-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setVerifyingReport(report);
                    setVerifyNotes(report.doctor_notes || "");
                  }}
                  className="px-6 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium flex items-center gap-2"
                >
                  <CheckCircleIcon className="h-5 w-5" />
                  Verify This Report
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-3xl font-bold text-gray-900">Doctor Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Welcome back, Dr. {state.user?.first_name} {state.user?.last_name}
        </p>
      </div>

      {/* Alerts */}
      {error && (
        <div className="mb-4">
          <Alert type="error" message={error} onClose={() => setError(null)} />
        </div>
      )}
      {successMsg && (
        <div className="mb-4 bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg flex items-center gap-2">
          <CheckCircleSolid className="h-5 w-5 text-green-600" />
          {successMsg}
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex space-x-1 border-b border-gray-200 mb-6 mt-4 overflow-x-auto">
        {[
          { id: "search" as const, label: "Search Patient", icon: MagnifyingGlassIcon },
          { id: "requests" as const, label: "Patient Requests", icon: UserGroupIcon },
          { id: "pending" as const, label: "Pending Reports", icon: ClipboardDocumentCheckIcon },
          { id: "patients" as const, label: "My Patients", icon: UserGroupIcon },
          { id: "analytics" as const, label: "Analytics", icon: ChartBarIcon },
          { id: "messages" as const, label: "Messages", icon: ChatBubbleLeftRightIcon },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => {
              handleTabChange(tab.id);
              setError(null);
            }}
            className={`flex items-center gap-2 py-3 px-4 outline-none font-medium border-b-2 transition-colors whitespace-nowrap ${activeTab === tab.id
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
          >
            <tab.icon className="h-5 w-5" />
            {tab.label}
            {tab.id === "pending" && analytics && analytics.pending_reports > 0 && (
              <span className="ml-1 px-2 py-0.5 bg-amber-500 text-white text-xs rounded-full font-bold">
                {analytics.pending_reports}
              </span>
            )}
            {tab.id === "requests" && patientRequests.length > 0 && (
              <span className="ml-1 px-2 py-0.5 bg-blue-500 text-white text-xs rounded-full font-bold">
                {patientRequests.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="min-h-[500px]">
        {/* SEARCH TAB */}
        {activeTab === "search" && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Patient Search</h2>
              <div className="flex gap-4">
                <input
                  type="text"
                  placeholder="Enter Patient ID (e.g., PID-123456 or UUID)..."
                  value={patientIdInput}
                  onChange={(e) => setPatientIdInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && searchPatientById()}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={searchPatientById}
                  disabled={searching || !patientIdInput.trim()}
                  className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {searching ? <LoadingSpinner size="sm" /> : <MagnifyingGlassIcon className="h-5 w-5" />}
                  Search
                </button>
              </div>
            </div>

            {searchedPatient && (
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 animate-fade-in">
                <div className="flex justify-between items-start mb-6 border-b pb-4">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">
                      {searchedPatient.patient.first_name} {searchedPatient.patient.last_name}
                    </h3>
                    <p className="text-gray-500">
                      ID: {searchedPatient.patient.patient_id || searchedPatient.patient.id}
                    </p>
                    <p className="text-gray-500 text-sm">{searchedPatient.patient.email}</p>
                  </div>
                  <button
                    onClick={() => setSearchedPatient(null)}
                    className="p-2 text-gray-400 hover:bg-gray-100 rounded-full"
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>

                <h4 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <DocumentTextIcon className="h-5 w-5 text-blue-600" />
                  Diagnosis Reports ({searchedPatient.reports.length})
                </h4>

                {searchedPatient.reports.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No reports found for this patient.</p>
                ) : (
                  <div className="space-y-4">
                    {searchedPatient.reports.map((rep) => (
                      <ReportCard key={rep.id} report={rep} />
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* PENDING REPORTS TAB */}
        {activeTab === "pending" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <ClipboardDocumentCheckIcon className="h-6 w-6 text-amber-500" />
                Reports Awaiting Verification
              </h2>
              <button
                onClick={fetchPendingReports}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium"
              >
                Refresh
              </button>
            </div>

            {pendingLoading ? (
              <div className="flex justify-center py-16">
                <LoadingSpinner />
              </div>
            ) : pendingReports.length === 0 ? (
              <div className="bg-white p-12 rounded-xl border border-gray-100 text-center">
                <CheckCircleSolid className="h-16 w-16 text-green-400 mx-auto mb-4" />
                <p className="text-xl font-semibold text-gray-700">All caught up!</p>
                <p className="text-gray-500 mt-1">No pending reports to verify.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {pendingReports.map((rep) => (
                  <ReportCard
                    key={rep.id}
                    report={rep}
                    patientLabel={`Patient: ${rep.patient_name}${rep.patient_pid ? ` (${rep.patient_pid})` : ""}`}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* PATIENT REQUESTS TAB */}
        {activeTab === "requests" && (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-semibold mb-6">Patient Connection Requests</h2>
            {requestsLoading ? (
              <div className="flex justify-center py-10">
                <LoadingSpinner />
              </div>
            ) : patientRequests.length === 0 ? (
              <p className="text-gray-500 text-center py-10">No pending requests.</p>
            ) : (
              <div className="space-y-4">
                {patientRequests.map((req) => (
                  <div key={req.id} className="p-5 border rounded-xl flex items-center justify-between shadow-sm">
                    <div>
                      <h3 className="font-bold text-lg text-gray-900">{req.patient_name}</h3>
                      <p className="text-sm text-gray-500">{req.patient_email} {req.patient_pid ? `• ID: ${req.patient_pid}` : ""}</p>
                      {req.message && (
                        <p className="text-sm text-gray-700 italic mt-2">"{req.message}"</p>
                      )}
                      <p className="text-xs text-gray-400 mt-1">Requested at {new Date(req.requested_at).toLocaleDateString()}</p>
                    </div>
                    <div className="flex gap-3">
                      <button
                        onClick={() => handleRequestAction(req.id, "reject")}
                        className="px-4 py-2 border border-red-200 text-red-600 rounded-lg hover:bg-red-50"
                      >
                        Reject
                      </button>
                      <button
                        onClick={() => handleRequestAction(req.id, "approve")}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                      >
                        Accept
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* PATIENTS TAB */}
        {activeTab === "patients" && (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-semibold mb-6">Patient Roster</h2>
            {patientsLoading ? (
              <div className="flex justify-center py-10">
                <LoadingSpinner />
              </div>
            ) : patients.length === 0 ? (
              <p className="text-gray-500 text-center py-10">No patients found.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-gray-50 text-gray-500 border-b">
                      <th className="p-4 font-medium rounded-tl-lg">Name</th>
                      <th className="p-4 font-medium">Email</th>
                      <th className="p-4 font-medium">Joined</th>
                      <th className="p-4 font-medium text-right rounded-tr-lg">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {patients.map((p) => (
                      <tr key={p.id} className="border-b hover:bg-blue-50/50 transition">
                        <td className="p-4 font-medium text-gray-900">
                          {p.first_name} {p.last_name}
                        </td>
                        <td className="p-4 text-gray-600">{p.email}</td>
                        <td className="p-4 text-gray-600">{new Date(p.created_at).toLocaleDateString()}</td>
                        <td className="p-4 text-right">
                          <button
                            onClick={() => {
                              setPatientIdInput(p.patient_id || p.id);
                              handleTabChange("search");
                              // Search immediately after state updates
                              setTimeout(async () => {
                                setSearching(true);
                                try {
                                  const response = await axios.get(
                                    `${API_BASE_URL}/doctors/search-patient/${p.patient_id || p.id}`,
                                    { headers: { Authorization: `Bearer ${state.token}` } }
                                  );
                                  const { patient, reports } = response.data;
                                  setSearchedPatient({ patient, reports, latestRecommendations: null });
                                } catch {
                                  setError("Failed to fetch patient.");
                                } finally {
                                  setSearching(false);
                                }
                              }, 100);
                            }}
                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          >
                            View Reports
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* ANALYTICS TAB */}
        {activeTab === "analytics" && (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-semibold mb-6">Dashboard Analytics</h2>
            {analyticsLoading ? (
              <div className="flex justify-center py-10">
                <LoadingSpinner />
              </div>
            ) : analytics ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border border-blue-200">
                  <div className="text-blue-800 text-sm font-bold uppercase tracking-wider mb-2">Total Patients</div>
                  <div className="text-4xl text-blue-900 font-extrabold">{analytics.total_patients}</div>
                </div>
                <div className="p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-xl border border-green-200">
                  <div className="text-green-800 text-sm font-bold uppercase tracking-wider mb-2">Total Reports</div>
                  <div className="text-4xl text-green-900 font-extrabold">{analytics.total_reports}</div>
                </div>
                <div className="p-6 bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-xl border border-yellow-200">
                  <div className="text-yellow-800 text-sm font-bold uppercase tracking-wider mb-2">Pending Reports</div>
                  <div className="text-4xl text-yellow-900 font-extrabold">{analytics.pending_reports}</div>
                </div>
                <div className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl border border-purple-200">
                  <div className="text-purple-800 text-sm font-bold uppercase tracking-wider mb-2">Recent Uploads</div>
                  <div className="text-4xl text-purple-900 font-extrabold">{analytics.recent_uploads}</div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">Failed to load analytics.</p>
            )}
          </div>
        )}

        {/* MESSAGES TAB */}
        {activeTab === "messages" && <GenericMessaging />}
      </div>

      {/* ─── Verify Modal ───────────────────────────────────────── */}
      {verifyingReport && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden">
            <div className="bg-green-600 text-white px-6 py-4">
              <h3 className="text-lg font-bold flex items-center gap-2">
                <CheckCircleIcon className="h-6 w-6" />
                Verify Diagnosis Report
              </h3>
              <p className="text-green-100 text-sm mt-1">
                {verifyingReport.final_diagnosis.replace(/_/g, " ").toUpperCase()} — Stage {verifyingReport.stage}
              </p>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Confidence</span>
                  <p className="font-semibold text-gray-800">{(verifyingReport.confidence * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <span className="text-gray-500">Date</span>
                  <p className="font-semibold text-gray-800">
                    {new Date(verifyingReport.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Doctor's Notes (optional)
                </label>
                <textarea
                  value={verifyNotes}
                  onChange={(e) => setVerifyNotes(e.target.value)}
                  placeholder="Add your clinical observations, notes, or recommendations..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 resize-none"
                  rows={4}
                />
              </div>

              <div className="flex gap-3 justify-end pt-2">
                <button
                  onClick={() => {
                    setVerifyingReport(null);
                    setVerifyNotes("");
                  }}
                  className="px-5 py-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleVerifyReport(verifyingReport.id)}
                  disabled={verifyLoading}
                  className="px-6 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium flex items-center gap-2"
                >
                  {verifyLoading ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    <CheckCircleSolid className="h-5 w-5" />
                  )}
                  Confirm Verification
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DoctorDashboard;