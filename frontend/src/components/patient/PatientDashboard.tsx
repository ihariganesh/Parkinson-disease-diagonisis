import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  DocumentTextIcon, CloudArrowUpIcon, ChartBarIcon, HeartIcon,
  MicrophoneIcon, PencilIcon, BeakerIcon, SparklesIcon,
  ChatBubbleLeftRightIcon, CpuChipIcon,
  MagnifyingGlassIcon, BellIcon,
  ShieldCheckIcon, ClipboardDocumentListIcon, CalendarIcon
} from "@heroicons/react/24/outline";
import CountUp from '../common/CountUp';
import { medicalService } from "../../services";
import { LoadingSpinner, Alert } from "../common";
import type { MedicalData, DiagnosisReport } from "../../types";
import ChatbotView from "./ChatbotView";
import GenericMessaging from "../common/GenericMessaging";
import MagicBento from "../common/MagicBento";

const dataTypeConfig = {
  handwriting: { icon: PencilIcon, title: "Handwriting", color: "text-purple-600", bgColor: "bg-purple-100" },
  voice: { icon: MicrophoneIcon, title: "Voice Recording", color: "text-emerald-600", bgColor: "bg-emerald-100" },
  ecg: { icon: HeartIcon, title: "ECG Data", color: "text-rose-600", bgColor: "bg-rose-100" },
  doctor_notes: { icon: DocumentTextIcon, title: "Doctor Notes", color: "text-indigo-600", bgColor: "bg-indigo-100" },
};

