import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  UserGroupIcon, ChartBarIcon, MagnifyingGlassIcon, XMarkIcon,
  ChatBubbleLeftRightIcon, CheckCircleIcon, ExclamationTriangleIcon,
  ClipboardDocumentCheckIcon, DocumentTextIcon, BellIcon, Bars3Icon,
  ArrowRightOnRectangleIcon, UserIcon, HomeIcon,
  ArrowUpTrayIcon
} from "@heroicons/react/24/outline";
import { CheckCircleIcon as CheckCircleSolid } from "@heroicons/react/24/solid";
import { useAuth } from "../../contexts/AuthContext";
import { LoadingSpinner, Alert } from "../common";
import CountUp from "../common/CountUp";
import axios from "axios";
import GenericMessaging from "../common/GenericMessaging";
import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const stageLabels: Record<number, { label: string; color: string; bg: string }> = {
  0: { label: "Healthy", color: "text-green-700", bg: "bg-green-100" },
  1: { label: "Early Stage", color: "text-yellow-700", bg: "bg-yellow-100" },
  2: { label: "Moderate", color: "text-orange-700", bg: "bg-orange-100" },
  3: { label: "Advanced", color: "text-red-700", bg: "bg-red-100" },
  4: { label: "Severe", color: "text-red-900", bg: "bg-red-200" },
};

