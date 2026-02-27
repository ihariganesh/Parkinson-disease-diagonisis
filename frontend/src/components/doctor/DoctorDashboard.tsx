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
  HomeIcon,
  CalendarIcon,
  CreditCardIcon,
  UserCircleIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  BellIcon,
  PhoneIcon,
  Bars3Icon,
} from "@heroicons/react/24/outline";
import { CheckCircleIcon as CheckCircleSolid, StarIcon } from "@heroicons/react/24/solid";
import { useAuth } from "../../contexts/AuthContext";
import { LoadingSpinner, Alert } from "../common";
import axios from "axios";
import GenericMessaging from "../common/GenericMessaging";
import DoctorAppointments from "./DoctorAppointments";

/* ─── Types ─────────────────────────────────────────────── */
interface Patient {
  id: string; patient_id?: string; first_name: string; last_name: string;
  email: string; date_of_birth?: string; phone_number?: string;
  created_at: string; diagnosis_status?: string;
}
interface DiagnosisReport {
  id: string; patient_id?: string; final_diagnosis: string; confidence: number;
  stage: number; multimodal_analysis?: any; fusion_score?: number;
  doctor_verified: boolean; doctor_notes?: string; created_at: string; updated_at?: string;
}
interface PatientDetails { patient: Patient; reports: DiagnosisReport[]; latestRecommendations: any; }
interface AnalyticsData { total_patients: number; total_reports: number; pending_reports: number; recent_uploads: number; }
interface PendingReport extends DiagnosisReport { patient_name: string; patient_pid?: string; }
interface PatientRequest {
  id: string; patient_id: string; patient_pid?: string; patient_name: string;
  patient_email: string; message?: string; requested_at: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const stageLabels: Record<number, { label: string; color: string; bg: string }> = {
  0: { label: "Healthy", color: "text-green-700", bg: "bg-green-100" },
  1: { label: "Early Stage", color: "text-yellow-700", bg: "bg-yellow-100" },
  2: { label: "Moderate", color: "text-orange-700", bg: "bg-orange-100" },
  3: { label: "Advanced", color: "text-red-700", bg: "bg-red-100" },
  4: { label: "Severe", color: "text-red-900", bg: "bg-red-200" },
};

/* ─── Donut Chart ────────────────────────────────────────── */
function DonutChart({ total, pending, recent }: { total: number; pending: number; recent: number }) {
  const healthy = Math.max(0, total - pending);
  const sum = total || 1;
  const r = 54; const cx = 70; const cy = 70; const stroke = 14;
  const circ = 2 * Math.PI * r;
  const pct1 = (healthy / sum) * circ;
  const pct2 = (pending / sum) * circ;
  const pct3 = (recent / sum) * circ;
  const offset2 = circ - pct1;
  const offset3 = circ - pct1 - pct2;
  return (
    <div className="flex flex-col items-center gap-4">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#e0e7ff" strokeWidth={stroke} />
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#6366f1" strokeWidth={stroke}
          strokeDasharray={`${pct1} ${circ - pct1}`} strokeDashoffset={circ / 4} strokeLinecap="round" />
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#f59e0b" strokeWidth={stroke}
          strokeDasharray={`${pct2} ${circ - pct2}`} strokeDashoffset={circ / 4 - pct1} strokeLinecap="round" />
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#10b981" strokeWidth={stroke}
          strokeDasharray={`${pct3} ${circ - pct3}`} strokeDashoffset={circ / 4 - pct1 - pct2} strokeLinecap="round" />
        <text x={cx} y={cy - 6} textAnchor="middle" fontSize="22" fontWeight="bold" fill="#1e3a5f">{total}</text>
        <text x={cx} y={cy + 14} textAnchor="middle" fontSize="10" fill="#64748b">Patients</text>
      </svg>
      <div className="flex gap-4 text-xs">
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-indigo-500 inline-block" />Healthy ({healthy})</span>
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" />Pending ({pending})</span>
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />New ({recent})</span>
      </div>
    </div>
  );
}

/* ─── Mini Calendar ──────────────────────────────────────── */
function MiniCalendar() {
  const today = new Date();
  const [current, setCurrent] = useState(new Date(today.getFullYear(), today.getMonth(), 1));
  const year = current.getFullYear(); const month = current.getMonth();
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const days: (number | null)[] = Array(firstDay).fill(null);
  for (let d = 1; d <= daysInMonth; d++) days.push(d);
  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
      <div className="flex items-center justify-between mb-4">
        <button onClick={() => setCurrent(new Date(year, month - 1, 1))} className="text-gray-400 hover:text-indigo-600 transition">&#8249;</button>
        <h3 className="font-semibold text-gray-800 text-sm">{monthNames[month]} {year}</h3>
        <button onClick={() => setCurrent(new Date(year, month + 1, 1))} className="text-gray-400 hover:text-indigo-600 transition">&#8250;</button>
      </div>
      <div className="grid grid-cols-7 text-center text-xs text-gray-400 mb-2">
        {["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"].map(d => <div key={d}>{d}</div>)}
      </div>
      <div className="grid grid-cols-7 text-center text-sm gap-y-1">
        {days.map((d, i) => (
          <div key={i} className={`py-1 rounded-full cursor-pointer transition text-xs
            ${d === today.getDate() && month === today.getMonth() && year === today.getFullYear()
              ? "bg-indigo-600 text-white font-bold" : d ? "text-gray-700 hover:bg-indigo-50" : ""}`}>
            {d || ""}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── Review Bar ─────────────────────────────────────────── */
function ReviewBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-3 text-sm">
      <span className="w-20 text-gray-500 text-xs shrink-0">{label}</span>
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${value}%`, transition: "width 1s" }} />
      </div>
      <span className="text-gray-600 font-medium text-xs w-8 text-right">{value}%</span>
    </div>
  );
}

/* ─── Component ──────────────────────────────────────────── */
const DoctorDashboard = () => {
  const { state, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const initialTab = location.hash
    ? (location.hash.replace("#", "") as any) : "dashboard";
  const [activeTab, setActiveTab] = useState<"dashboard" | "search" | "patients" | "analytics" | "pending" | "messages" | "requests" | "appointments">(initialTab);

  useEffect(() => {
    if (location.hash) {
      const h = location.hash.replace("#", "") as typeof activeTab;
      if (["dashboard", "search", "patients", "analytics", "pending", "messages", "requests", "appointments"].includes(h)) setActiveTab(h);
    }
  }, [location.hash]);

  const handleTabChange = (tabId: typeof activeTab) => {
    setActiveTab(tabId);
    navigate(`/doctor/dashboard#${tabId}`, { replace: true });
  };

  /* State */
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
  const [verifyingReport, setVerifyingReport] = useState<DiagnosisReport | PendingReport | null>(null);
  const [verifyNotes, setVerifyNotes] = useState("");
  const [verifyLoading, setVerifyLoading] = useState(false);
  const [expandedReportId, setExpandedReportId] = useState<string | null>(null);

  useEffect(() => {
    if (activeTab === "patients" && patients.length === 0) fetchPatients();
    else if (activeTab === "analytics" && !analytics) fetchAnalytics();
    else if (activeTab === "dashboard" && !analytics) fetchAnalytics();
    else if (activeTab === "pending" && pendingReports.length === 0) fetchPendingReports();
    else if (activeTab === "requests" && patientRequests.length === 0) fetchRequests();
  }, [activeTab]);

  const fetchPatients = async () => {
    setPatientsLoading(true);
    try { const r = await axios.get(`${API_BASE_URL}/doctors/patients`, { headers: { Authorization: `Bearer ${state.token}` } }); setPatients(r.data); }
    catch { setError("Failed to fetch patients."); } finally { setPatientsLoading(false); }
  };
  const fetchAnalytics = async () => {
    setAnalyticsLoading(true);
    try { const r = await axios.get(`${API_BASE_URL}/doctors/analytics`, { headers: { Authorization: `Bearer ${state.token}` } }); setAnalytics(r.data); }
    catch { setError("Failed to fetch analytics."); } finally { setAnalyticsLoading(false); }
  };
  const fetchPendingReports = async () => {
    setPendingLoading(true);
    try { const r = await axios.get(`${API_BASE_URL}/doctors/reports/pending`, { headers: { Authorization: `Bearer ${state.token}` } }); setPendingReports(r.data); }
    catch { setError("Failed to fetch pending reports."); } finally { setPendingLoading(false); }
  };
  const fetchRequests = async () => {
    setRequestsLoading(true);
    try { const r = await axios.get(`${API_BASE_URL}/doctors/requests`, { headers: { Authorization: `Bearer ${state.token}` } }); setPatientRequests(r.data); }
    catch { setError("Failed to fetch patient requests."); } finally { setRequestsLoading(false); }
  };
  const handleRequestAction = async (reqId: string, action: "approve" | "reject") => {
    try {
      await axios.post(`${API_BASE_URL}/doctors/requests/${reqId}/${action}`, {}, { headers: { Authorization: `Bearer ${state.token}` } });
      setSuccessMsg(`Patient request ${action}d successfully`);
      setPatientRequests(prev => prev.filter(r => r.id !== reqId));
      if (action === "approve") fetchPatients();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch { setError(`Failed to ${action} request.`); }
  };
  const searchPatientById = async () => {
    if (!patientIdInput.trim()) { setError("Please enter a valid Patient ID"); return; }
    setSearching(true); setError(null); setSearchedPatient(null);
    try {
      const r = await axios.get(`${API_BASE_URL}/doctors/search-patient/${patientIdInput}`, { headers: { Authorization: `Bearer ${state.token}` } });
      setSearchedPatient({ patient: r.data.patient, reports: r.data.reports, latestRecommendations: null });
    } catch (err: any) {
      setError(err.response?.status === 404 ? "Patient not found." : "Failed to fetch patient data.");
    } finally { setSearching(false); }
  };
  const handleVerifyReport = async (reportId: string) => {
    setVerifyLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/doctors/reports/${reportId}/verify`, JSON.stringify(verifyNotes || null), {
        headers: { Authorization: `Bearer ${state.token}`, "Content-Type": "application/json" }
      });
      setSuccessMsg("Report verified successfully!");
      setVerifyingReport(null); setVerifyNotes("");
      if (searchedPatient) setSearchedPatient({ ...searchedPatient, reports: searchedPatient.reports.map(r => r.id === reportId ? { ...r, doctor_verified: true, doctor_notes: verifyNotes } : r) });
      if (pendingReports.length > 0) setPendingReports(pendingReports.filter(r => r.id !== reportId));
      if (analytics) setAnalytics({ ...analytics, pending_reports: Math.max(0, analytics.pending_reports - 1) });
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch { setError("Failed to verify report."); } finally { setVerifyLoading(false); }
  };

  const renderStage = (stage: number) => {
    const info = stageLabels[stage] || { label: `Stage ${stage}`, color: "text-gray-700", bg: "bg-gray-100" };
    return <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${info.color} ${info.bg}`}>{info.label}</span>;
  };

  const ReportCard = ({ report, patientLabel, showVerify = true }: { report: DiagnosisReport | PendingReport; patientLabel?: string; showVerify?: boolean }) => {
    const isExpanded = expandedReportId === report.id;
    return (
      <div className={`bg-white rounded-xl border transition-all duration-200 ${report.doctor_verified ? "border-green-200" : "border-amber-200"} hover:shadow-md`}>
        <div className="p-5 cursor-pointer" onClick={() => setExpandedReportId(isExpanded ? null : report.id)}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {patientLabel && <p className="text-sm text-gray-500 mb-1 font-medium">{patientLabel}</p>}
              <div className="flex items-center gap-3 mb-2">
                <h4 className="text-lg font-bold text-gray-900 capitalize">{report.final_diagnosis.replace(/_/g, " ")}</h4>
                {renderStage(report.stage)}
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>Confidence: <b className="text-gray-800">{(report.confidence * 100).toFixed(1)}%</b></span>
                {report.fusion_score !== undefined && <span>Fusion: <b className="text-gray-800">{(report.fusion_score * 100).toFixed(1)}%</b></span>}
                <span>{new Date(report.created_at).toLocaleDateString()}</span>
              </div>
            </div>
            <div>
              {report.doctor_verified
                ? <span className="flex items-center gap-1 px-3 py-1.5 bg-green-50 border border-green-200 text-green-700 rounded-full text-xs font-semibold"><CheckCircleSolid className="h-4 w-4" /> Verified</span>
                : <span className="flex items-center gap-1 px-3 py-1.5 bg-amber-50 border border-amber-200 text-amber-700 rounded-full text-xs font-semibold"><ExclamationTriangleIcon className="h-4 w-4" /> Pending</span>}
            </div>
          </div>
        </div>
        {isExpanded && (
          <div className="border-t border-gray-100 p-5 bg-gray-50/60 space-y-4">
            {report.multimodal_analysis && Object.keys(report.multimodal_analysis).length > 0 && (
              <div>
                <h5 className="font-semibold text-gray-800 mb-2 flex items-center gap-2"><DocumentTextIcon className="h-5 w-5 text-blue-600" /> Multimodal Analysis</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {Object.entries(report.multimodal_analysis).map(([key, value]: [string, any]) => (
                    <div key={key} className="bg-white p-3 rounded-lg border border-gray-200">
                      <div className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-1">{key.replace(/_/g, " ")}</div>
                      {typeof value === "object"
                        ? <div className="text-sm text-gray-700 space-y-0.5">{Object.entries(value).map(([k, v]) => (<div key={k} className="flex justify-between"><span className="capitalize text-gray-500">{k.replace(/_/g, " ")}</span><span className="font-medium">{typeof v === "number" ? (v * 100).toFixed(1) + "%" : String(v)}</span></div>))}</div>
                        : <div className="text-sm font-medium text-gray-700">{typeof value === "number" ? (value * 100).toFixed(1) + "%" : String(value)}</div>}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {report.doctor_notes && (
              <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                <h5 className="font-semibold text-blue-800 text-sm mb-1">Doctor's Notes</h5>
                <p className="text-blue-700 text-sm">{report.doctor_notes}</p>
              </div>
            )}
            {showVerify && !report.doctor_verified && (
              <button onClick={(e) => { e.stopPropagation(); setVerifyingReport(report); setVerifyNotes(report.doctor_notes || ""); }}
                className="px-6 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium flex items-center gap-2">
                <CheckCircleIcon className="h-5 w-5" /> Verify This Report
              </button>
            )}
          </div>
        )}
      </div>
    );
  };

  /* ── Sidebar items ── */
  const sidebarItems = [
    { id: "dashboard", label: "Dashboard", icon: HomeIcon },
    { id: "appointments", label: "Appointments", icon: CalendarIcon },
    { id: "requests", label: "Patient Requests", icon: UserGroupIcon, badge: patientRequests.length },
    { id: "pending", label: "Pending Reports", icon: ClipboardDocumentCheckIcon, badge: analytics?.pending_reports || 0 },
    { id: "patients", label: "My Patients", icon: UserGroupIcon },
    { id: "search", label: "Search Patient", icon: MagnifyingGlassIcon },
    { id: "analytics", label: "Analytics", icon: ChartBarIcon },
    { id: "messages", label: "Messages", icon: ChatBubbleLeftRightIcon },
  ];

  const doctorName = `Dr. ${state.user?.first_name || ""} ${state.user?.last_name || ""}`.trim();

  /* ── Dashboard home panel ── */
  const DashboardHome = () => (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        {[
          { label: "Total Patients", value: analytics?.total_patients ?? "—", icon: UserGroupIcon, color: "from-indigo-500 to-indigo-600", light: "bg-indigo-100", iconColor: "text-indigo-600", desc: "Registered patients" },
          { label: "Pending Reports", value: analytics?.pending_reports ?? "—", icon: ClipboardDocumentCheckIcon, color: "from-amber-400 to-amber-500", light: "bg-amber-100", iconColor: "text-amber-600", desc: "Awaiting verification" },
          { label: "New Uploads", value: analytics?.recent_uploads ?? "—", icon: DocumentTextIcon, color: "from-emerald-500 to-emerald-600", light: "bg-emerald-100", iconColor: "text-emerald-600", desc: "Recent reports" },
        ].map((card) => (
          <div key={card.label} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex items-center gap-5 hover:shadow-md transition-shadow">
            <div className={`w-14 h-14 rounded-full ${card.light} flex items-center justify-center flex-shrink-0`}>
              <card.icon className={`h-7 w-7 ${card.iconColor}`} />
            </div>
            <div>
              <p className="text-sm text-gray-500">{card.label}</p>
              <p className="text-3xl font-extrabold text-gray-900">{analyticsLoading ? "..." : card.value}</p>
              <p className="text-xs text-gray-400 mt-0.5">{card.desc}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Middle Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Patient Summary Chart */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-800 mb-4 text-sm uppercase tracking-wide">Patient Summary</h3>
          {analytics ? (
            <DonutChart total={analytics.total_patients} pending={analytics.pending_reports} recent={analytics.recent_uploads} />
          ) : (
            <div className="flex justify-center py-10"><LoadingSpinner /></div>
          )}
        </div>

        {/* Recent Patients */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-800 text-sm uppercase tracking-wide">Recent Patients</h3>
            <button onClick={() => handleTabChange("patients")} className="text-indigo-600 text-xs font-medium hover:underline">View All →</button>
          </div>
          {patientsLoading ? <div className="flex justify-center py-8"><LoadingSpinner /></div> :
            patients.length === 0 ? (
              <div className="flex flex-col items-center py-10 text-gray-400">
                <UserGroupIcon className="h-10 w-10 mb-2" />
                <p className="text-sm">No patients yet. Accept requests to add patients.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {patients.slice(0, 5).map((p, i) => (
                  <div key={p.id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 transition cursor-pointer"
                    onClick={() => { setPatientIdInput(p.patient_id || p.id); handleTabChange("search"); }}>
                    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                      {p.first_name[0]}{p.last_name[0]}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-gray-900 text-sm truncate">{p.first_name} {p.last_name}</p>
                      <p className="text-xs text-gray-400 truncate">{p.email}</p>
                    </div>
                    <span className="text-xs text-gray-400">{new Date(p.created_at).toLocaleDateString()}</span>
                    <span className={`w-2 h-2 rounded-full flex-shrink-0 ${i % 3 === 0 ? "bg-emerald-400" : i % 3 === 1 ? "bg-amber-400" : "bg-indigo-400"}`} />
                  </div>
                ))}
              </div>
            )}
        </div>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Patient Reviews */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-800 mb-5 text-sm uppercase tracking-wide flex items-center gap-2">
            <StarIcon className="h-4 w-4 text-amber-400" /> Patient Outcomes
          </h3>
          <div className="space-y-3">
            <ReviewBar label="Healthy" value={72} color="bg-emerald-500" />
            <ReviewBar label="Early Stage" value={15} color="bg-indigo-400" />
            <ReviewBar label="Moderate" value={9} color="bg-amber-400" />
            <ReviewBar label="Advanced" value={4} color="bg-red-400" />
          </div>
        </div>

        {/* Appointment Requests */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-800 text-sm uppercase tracking-wide">Appointment Requests</h3>
            {patientRequests.length > 0 && <span className="px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded-full text-xs font-bold">{patientRequests.length}</span>}
          </div>
          {requestsLoading ? <div className="flex justify-center py-8"><LoadingSpinner /></div> :
            patientRequests.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-6">No pending requests</p>
            ) : (
              <div className="space-y-3">
                {patientRequests.slice(0, 3).map(req => (
                  <div key={req.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-pink-400 to-rose-500 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                      {req.patient_name?.[0] ?? "P"}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-gray-900 text-sm truncate">{req.patient_name}</p>
                      <p className="text-xs text-gray-400 truncate">{new Date(req.requested_at).toLocaleDateString()}</p>
                    </div>
                    <div className="flex gap-1">
                      <button onClick={() => handleRequestAction(req.id, "reject")} className="p-1.5 rounded-lg border border-red-200 text-red-500 hover:bg-red-50 transition"><XMarkIcon className="h-4 w-4" /></button>
                      <button onClick={() => handleRequestAction(req.id, "approve")} className="p-1.5 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition"><CheckCircleIcon className="h-4 w-4" /></button>
                    </div>
                  </div>
                ))}
                {patientRequests.length > 3 && (
                  <button onClick={() => handleTabChange("requests")} className="w-full text-center text-xs text-indigo-600 hover:underline pt-1">View all {patientRequests.length} requests →</button>
                )}
              </div>
            )}
        </div>

        {/* Calendar */}
        <MiniCalendar />
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-[#f0f4fa] overflow-hidden font-sans">
      {/* ── Sidebar ── */}
      <aside className={`${sidebarOpen ? "w-64" : "w-0 overflow-hidden"} transition-all duration-300 bg-white shadow-lg flex flex-col flex-shrink-0 z-20 border-r border-gray-100`}>
        {/* Doctor Profile */}
        <div className="p-6 border-b border-gray-100">
          <div className="flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold mb-3 shadow-md">
              {state.user?.first_name?.[0] ?? "D"}{state.user?.last_name?.[0] ?? "R"}
            </div>
            <p className="font-bold text-gray-900 text-sm leading-tight">{doctorName || "Doctor"}</p>
            <p className="text-xs text-indigo-600 font-medium mt-0.5">Neurologist</p>
            <span className="mt-2 px-2.5 py-0.5 bg-emerald-100 text-emerald-700 rounded-full text-xs font-semibold">● Online</span>
          </div>
        </div>

        {/* Nav Items */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {sidebarItems.map(item => (
            <button key={item.id} onClick={() => { handleTabChange(item.id as any); setError(null); }}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all
                ${activeTab === item.id ? "bg-indigo-600 text-white shadow-sm" : "text-gray-600 hover:bg-indigo-50 hover:text-indigo-700"}`}>
              <item.icon className="h-5 w-5 flex-shrink-0" />
              <span className="flex-1 text-left">{item.label}</span>
              {(item.badge ?? 0) > 0 && (
                <span className={`px-1.5 py-0.5 rounded-full text-xs font-bold ${activeTab === item.id ? "bg-white text-indigo-600" : "bg-indigo-600 text-white"}`}>
                  {item.badge}
                </span>
              )}
            </button>
          ))}
        </nav>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-gray-100 space-y-1">
          <button onClick={() => handleTabChange("analytics" as any)}
            className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-100 transition">
            <Cog6ToothIcon className="h-5 w-5" /> Settings
          </button>
          <button onClick={() => { logout(); navigate("/login"); }}
            className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium text-red-500 hover:bg-red-50 transition">
            <ArrowRightOnRectangleIcon className="h-5 w-5" /> Logout
          </button>
        </div>
      </aside>

      {/* ── Main Content ── */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="bg-white border-b border-gray-100 px-6 py-4 flex items-center gap-4 shadow-sm flex-shrink-0">
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-gray-500 hover:text-indigo-600 transition">
            <Bars3Icon className="h-6 w-6" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-gray-900 capitalize">{activeTab === "dashboard" ? "Dashboard" : activeTab.replace(/_/g, " ")}</h1>
            <p className="text-xs text-gray-400">Welcome back, {doctorName}</p>
          </div>
          <div className="flex-1 max-w-md ml-6">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input placeholder="Search patient by ID…" value={patientIdInput} onChange={e => setPatientIdInput(e.target.value)}
                onKeyPress={e => e.key === "Enter" && (handleTabChange("search"), searchPatientById())}
                className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-xl bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:bg-white transition" />
            </div>
          </div>
          <div className="ml-auto flex items-center gap-3">
            <button className="relative p-2 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition">
              <BellIcon className="h-5 w-5" />
              {(analytics?.pending_reports ?? 0) > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              )}
            </button>
            <button onClick={() => handleTabChange("messages")} className="p-2 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition">
              <ChatBubbleLeftRightIcon className="h-5 w-5" />
            </button>
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold cursor-pointer">
              {state.user?.first_name?.[0] ?? "D"}
            </div>
          </div>
        </header>

        {/* Alerts */}
        <div className="px-6 pt-4 space-y-2 flex-shrink-0">
          {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
          {successMsg && (
            <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-xl flex items-center gap-2">
              <CheckCircleSolid className="h-5 w-5 text-green-600 flex-shrink-0" />{successMsg}
            </div>
          )}
        </div>

        {/* Tab Content */}
        <main className="flex-1 overflow-y-auto px-6 pb-6 pt-4">
          {activeTab === "dashboard" && <DashboardHome />}

          {activeTab === "search" && (
            <div className="space-y-6 max-w-4xl">
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Search Patient by ID</h2>
                <div className="flex gap-4">
                  <input type="text" placeholder="Enter Patient ID (e.g., PID-123456 or UUID)…" value={patientIdInput}
                    onChange={e => setPatientIdInput(e.target.value)} onKeyPress={e => e.key === "Enter" && searchPatientById()}
                    className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-400 focus:outline-none text-sm" />
                  <button onClick={searchPatientById} disabled={searching || !patientIdInput.trim()}
                    className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2 text-sm font-medium transition">
                    {searching ? <LoadingSpinner size="sm" /> : <MagnifyingGlassIcon className="h-5 w-5" />} Search
                  </button>
                </div>
              </div>
              {searchedPatient && (
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                  <div className="flex justify-between items-start mb-6 border-b pb-4">
                    <div className="flex items-center gap-4">
                      <div className="w-14 h-14 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white text-xl font-bold">
                        {searchedPatient.patient.first_name[0]}{searchedPatient.patient.last_name[0]}
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900">{searchedPatient.patient.first_name} {searchedPatient.patient.last_name}</h3>
                        <p className="text-gray-500 text-sm">ID: {searchedPatient.patient.patient_id || searchedPatient.patient.id}</p>
                        <p className="text-gray-400 text-xs">{searchedPatient.patient.email}</p>
                      </div>
                    </div>
                    <button onClick={() => setSearchedPatient(null)} className="p-2 text-gray-400 hover:bg-gray-100 rounded-full transition"><XMarkIcon className="h-5 w-5" /></button>
                  </div>
                  <h4 className="text-base font-bold text-gray-900 mb-4 flex items-center gap-2"><DocumentTextIcon className="h-5 w-5 text-indigo-600" /> Diagnosis Reports ({searchedPatient.reports.length})</h4>
                  {searchedPatient.reports.length === 0
                    ? <p className="text-gray-500 text-center py-8">No reports found for this patient.</p>
                    : <div className="space-y-4">{searchedPatient.reports.map(rep => <ReportCard key={rep.id} report={rep} />)}</div>}
                </div>
              )}
            </div>
          )}

          {activeTab === "pending" && (
            <div className="space-y-4 max-w-4xl">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2"><ClipboardDocumentCheckIcon className="h-6 w-6 text-amber-500" /> Reports Awaiting Verification</h2>
                <button onClick={fetchPendingReports} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 text-sm font-medium transition">Refresh</button>
              </div>
              {pendingLoading ? <div className="flex justify-center py-16"><LoadingSpinner /></div>
                : pendingReports.length === 0
                  ? <div className="bg-white p-12 rounded-2xl border border-gray-100 text-center"><CheckCircleSolid className="h-14 w-14 text-green-400 mx-auto mb-3" /><p className="text-lg font-semibold text-gray-700">All caught up!</p><p className="text-gray-400 mt-1 text-sm">No pending reports.</p></div>
                  : <div className="space-y-4">{pendingReports.map(rep => <ReportCard key={rep.id} report={rep} patientLabel={`Patient: ${rep.patient_name}${rep.patient_pid ? ` (${rep.patient_pid})` : ""}`} />)}</div>}
            </div>
          )}

          {activeTab === "requests" && (
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 max-w-4xl">
              <h2 className="text-lg font-semibold mb-6">Patient Connection Requests</h2>
              {requestsLoading ? <div className="flex justify-center py-10"><LoadingSpinner /></div>
                : patientRequests.length === 0 ? <p className="text-gray-500 text-center py-10">No pending requests.</p>
                  : <div className="space-y-4">{patientRequests.map(req => (
                    <div key={req.id} className="p-5 border border-gray-100 rounded-2xl flex items-center justify-between shadow-sm hover:shadow-md transition">
                      <div className="flex items-center gap-4">
                        <div className="w-11 h-11 rounded-full bg-gradient-to-br from-pink-400 to-rose-500 flex items-center justify-center text-white font-bold">{req.patient_name?.[0] ?? "P"}</div>
                        <div>
                          <h3 className="font-bold text-gray-900">{req.patient_name}</h3>
                          <p className="text-sm text-gray-500">{req.patient_email}{req.patient_pid ? ` • ID: ${req.patient_pid}` : ""}</p>
                          {req.message && <p className="text-sm text-gray-700 italic mt-1">"{req.message}"</p>}
                          <p className="text-xs text-gray-400 mt-1">Requested {new Date(req.requested_at).toLocaleDateString()}</p>
                        </div>
                      </div>
                      <div className="flex gap-3">
                        <button onClick={() => handleRequestAction(req.id, "reject")} className="px-4 py-2 border border-red-200 text-red-600 rounded-xl hover:bg-red-50 text-sm font-medium transition">Reject</button>
                        <button onClick={() => handleRequestAction(req.id, "approve")} className="px-4 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 text-sm font-medium transition">Accept</button>
                      </div>
                    </div>
                  ))}</div>}
            </div>
          )}

          {activeTab === "patients" && (
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
              <h2 className="text-lg font-semibold mb-6">Patient Roster</h2>
              {patientsLoading ? <div className="flex justify-center py-10"><LoadingSpinner /></div>
                : patients.length === 0 ? <p className="text-gray-500 text-center py-10">No patients found.</p>
                  : <div className="overflow-x-auto"><table className="w-full text-left">
                    <thead><tr className="bg-gray-50 text-gray-500 border-b text-sm">
                      <th className="p-4 font-medium rounded-tl-xl">Patient</th>
                      <th className="p-4 font-medium">Email</th>
                      <th className="p-4 font-medium">Joined</th>
                      <th className="p-4 font-medium text-right rounded-tr-xl">Action</th>
                    </tr></thead>
                    <tbody>{patients.map(p => (
                      <tr key={p.id} className="border-b hover:bg-indigo-50/40 transition">
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white text-xs font-bold">{p.first_name[0]}{p.last_name[0]}</div>
                            <span className="font-medium text-gray-900 text-sm">{p.first_name} {p.last_name}</span>
                          </div>
                        </td>
                        <td className="p-4 text-gray-600 text-sm">{p.email}</td>
                        <td className="p-4 text-gray-500 text-sm">{new Date(p.created_at).toLocaleDateString()}</td>
                        <td className="p-4 text-right">
                          <button onClick={() => { setPatientIdInput(p.patient_id || p.id); handleTabChange("search"); setTimeout(async () => { setSearching(true); try { const r = await axios.get(`${API_BASE_URL}/doctors/search-patient/${p.patient_id || p.id}`, { headers: { Authorization: `Bearer ${state.token}` } }); setSearchedPatient({ patient: r.data.patient, reports: r.data.reports, latestRecommendations: null }); } catch { setError("Failed to fetch patient."); } finally { setSearching(false); } }, 100); }}
                            className="text-indigo-600 hover:text-indigo-800 text-sm font-medium hover:underline">View Reports</button>
                        </td>
                      </tr>
                    ))}</tbody>
                  </table></div>}
            </div>
          )}

          {activeTab === "analytics" && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                {analyticsLoading ? <div className="col-span-4 flex justify-center py-10"><LoadingSpinner /></div>
                  : analytics ? [
                    { label: "Total Patients", val: analytics.total_patients, from: "from-indigo-500", to: "to-indigo-600" },
                    { label: "Total Reports", val: analytics.total_reports, from: "from-emerald-500", to: "to-emerald-600" },
                    { label: "Pending Reports", val: analytics.pending_reports, from: "from-amber-400", to: "to-amber-500" },
                    { label: "Recent Uploads", val: analytics.recent_uploads, from: "from-purple-500", to: "to-purple-600" },
                  ].map(c => (
                    <div key={c.label} className={`p-6 bg-gradient-to-br ${c.from} ${c.to} rounded-2xl text-white shadow-md`}>
                      <p className="text-white/80 text-xs font-semibold uppercase tracking-wide mb-2">{c.label}</p>
                      <p className="text-5xl font-extrabold">{c.val}</p>
                    </div>
                  )) : <p className="text-gray-500">Failed to load analytics.</p>}
              </div>
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                <h3 className="font-semibold text-gray-800 mb-5">Patient Outcome Distribution</h3>
                <div className="space-y-4">
                  <ReviewBar label="Healthy" value={72} color="bg-emerald-500" />
                  <ReviewBar label="Early Stage" value={15} color="bg-indigo-400" />
                  <ReviewBar label="Moderate" value={9} color="bg-amber-400" />
                  <ReviewBar label="Advanced" value={4} color="bg-red-400" />
                </div>
              </div>
            </div>
          )}

          {activeTab === "appointments" && (
            <DoctorAppointments patients={patients} />
          )}

          {activeTab === "messages" && <GenericMessaging />}
        </main>
      </div>

      {/* ── Verify Modal ── */}
      {verifyingReport && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden">
            <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-4">
              <h3 className="text-lg font-bold flex items-center gap-2"><CheckCircleIcon className="h-6 w-6" /> Verify Diagnosis Report</h3>
              <p className="text-green-100 text-sm mt-1">{verifyingReport.final_diagnosis.replace(/_/g, " ").toUpperCase()} — Stage {verifyingReport.stage}</p>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div><span className="text-gray-500">Confidence</span><p className="font-semibold text-gray-800">{(verifyingReport.confidence * 100).toFixed(1)}%</p></div>
                <div><span className="text-gray-500">Date</span><p className="font-semibold text-gray-800">{new Date(verifyingReport.created_at).toLocaleDateString()}</p></div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Doctor's Notes (optional)</label>
                <textarea value={verifyNotes} onChange={e => setVerifyNotes(e.target.value)}
                  placeholder="Add your clinical observations, notes, or recommendations…"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-green-500 resize-none text-sm" rows={4} />
              </div>
              <div className="flex gap-3 justify-end pt-2">
                <button onClick={() => { setVerifyingReport(null); setVerifyNotes(""); }}
                  className="px-5 py-2.5 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 font-medium text-sm transition">Cancel</button>
                <button onClick={() => handleVerifyReport(verifyingReport.id)} disabled={verifyLoading}
                  className="px-6 py-2.5 bg-green-600 text-white rounded-xl hover:bg-green-700 disabled:opacity-50 font-medium flex items-center gap-2 text-sm transition">
                  {verifyLoading ? <LoadingSpinner size="sm" /> : <CheckCircleSolid className="h-5 w-5" />}
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