export default function PatientDashboard() {
  const navigate = useNavigate();
  const location = useLocation();

  const [recentData, setRecentData] = useState<MedicalData[]>([]);
  const [recentReports, setRecentReports] = useState<DiagnosisReport[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const initialTab = location.hash ? location.hash.replace('#', '') : 'overview';
  const [activeTab, setActiveTab] = useState<string>(initialTab);

  useEffect(() => {
    if (location.hash) {
      setActiveTab(location.hash.replace('#', ''));
    } else {
      setActiveTab("overview");
    }
  }, [location.hash]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    navigate(`/patient/dashboard#${tabId}`, { replace: true });
  }

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const [dataResult, reportsResult] = await Promise.allSettled([
        medicalService.getMedicalData(undefined, undefined, 1, 5),
        medicalService.getDiagnosisReports(undefined, 1, 3),
      ]);

      if (dataResult.status === 'fulfilled' && dataResult.value.success && dataResult.value.data) {
        setRecentData(dataResult.value.data.items);
      }
      if (reportsResult.status === 'fulfilled' && reportsResult.value.success && reportsResult.value.data) {
        setRecentReports(reportsResult.value.data.items);
      }
      if (dataResult.status === 'rejected' && reportsResult.status === 'rejected') {
        const errMsg = dataResult.reason instanceof Error ? dataResult.reason.message : "Failed to load dashboard data";
        if (!(dataResult.reason as any)?.statusCode || (dataResult.reason as any).statusCode !== 401) {
          setError(errMsg);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard data");
    } finally {
      setIsLoading(false);
    }
  };



  if (isLoading) {
    return <div className="flex h-screen items-center justify-center bg-slate-50"><LoadingSpinner size="lg" /></div>;
  }

  return (
    <div className="flex bg-slate-50 font-sans min-h-[calc(100vh-4rem)]">
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="bg-white border-b border-slate-200 flex items-center justify-between px-8 py-5 shadow-sm z-10 sticky top-0">
          <div className="flex items-center gap-4">
            <div>
              <h1 className="text-2xl font-extrabold text-slate-800 capitalize tracking-tight">{activeTab.replace('-', ' ')}</h1>
              <p className="text-sm font-medium text-slate-500 hidden sm:block">Monitor your health parameters and stay directly connected.</p>
            </div>
          </div>
          <div className="flex items-center gap-5">
            <div className="relative hidden md:block">
              <input type="text" placeholder="Search my records..." className="pl-11 pr-4 py-2.5 bg-slate-100 border-none rounded-full text-sm font-medium focus:ring-2 focus:ring-indigo-500 w-64 transition-all focus:bg-white focus:shadow-md" />
              <MagnifyingGlassIcon className="h-5 w-5 text-slate-400 absolute left-4 top-2.5" />
            </div>
            <button className="p-2.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition-colors relative shadow-sm border border-slate-100 block">
              <BellIcon className="h-6 w-6" />
              <span className="absolute top-2 right-2 h-2.5 w-2.5 bg-rose-500 rounded-full border-2 border-white animate-pulse"></span>
            </button>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-slate-50 p-4 sm:p-8">
          {error && <Alert type="error" message={error} onClose={() => setError("")} className="mb-6 shadow-sm rounded-xl" />}

          {/* OVERVIEW TAB */}
          {activeTab === "overview" && (
            <div className="space-y-8 animate-fade-in max-w-7xl mx-auto">

              {/* Comprehensive Analysis Banner CTA */}
              <div className="bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 rounded-3xl p-8 sm:p-10 text-white shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>
                <div className="relative z-10 grid lg:grid-cols-5 gap-8 items-center">
                  <div className="lg:col-span-3">
                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/20 rounded-full text-sm font-bold tracking-wide mb-4 backdrop-blur-sm border border-white/30">
                      <SparklesIcon className="h-4 w-4 text-yellow-300" /> New Premium Feature
                    </div>
                    <h2 className="text-3xl sm:text-4xl font-extrabold mb-4 leading-tight">
                      Multimodal Parkinson's Assessment
                    </h2>
                    <p className="text-indigo-100 mb-8 text-lg font-medium leading-relaxed max-w-xl">
                      Combine your Voice, Handwriting, and Medical records into one single AI process to achieve maximum clinical accuracy and personalized recommendations.
                    </p>
                    <button onClick={() => navigate("/comprehensive")} className="bg-white text-indigo-700 hover:bg-slate-50 font-extrabold py-4 px-8 rounded-2xl transition duration-300 hover:scale-105 hover:shadow-[0_0_20px_rgba(255,255,255,0.3)] inline-flex items-center text-lg shadow-xl group">
                      <CloudArrowUpIcon className="h-6 w-6 mr-3 group-hover:-translate-y-1 transition-transform" />
                      Run Standard Scan Now
                    </button>
                  </div>
                  <div className="hidden lg:block lg:col-span-2">
                    <MagicBento
                      items={[
                        { icon: PencilIcon, label: "Drawing", desc: "Motor test" },
                        { icon: MicrophoneIcon, label: "Audio", desc: "Vocal test" },
                        { icon: ShieldCheckIcon, label: "AI Results", desc: "High confidence", col: "col-span-2" }
                      ]}
                      enableStars
                      enableSpotlight
                      enableBorderGlow
                      enableTilt={false}
                      enableMagnetism={false}
                      clickEffect
                      spotlightRadius={400}
                      particleCount={12}
                      glowColor="255, 255, 255"
                      disableAnimations={false}
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Recent Reports Card */}
                <div className="bg-white rounded-3xl p-6 lg:p-8 border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-center border-b border-slate-100 pb-5 mb-5">
                    <h2 className="text-xl font-extrabold text-slate-800 flex items-center gap-2">
                      <ChartBarIcon className="h-6 w-6 text-indigo-500" /> Diagnostics History
                    </h2>
                    <button onClick={() => handleTabChange('history')} className="text-indigo-600 font-bold text-sm hover:text-indigo-800 bg-indigo-50 px-3 py-1.5 rounded-lg">View All</button>
                  </div>
                  <div className="space-y-4">
                    {recentReports.length === 0 ? (
                      <div className="text-center py-10 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                        <DocumentTextIcon className="h-12 w-12 text-slate-300 mx-auto mb-3" />
                        <p className="text-slate-500 font-medium">No diagnostic reports available.</p>
                      </div>
                    ) : (
                      recentReports.map(report => (
                        <div key={report.id} className="p-5 border border-slate-100 hover:border-indigo-100 bg-slate-50/50 hover:bg-indigo-50/30 rounded-2xl transition-colors cursor-pointer group">
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <h3 className="font-bold text-slate-800 group-hover:text-indigo-700 transition-colors">AI Analysis Result</h3>
                              <p className="text-xs font-semibold text-slate-500 mt-1 flex items-center gap-1"><CalendarIcon className="h-3 w-3" /> {new Date(report.createdAt).toLocaleDateString()}</p>
                            </div>
                            <span className={`px-3 py-1 rounded-full text-xs font-bold shadow-sm ${report.finalDiagnosis === 'healthy' || (report as any).final_diagnosis === 'healthy' ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' : 'bg-rose-100 text-rose-800 border border-rose-200'}`}>
                              {(report.finalDiagnosis || (report as any).final_diagnosis).replace("_", " ").toUpperCase()}
                            </span>
                          </div>
                          <div className="flex items-center gap-4 bg-white p-3 rounded-xl border border-slate-100 shadow-sm mt-3">
                            <div className="flex-1">
                              <p className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-1">Confidence Score</p>
                              <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                                <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${Math.round(report.confidence * 100)}%` }}></div>
                              </div>
                            </div>
                            <span className="font-extrabold text-indigo-700 flex"><CountUp to={Math.round(report.confidence * 100)} direction="up" duration={2} />%</span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* Uploaded Documents */}
                <div className="bg-white rounded-3xl p-6 lg:p-8 border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-5 mb-5">
                    <h2 className="text-xl font-extrabold text-slate-800 flex items-center gap-2">
                      <CloudArrowUpIcon className="h-6 w-6 text-emerald-500" /> Recent Uploads
                    </h2>
                  </div>
                  <div className="space-y-4">
                    {recentData.length === 0 ? (
                      <div className="text-center py-10 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                        <BeakerIcon className="h-12 w-12 text-slate-300 mx-auto mb-3" />
                        <p className="text-slate-500 font-medium">No medical data uploaded yet.</p>
                      </div>
                    ) : (
                      recentData.map(data => {
                        const config = dataTypeConfig[data.type as keyof typeof dataTypeConfig] || dataTypeConfig.doctor_notes;
                        return (
                          <div key={data.id} className="flex items-center p-4 bg-white border border-slate-100 shadow-sm rounded-2xl hover:border-emerald-200 transition-colors">
                            <div className={`p-3 rounded-xl ${config.bgColor} ${config.color} shadow-sm border border-white`}>
                              <config.icon className="h-6 w-6" />
                            </div>
                            <div className="ml-4 flex-1">
                              <p className="font-bold text-slate-800">{data.fileName}</p>
                              <p className="text-xs font-medium text-slate-500 mt-0.5">{new Date(data.uploadedAt || (data as any).created_at).toLocaleDateString()}</p>
                            </div>
                            {((data as any).analysis_result || data.analysisResult) ? (
                              <span className="px-3 py-1 bg-emerald-50 text-emerald-700 text-xs font-extrabold rounded-full border border-emerald-200">Analyzed</span>
                            ) : (
                              <span className="px-3 py-1 bg-amber-50 text-amber-700 text-xs font-extrabold rounded-full border border-amber-200">Pending</span>
                            )}
                          </div>
                        )
                      })
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* CHATBOT TAB */}
          {activeTab === "chatbot" && (
            <div className="animate-fade-in max-w-5xl mx-auto bg-white rounded-3xl shadow-lg border border-slate-100 overflow-hidden h-[calc(100vh-140px)] flex flex-col">
              <div className="bg-gradient-to-r from-indigo-50 to-white px-8 py-6 border-b border-indigo-100 flex items-center gap-4 shrink-0">
                <div className="p-3 bg-indigo-600 rounded-2xl shadow-lg text-white"><CpuChipIcon className="h-8 w-8" /></div>
                <div>
                  <h2 className="text-2xl font-extrabold text-slate-800">Your AI Health Assistant</h2>
                  <p className="text-indigo-600/80 font-medium text-sm mt-1">Powered by advanced conversational AI models</p>
                </div>
              </div>
              <div className="flex-1 overflow-hidden relative bg-slate-50/30">
                <ChatbotView />
              </div>
            </div>
          )}

          {/* MESSAGES TAB */}
          {activeTab === "messages" && (
            <div className="animate-fade-in max-w-5xl mx-auto bg-white rounded-3xl shadow-lg border border-slate-100 overflow-hidden h-[calc(100vh-140px)] flex flex-col">
              <div className="bg-gradient-to-r from-emerald-50 to-white px-8 py-6 border-b border-emerald-100 flex items-center gap-4 shrink-0">
                <div className="p-3 bg-emerald-600 rounded-2xl shadow-lg text-white"><ChatBubbleLeftRightIcon className="h-8 w-8" /></div>
                <div>
                  <h2 className="text-2xl font-extrabold text-slate-800">Medical Messaging</h2>
                  <p className="text-emerald-700/80 font-medium text-sm mt-1">Direct encrypted connection with your specialists</p>
                </div>
              </div>
              <div className="flex-1 overflow-hidden bg-slate-50/30 p-2">
                <GenericMessaging />
              </div>
            </div>
          )}

          {/* HISTORY FALLBACK TAB */}
          {activeTab === "history" && (
            <div className="animate-fade-in max-w-7xl mx-auto">
              <div className="bg-white rounded-3xl p-8 border border-slate-100 shadow-sm">
                <h2 className="text-3xl font-extrabold text-slate-800 mb-8 flex items-center gap-3">
                  <ClipboardDocumentListIcon className="h-8 w-8 text-indigo-600" /> Full Medical History
                </h2>
                <p className="text-slate-500 font-medium pb-8 border-b border-slate-100 text-lg">Browse all past reports and uploaded datasets in one consolidated view.</p>

                <div className="mt-8 space-y-6">
                  {recentReports.length === 0 && recentData.length === 0 ? (
                    <p className="text-center py-20 text-slate-400 font-bold bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200 text-lg">No records available.</p>
                  ) : (
                    <div className="grid md:grid-cols-2 gap-8">
                      <div>
                        <h3 className="font-bold text-slate-700 uppercase tracking-widest text-sm mb-4">Diagnostics</h3>
                        {recentReports.map(rep => (
                          <div key={rep.id} className="p-4 bg-slate-50 border border-slate-200 rounded-2xl mb-3 shadow-sm hover:border-indigo-300 transition-colors">
                            <p className="font-bold text-slate-800 mb-1">{new Date(rep.createdAt || (rep as any).created_at).toLocaleDateString()}</p>
                            <p className="text-indigo-600 font-bold uppercase text-sm">{(rep.finalDiagnosis || (rep as any).final_diagnosis).replace("_", " ")}</p>
                          </div>
                        ))}
                      </div>
                      <div>
                        <h3 className="font-bold text-slate-700 uppercase tracking-widest text-sm mb-4">Raw Uploads</h3>
                        {recentData.map(dat => (
                          <div key={dat.id} className="p-4 bg-slate-50 border border-slate-200 rounded-2xl mb-3 shadow-sm hover:border-emerald-300 transition-colors">
                            <p className="font-bold text-slate-800 mb-1">{new Date(dat.uploadedAt || (dat as any).created_at).toLocaleDateString()}</p>
                            <p className="text-emerald-600 font-bold text-sm tracking-wide">{dat.fileName}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

        </main>
      </div>
    </div>
  );
}