export default function DoctorDashboard() {
  const { state, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const initialTab = location.hash ? location.hash.replace("#", "") : "dashboard";
  const [activeTab, setActiveTab] = useState<string>(initialTab);

  useEffect(() => {
    if (location.hash) {
      const hashTab = location.hash.replace("#", "");
      setActiveTab(hashTab);
    }
  }, [location.hash]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    navigate(`/doctor/dashboard#${tabId}`, { replace: true });
    setSidebarOpen(false);
  };

  const [patients, setPatients] = useState<any[]>([]);
  const [patientsLoading, setPatientsLoading] = useState(false);
  const [analytics, setAnalytics] = useState<any>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const [patientIdInput, setPatientIdInput] = useState("");
  const [searchedPatient, setSearchedPatient] = useState<any>(null);
  const [searching, setSearching] = useState(false);

  const [pendingReports, setPendingReports] = useState<any[]>([]);
  const [pendingLoading, setPendingLoading] = useState(false);
  const [patientRequests, setPatientRequests] = useState<any[]>([]);
  const [requestsLoading, setRequestsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [verifyingReport, setVerifyingReport] = useState<any>(null);
  const [verifyNotes, setVerifyNotes] = useState("");
  const [verifyLoading, setVerifyLoading] = useState(false);
  const [expandedReportId, setExpandedReportId] = useState<string | null>(null);

  useEffect(() => {
    if (activeTab === "patients" || activeTab === "dashboard") { if (patients.length === 0) fetchPatients(); }
    if (activeTab === "analytics" || activeTab === "dashboard") { if (!analytics) fetchAnalytics(); }
    if (activeTab === "pending" || activeTab === "dashboard") { if (pendingReports.length === 0) fetchPendingReports(); }
    if (activeTab === "requests" || activeTab === "dashboard") { if (patientRequests.length === 0) fetchRequests(); }
  }, [activeTab]);

  const fetchPatients = async () => {
    setPatientsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/doctors/patients`, { headers: { Authorization: `Bearer ${state.token}` } });
      setPatients(response.data);
    } catch { console.error("Failed to fetch patients."); }
    finally { setPatientsLoading(false); }
  };

  const fetchAnalytics = async () => {
    setAnalyticsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/doctors/analytics`, { headers: { Authorization: `Bearer ${state.token}` } });
      setAnalytics(response.data);
    } catch { console.error("Failed to fetch analytics."); }
    finally { setAnalyticsLoading(false); }
  };

  const fetchPendingReports = async () => {
    setPendingLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/doctors/reports/pending`, { headers: { Authorization: `Bearer ${state.token}` } });
      setPendingReports(response.data);
    } catch { console.error("Failed to fetch pending reports."); }
    finally { setPendingLoading(false); }
  };

  const fetchRequests = async () => {
    setRequestsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/doctors/requests`, { headers: { Authorization: `Bearer ${state.token}` } });
      setPatientRequests(response.data);
    } catch { console.error("Failed to fetch patient requests."); }
    finally { setRequestsLoading(false); }
  };

  const handleRequestAction = async (reqId: string, action: "approve" | "reject") => {
    try {
      await axios.post(`${API_BASE_URL}/doctors/requests/${reqId}/${action}`, {}, { headers: { Authorization: `Bearer ${state.token}` } });
      setSuccessMsg(`Patient request ${action}d successfully`);
      setPatientRequests((prev) => prev.filter((r) => r.id !== reqId));
      if (action === "approve") fetchPatients();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch { setError(`Failed to ${action} request.`); }
  };

  const searchPatientById = async () => {
    if (!patientIdInput.trim()) { setError("Please enter a valid Patient ID"); return; }
    setSearching(true); setError(null); setSearchedPatient(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/doctors/search-patient/${patientIdInput}`, { headers: { Authorization: `Bearer ${state.token}` } });
      setSearchedPatient({ patient: response.data.patient, reports: response.data.reports });
      handleTabChange("search");
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
      if (searchedPatient) {
        setSearchedPatient({
          ...searchedPatient,
          reports: searchedPatient.reports.map((r: any) => r.id === reportId ? { ...r, doctor_verified: true, doctor_notes: verifyNotes } : r),
        });
      }
      setPendingReports(pendingReports.filter((r) => r.id !== reportId));
      if (analytics) setAnalytics({ ...analytics, pending_reports: Math.max(0, analytics.pending_reports - 1) });
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch { setError("Failed to verify report."); } finally { setVerifyLoading(false); }
  };

  const renderStage = (stage: number) => {
    const info = stageLabels[stage] || { label: `Stage ${stage}`, color: "text-gray-700", bg: "bg-gray-100" };
    return <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${info.color} ${info.bg}`}>{info.label}</span>;
  };

  const handleLogout = () => { logout(); navigate("/login"); };

  // Nav Items
  const navItems = [
    { id: "dashboard", icon: HomeIcon, label: "Dashboard" },
    { id: "patients", icon: UserGroupIcon, label: "My Patients" },
    { id: "search", icon: MagnifyingGlassIcon, label: "Search Patient" },
    { id: "pending", icon: ClipboardDocumentCheckIcon, label: "Pending Reports", badge: analytics?.pending_reports },
    { id: "requests", icon: DocumentTextIcon, label: "Requests", badge: patientRequests.length },
    { id: "analytics", icon: ChartBarIcon, label: "Analytics" },
    { id: "messages", icon: ChatBubbleLeftRightIcon, label: "Messages" },
  ];

  const donutData = {
    labels: ['New Patients', 'Old Patients', 'Recovered'],
    datasets: [{
      data: [patients.length > 5 ? 5 : patients.length, patients.length > 5 ? patients.length - 5 : 0, 0],
      backgroundColor: ['#3b82f6', '#60a5fa', '#93c5fd'],
      borderWidth: 0,
    }]
  };

  const ReportCard = ({ report, patientLabel, showVerify = true }: { report: any, patientLabel?: string, showVerify?: boolean }) => {
    const isExpanded = expandedReportId === report.id;
    return (
      <div className={`bg-white rounded-xl border transition-all duration-200 ${report.doctor_verified ? "border-green-200" : "border-amber-200"} hover:shadow-md mb-4`}>
        <div className="p-5 cursor-pointer" onClick={() => setExpandedReportId(isExpanded ? null : report.id)}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {patientLabel && <p className="text-sm text-gray-500 mb-1 font-medium">{patientLabel}</p>}
              <div className="flex items-center gap-3 mb-2">
                <h4 className="text-lg font-bold text-gray-900 capitalize">{report.final_diagnosis.replace(/_/g, " ")}</h4>
                {renderStage(report.stage)}
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span className="flex">Confidence: <b className="text-gray-800 ml-1 flex"><CountUp to={Number((report.confidence * 100).toFixed(1))} direction="up" duration={2} />%</b></span>
                {report.fusion_score !== undefined && <span className="flex">Fusion Score: <b className="text-gray-800 ml-1 flex"><CountUp to={Number((report.fusion_score * 100).toFixed(1))} direction="up" duration={2} />%</b></span>}
                <span>{new Date(report.created_at).toLocaleDateString()}</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {report.doctor_verified ? (
                <span className="flex items-center gap-1 px-3 py-1.5 bg-green-50 border border-green-200 text-green-700 rounded-full text-xs font-semibold"><CheckCircleSolid className="h-4 w-4" /> Verified</span>
              ) : (
                <span className="flex items-center gap-1 px-3 py-1.5 bg-amber-50 border border-amber-200 text-amber-700 rounded-full text-xs font-semibold"><ExclamationTriangleIcon className="h-4 w-4" /> Pending</span>
              )}
            </div>
          </div>
        </div>
        {isExpanded && (
          <div className="border-t border-gray-100 p-5 bg-gray-50/60 space-y-4">
            {report.doctor_notes && (
              <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                <h5 className="font-semibold text-blue-800 text-sm mb-1">Doctor's Notes</h5>
                <p className="text-blue-700 text-sm">{report.doctor_notes}</p>
              </div>
            )}
            {showVerify && !report.doctor_verified && (
              <button onClick={(e) => { e.stopPropagation(); setVerifyingReport(report); setVerifyNotes(report.doctor_notes || ""); }} className="px-6 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium flex items-center gap-2 pt-2">
                <CheckCircleIcon className="h-5 w-5" /> Verify This Report
              </button>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-slate-50 font-sans">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 text-white left-0 z-50 w-64 bg-blue-900 border-r border-gray-200 transform transition-transform duration-300 ease-in-out ${sidebarOpen ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0 lg:static lg:block h-full flex flex-col shadow-xl`}>
        <div className="flex flex-col items-center justify-center pt-8 pb-6 border-b border-blue-800">
          <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg text-blue-900 mb-3 border-4 border-blue-200">
            <UserIcon className="w-10 h-10" />
          </div>
          <h2 className="text-lg font-bold">Dr. {state.user?.first_name} {state.user?.last_name}</h2>
          <p className="text-sm font-medium text-blue-200">Neurologist</p>
        </div>

        <div className="overflow-y-auto flex-1 py-4 px-3 space-y-1">
          {navItems.map((item) => (
            <button key={item.id} onClick={() => handleTabChange(item.id)} className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-200 ${activeTab === item.id ? "bg-white text-blue-900 shadow-md font-bold" : "text-blue-50 hover:bg-blue-800 hover:text-white"}`}>
              <div className="flex items-center gap-3">
                <item.icon className="h-5 w-5" />
                <span>{item.label}</span>
              </div>
              {item.badge ? <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full font-bold">{item.badge}</span> : null}
            </button>
          ))}
        </div>
        <div className="p-4 border-t border-blue-800">
          <button onClick={handleLogout} className="w-full flex items-center gap-3 px-4 py-3 text-blue-200 hover:text-white hover:bg-blue-800 rounded-xl transition-all duration-200 font-medium">
            <ArrowRightOnRectangleIcon className="h-5 w-5" /> Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="bg-white border-b border-gray-100 flex items-center justify-between px-6 py-4 shadow-sm z-10">
          <div className="flex items-center gap-4">
            <button onClick={() => setSidebarOpen(true)} className="lg:hidden p-2 text-gray-500 hover:bg-gray-100 rounded-lg">
              <Bars3Icon className="h-6 w-6" />
            </button>
            <h1 className="text-2xl font-bold text-gray-800 capitalize tracking-tight">{activeTab.replace('-', ' ')} Overview</h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative hidden md:block">
              <input type="text" placeholder="Quick search..." value={patientIdInput} onChange={(e) => setPatientIdInput(e.target.value)} onKeyPress={(e) => e.key === "Enter" && searchPatientById()} className="pl-10 pr-4 py-2 bg-gray-50 border-none rounded-full text-sm focus:ring-2 focus:ring-blue-500 w-64 transition-all focus:bg-white" />
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-2" />
            </div>
            <button className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors relative">
              <BellIcon className="h-6 w-6" />
              <span className="absolute top-1 right-1 h-2.5 w-2.5 bg-red-500 rounded-full border-2 border-white"></span>
            </button>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-slate-50/50 p-6">
          {error && <Alert type="error" message={error} onClose={() => setError(null)} className="mb-4" />}
          {successMsg && <div className="mb-4 bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg flex items-center gap-2 shadow-sm font-medium"><CheckCircleSolid className="h-5 w-5 text-green-500" />{successMsg}</div>}

          {/* DASHBOARD TAB DYNAMIC VIEW */}
          {activeTab === "dashboard" && (
            <div className="space-y-6 animate-fade-in">
              {/* Stat Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                  { label: "Total Patients", val: analytics?.total_patients || patients.length, icon: UserGroupIcon, color: "text-blue-600", bg: "bg-blue-50" },
                  { label: "Pending verification", val: analytics?.pending_reports || pendingReports.length, icon: ClipboardDocumentCheckIcon, color: "text-amber-600", bg: "bg-amber-50" },
                  { label: "New Requests", val: patientRequests.length, icon: ArrowUpTrayIcon, color: "text-emerald-600", bg: "bg-emerald-50" }
                ].map((stat, i) => (
                  <div key={i} className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex items-center gap-5 hover:shadow-md transition-shadow">
                    <div className={`p-4 rounded-full ${stat.bg}`}><stat.icon className={`h-8 w-8 ${stat.color}`} /></div>
                    <div>
                      <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide">{stat.label}</p>
                      <p className="text-3xl font-extrabold text-gray-900 mt-1">{stat.val}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Middle Section */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column - Chart */}
                <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex flex-col">
                  <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">Patient Summary</h3>
                  <div className="flex-1 flex items-center justify-center relative min-h-[250px]">
                    <Doughnut data={donutData} options={{ maintainAspectRatio: false, cutout: '75%', plugins: { legend: { position: 'bottom' } } }} />
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none mt-[-20px]">
                      <div className="text-center">
                        <p className="text-sm text-gray-500 font-medium">Total</p>
                        <p className="text-2xl font-bold text-gray-800">{patients.length}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Middle & Right Column - Patients & Requests */}
                <div className="lg:col-span-2 space-y-6">
                  {/* Next Patient Highlight */}
                  {patients.length > 0 ? (
                    <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm overflow-hidden relative">
                      <div className="absolute top-0 right-0 w-32 h-32 bg-blue-50 rounded-bl-full -z-10 opacity-60"></div>
                      <h3 className="text-sm font-bold tracking-widest text-blue-600 mb-4 uppercase">Next Appointment / Active</h3>
                      <div className="flex items-start gap-4">
                        <div className="h-16 w-16 bg-gradient-to-tr from-blue-200 to-blue-100 rounded-full flex items-center justify-center text-blue-800 font-bold text-xl shadow-inner">
                          {patients[0].first_name[0]}{patients[0].last_name[0]}
                        </div>
                        <div className="flex-1">
                          <h4 className="text-2xl font-bold text-gray-900">{patients[0].first_name} {patients[0].last_name}</h4>
                          <p className="text-gray-500 font-medium mt-1">ID: {patients[0].patient_id || patients[0].id}</p>
                          <div className="flex flex-wrap gap-2 mt-3 text-sm">
                            {patients[0].diagnosis_status ? <span className="bg-amber-100 text-amber-800 px-3 py-1 rounded-full font-semibold">{patients[0].diagnosis_status}</span> : null}
                            <span className="bg-slate-100 text-slate-700 px-3 py-1 rounded-full font-medium">Checkup</span>
                          </div>
                        </div>
                        <div className="flex flex-col gap-2">
                          <button onClick={() => { setPatientIdInput(patients[0].patient_id || patients[0].id); searchPatientById(); }} className="p-2.5 bg-blue-600 text-white rounded-xl shadow hover:bg-blue-700 transition" title="View Documents">
                            <DocumentTextIcon className="h-5 w-5" />
                          </button>
                          <button onClick={() => handleTabChange('messages')} className="p-2.5 bg-indigo-50 text-indigo-600 rounded-xl border border-indigo-100 hover:bg-indigo-100 transition" title="Message">
                            <ChatBubbleLeftRightIcon className="h-5 w-5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm text-center text-gray-500 py-10">No active patients.</div>
                  )}

                  {/* Quick Lists */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
                      <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2"><UserGroupIcon className="h-5 w-5 text-gray-400" /> Recent Patients</h4>
                      <div className="space-y-3">
                        {patients.slice(0, 3).map(p => (
                          <div key={p.id} className="flex justify-between items-center p-3 hover:bg-gray-50 rounded-xl cursor-pointer transition border border-transparent hover:border-gray-100" onClick={() => { setPatientIdInput(p.patient_id || p.id); searchPatientById(); }}>
                            <div>
                              <p className="font-semibold text-gray-800 text-sm">{p.first_name} {p.last_name}</p>
                              <p className="text-xs text-gray-500">{new Date(p.created_at).toLocaleDateString()}</p>
                            </div>
                            <div className="h-8 w-8 rounded-full bg-blue-50 flex items-center justify-center text-blue-600"><ArrowUpTrayIcon className="h-4 w-4" /></div>
                          </div>
                        ))}
                        {patients.length === 0 && <p className="text-xs text-gray-400">No patients</p>}
                      </div>
                    </div>

                    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
                      <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2"><ClipboardDocumentCheckIcon className="h-5 w-5 text-amber-500" /> Needs Action</h4>
                      <div className="space-y-3">
                        {pendingReports.slice(0, 3).map(r => (
                          <div key={r.id} className="p-3 border border-amber-100 bg-amber-50/30 rounded-xl text-sm hover:bg-amber-50 cursor-pointer transition" onClick={() => handleTabChange('pending')}>
                            <p className="font-semibold text-amber-900">{r.patient_name}</p>
                            <p className="text-xs text-amber-700 mt-1 capitalize">{r.final_diagnosis.replace('_', ' ')} • Unverified</p>
                          </div>
                        ))}
                        {pendingReports.length === 0 && <p className="text-xs text-gray-400">All reports verified</p>}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SEARCH TAB */}
          {activeTab === "search" && (
            <div className="space-y-6 animate-fade-in">
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Patient Search & Documents</h2>
                <div className="flex gap-4">
                  <input type="text" placeholder="Enter Patient ID (e.g., PID-123456)..." value={patientIdInput} onChange={(e) => setPatientIdInput(e.target.value)} onKeyPress={(e) => e.key === "Enter" && searchPatientById()} className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500" />
                  <button onClick={searchPatientById} disabled={searching || !patientIdInput.trim()} className="px-8 py-3 bg-blue-600 text-white rounded-xl shadow-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2 font-semibold">
                    {searching ? <LoadingSpinner size="sm" /> : <MagnifyingGlassIcon className="h-5 w-5" />} Search
                  </button>
                </div>
              </div>
              {searchedPatient && (
                <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 animate-fade-in">
                  <div className="flex justify-between items-start mb-6 border-b border-gray-100 pb-6">
                    <div className="flex gap-5">
                      <div className="h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center text-blue-700 font-bold text-xl">{searchedPatient.patient.first_name[0]}{searchedPatient.patient.last_name[0]}</div>
                      <div>
                        <h3 className="text-2xl font-extrabold text-gray-900">{searchedPatient.patient.first_name} {searchedPatient.patient.last_name}</h3>
                        <p className="text-gray-500 font-medium">ID: {searchedPatient.patient.patient_id || searchedPatient.patient.id}</p>
                        <p className="text-gray-400 text-sm">{searchedPatient.patient.email}</p>
                      </div>
                    </div>
                    <button onClick={() => setSearchedPatient(null)} className="p-2 text-gray-400 hover:bg-gray-100 rounded-full"><XMarkIcon className="h-6 w-6" /></button>
                  </div>
                  <h4 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2"><DocumentTextIcon className="h-5 w-5 text-blue-600" /> Diagnosis Reports ({searchedPatient.reports.length})</h4>
                  {searchedPatient.reports.length === 0 ? <p className="text-gray-500 bg-gray-50 rounded-xl py-8 text-center border border-dashed border-gray-200">No reports found.</p> : (
                    <div className="space-y-4">
                      {searchedPatient.reports.map((rep: any) => <ReportCard key={rep.id} report={rep} />)}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* PENDING TAB */}
          {activeTab === "pending" && (
            <div className="space-y-6 animate-fade-in">
              <div className="flex items-center justify-between bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Pending Verification</h2>
                  <p className="text-gray-500 mt-1">Review AI analysis reports before making final decisions.</p>
                </div>
                <button onClick={fetchPendingReports} className="px-5 py-2.5 bg-gray-50 text-gray-700 border border-gray-200 rounded-xl hover:bg-gray-100 text-sm font-semibold shadow-sm transition">Refresh List</button>
              </div>
              {pendingLoading ? <div className="py-16 flex justify-center"><LoadingSpinner /></div> : pendingReports.length === 0 ? (
                <div className="bg-white p-16 rounded-2xl border border-gray-100 text-center shadow-sm">
                  <CheckCircleSolid className="h-16 w-16 text-emerald-400 mx-auto mb-4" />
                  <p className="text-2xl font-bold text-gray-800">All caught up!</p>
                  <p className="text-gray-500 mt-2">There are no pending reports awaiting your verification.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-4">
                  {pendingReports.map(rep => <ReportCard key={rep.id} report={rep} patientLabel={`${rep.patient_name} (${rep.patient_pid || 'No ID'})`} />)}
                </div>
              )}
            </div>
          )}

          {/* REQUESTS TAB */}
          {activeTab === "requests" && (
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 animate-fade-in">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Patient Requests</h2>
              <p className="text-gray-500 mb-8 border-b pb-4">Manage connection requests from new patients on the platform.</p>
              {requestsLoading ? <div className="flex justify-center py-10"><LoadingSpinner /></div> : patientRequests.length === 0 ? (
                <p className="text-center py-12 text-gray-500 bg-gray-50 rounded-xl border border-dashed border-gray-200">No new connection requests.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {patientRequests.map(req => (
                    <div key={req.id} className="p-6 bg-white border border-gray-200 rounded-2xl shadow-sm hover:shadow-md transition">
                      <div className="h-12 w-12 bg-blue-50 text-blue-600 rounded-full flex justify-center items-center font-bold text-lg mb-4">{req.patient_name[0]}</div>
                      <h3 className="font-bold text-xl text-gray-900">{req.patient_name}</h3>
                      <p className="text-sm text-gray-500 mb-4">{req.patient_email}</p>
                      {req.message && <div className="bg-gray-50 p-3 rounded-lg text-sm text-gray-700 italic border-l-4 border-blue-400 mb-4">"{req.message}"</div>}
                      <div className="flex flex-col gap-2 mt-4">
                        <button onClick={() => handleRequestAction(req.id, "approve")} className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition shadow-sm">Accept Patient</button>
                        <button onClick={() => handleRequestAction(req.id, "reject")} className="w-full py-2.5 border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition">Decline</button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* PATIENTS TAB (FULL ROSTER) */}
          {activeTab === "patients" && (
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 animate-fade-in">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Patient Roster</h2>
              {patientsLoading ? <div className="flex justify-center py-10"><LoadingSpinner /></div> : patients.length === 0 ? (
                <p className="text-center py-12 text-gray-500 bg-gray-50 rounded-xl border border-dashed border-gray-200">No patients assigned yet.</p>
              ) : (
                <div className="overflow-hidden rounded-xl border border-gray-200">
                  <table className="w-full text-left">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Patient Name</th>
                        <th className="p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Contact</th>
                        <th className="p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="p-4 text-xs font-bold text-gray-500 uppercase tracking-wider text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {patients.map(p => (
                        <tr key={p.id} className="hover:bg-blue-50/40 transition">
                          <td className="p-4 flex items-center gap-3">
                            <div className="h-10 w-10 rounded-full bg-blue-100 text-blue-700 flex justify-center items-center font-bold">{p.first_name[0]}{p.last_name[0]}</div>
                            <div>
                              <p className="font-bold text-gray-900">{p.first_name} {p.last_name}</p>
                              <p className="text-xs text-gray-500">ID: {p.patient_id || p.id}</p>
                            </div>
                          </td>
                          <td className="p-4">
                            <p className="text-sm text-gray-700">{p.email}</p>
                            {p.phone_number && <p className="text-xs text-gray-500">{p.phone_number}</p>}
                          </td>
                          <td className="p-4">
                            <span className="px-2.5 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-semibold">{p.diagnosis_status || 'Monitoring'}</span>
                          </td>
                          <td className="p-4 text-right">
                            <button onClick={() => { setPatientIdInput(p.patient_id || p.id); searchPatientById(); }} className="px-4 py-2 bg-white border border-gray-200 text-blue-600 hover:bg-blue-50 hover:border-blue-200 font-medium rounded-lg text-sm shadow-sm transition">View Details</button>
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
            <div className="space-y-6 animate-fade-in">
              <h2 className="text-2xl font-bold text-gray-900">Hospital Analytics Overview</h2>
              {analyticsLoading ? <div className="flex justify-center py-10"><LoadingSpinner /></div> : analytics && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="bg-gradient-to-br from-indigo-500 to-indigo-600 p-6 rounded-2xl text-white shadow-lg relative overflow-hidden">
                    <div className="relative z-10"><p className="text-indigo-100 font-medium tracking-wide">Total Patients</p><p className="text-5xl font-extrabold mt-2">{analytics.total_patients}</p></div>
                    <UserGroupIcon className="absolute -right-4 -bottom-4 h-32 w-32 text-white opacity-10" />
                  </div>
                  <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-2xl text-white shadow-lg relative overflow-hidden">
                    <div className="relative z-10"><p className="text-blue-100 font-medium tracking-wide">Analyses Run</p><p className="text-5xl font-extrabold mt-2">{analytics.total_reports}</p></div>
                    <ChartBarIcon className="absolute -right-4 -bottom-4 h-32 w-32 text-white opacity-10" />
                  </div>
                  <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 p-6 rounded-2xl text-white shadow-lg relative overflow-hidden">
                    <div className="relative z-10"><p className="text-emerald-100 font-medium tracking-wide">Recent Uploads</p><p className="text-5xl font-extrabold mt-2">{analytics.recent_uploads}</p></div>
                    <ArrowUpTrayIcon className="absolute -right-4 -bottom-4 h-32 w-32 text-white opacity-10" />
                  </div>
                  <div className="bg-gradient-to-br from-amber-500 to-amber-600 p-6 rounded-2xl text-white shadow-lg relative overflow-hidden">
                    <div className="relative z-10"><p className="text-amber-100 font-medium tracking-wide">Pending Review</p><p className="text-5xl font-extrabold mt-2">{analytics.pending_reports}</p></div>
                    <ClipboardDocumentCheckIcon className="absolute -right-4 -bottom-4 h-32 w-32 text-white opacity-10" />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* MESSAGES TAB */}
          {activeTab === "messages" && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 h-[calc(100vh-140px)] overflow-hidden animate-fade-in flex flex-col">
              <GenericMessaging />
            </div>
          )}
        </main>
      </div>

      {/* Verify Report Modal Override */}
      {verifyingReport && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4 animate-fade-in">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden transform transition-all scale-100">
            <div className="bg-emerald-600 text-white px-6 py-5 flex items-center gap-3">
              <CheckCircleIcon className="h-8 w-8 opacity-80" />
              <div>
                <h3 className="text-xl font-bold tracking-tight">Verify AI Diagnosis</h3>
                <p className="text-emerald-100 text-sm font-medium mt-0.5">{verifyingReport.final_diagnosis.replace(/_/g, " ").toUpperCase()} — Stage {verifyingReport.stage}</p>
              </div>
            </div>
            <div className="p-8 space-y-6 bg-gray-50/50">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm text-center">
                  <span className="text-xs text-gray-500 uppercase tracking-widest font-bold block mb-1">Confidence</span>
                  <p className="text-2xl font-extrabold text-gray-800 flex justify-center"><CountUp to={Number((verifyingReport.confidence * 100).toFixed(1))} direction="up" duration={2} />%</p>
                </div>
                <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm text-center">
                  <span className="text-xs text-gray-500 uppercase tracking-widest font-bold block mb-1">Date</span>
                  <p className="text-xl font-bold text-gray-800 mt-1">{new Date(verifyingReport.created_at).toLocaleDateString()}</p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Clinical Observations (Optional)</label>
                <textarea
                  value={verifyNotes} onChange={(e) => setVerifyNotes(e.target.value)}
                  placeholder="Add qualitative notes regarding patient condition..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-4 focus:ring-emerald-500/20 focus:border-emerald-500 resize-none font-medium text-gray-800 shadow-sm transition" rows={4}
                />
              </div>

              <div className="flex gap-3 justify-end pt-2 border-t border-gray-200 mt-4">
                <button onClick={() => { setVerifyingReport(null); setVerifyNotes(""); }} className="px-6 py-3 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 font-bold transition shadow-sm">Cancel</button>
                <button onClick={() => handleVerifyReport(verifyingReport.id)} disabled={verifyLoading} className="px-6 py-3 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 disabled:opacity-50 font-bold flex items-center gap-2 shadow-md transition">
                  {verifyLoading ? <LoadingSpinner size="sm" /> : <CheckCircleSolid className="h-5 w-5" />} Approve & Finalize
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}