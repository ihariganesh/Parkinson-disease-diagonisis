import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { medicalService } from '../services/medical';
import axios from 'axios';
import {
  SparklesIcon,
  UserIcon,
  MapPinIcon,
  CalendarIcon,
  HeartIcon,
  FireIcon,
  MoonIcon,
  FaceSmileIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  ArrowPathIcon,
  CpuChipIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import CountUp from '../components/common/CountUp';

interface RecommendationDetail {
  category: string;
  recommendation: string;
  details: string[];
  priority: string;
  ai_note?: string;
}

interface PredictionInput {
  gender: string;
  age: number;
  age_group: string;
  location: { city: string; state: string };
  previous_condition: string;
  parkinson_status: number;
  parkinson_stage: number;
  parkinson_stage_label: string;
}

interface PredictionResult {
  success: boolean;
  source: string;
  llama_validated: boolean;
  llama_available: boolean;
  corrections_made: boolean;
  general_advice?: string;
  input: PredictionInput;
  recommendations: {
    exercise: RecommendationDetail;
    diet: RecommendationDetail;
    sleep: RecommendationDetail;
    stress_management: RecommendationDetail;
  };
  model_accuracy: number;
}

const HEALTH_CONDITIONS = [
  { value: 'None', label: 'No previous conditions' },
  { value: 'Diabetes', label: 'Diabetes' },
  { value: 'Hypertension', label: 'Hypertension (High BP)' },
  { value: 'Heart Disease', label: 'Heart Disease' },
  { value: 'Arthritis', label: 'Arthritis / Joint Pain' },
  { value: 'Obesity', label: 'Obesity' },
  { value: 'Hypertension + Diabetes', label: 'Hypertension + Diabetes' },
];

const PARKINSON_STAGES = [
  { value: 0, label: 'No Parkinson (Healthy)', statusLabel: 'Healthy', color: 'text-green-700 bg-green-50 border-green-300', emoji: '🟢' },
  { value: 1, label: 'Early Stage (Mild Symptoms)', statusLabel: 'Early', color: 'text-yellow-700 bg-yellow-50 border-yellow-300', emoji: '🟡' },
  { value: 2, label: 'Moderate Stage', statusLabel: 'Moderate', color: 'text-orange-700 bg-orange-50 border-orange-300', emoji: '🟠' },
  { value: 3, label: 'Advanced Stage', statusLabel: 'Advanced', color: 'text-red-700 bg-red-50 border-red-300', emoji: '🔴' },
];

const CITIES = [
  'Chennai', 'Bangalore', 'Hyderabad', 'Coimbatore', 'Mumbai',
  'Madurai', 'Salem', 'Erode', 'Karur', 'Other',
];

const STATES = [
  { value: 'TN', label: 'Tamil Nadu' },
  { value: 'KA', label: 'Karnataka' },
  { value: 'TS', label: 'Telangana' },
  { value: 'MH', label: 'Maharashtra' },
  { value: 'Other', label: 'Other' },
];

const RecommendationsPage = () => {
  const { state: authState } = useAuth();
  const [loading, setLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PredictionResult | null>(null);

  // Form state
  const [gender, setGender] = useState('Male');
  const [age, setAge] = useState<number>(50);
  const [city, setCity] = useState('Chennai');
  const [stateVal, setStateVal] = useState('TN');
  const [previousCondition, setPreviousCondition] = useState('None');

  // Parkinson stage — auto-loaded from diagnosis, NOT user-editable
  const [parkinsonStage, setParkinsonStage] = useState(0);
  const [diagnosisLoaded, setDiagnosisLoaded] = useState(false);
  const [diagnosisDate, setDiagnosisDate] = useState<string | null>(null);
  const [diagnosisConfidence, setDiagnosisConfidence] = useState<number>(0);
  const [noDiagnosisFound, setNoDiagnosisFound] = useState(false);

  // Load profile + latest diagnosis on mount
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setPageLoading(true);
    try {
      // Fetch user profile
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const profileResponse = await axios.get(
            `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/patients/profile`,
            { headers: { Authorization: `Bearer ${token}` } }
          );
          const profile = profileResponse.data;
          if (profile.gender) setGender(profile.gender === 'female' ? 'Female' : 'Male');
          if (profile.date_of_birth) {
            const today = new Date();
            const birth = new Date(profile.date_of_birth);
            let calculatedAge = today.getFullYear() - birth.getFullYear();
            const m = today.getMonth() - birth.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) calculatedAge--;
            if (calculatedAge > 0 && calculatedAge < 120) setAge(calculatedAge);
          }
          if (profile.address_city) setCity(profile.address_city);
          if (profile.address_state) setStateVal(profile.address_state);
        } catch {
          // Profile fetch failed — user can fill manually
        }
      }

      // Fetch latest diagnosis report to get Parkinson's stage
      try {
        const reportsResponse = await medicalService.getDiagnosisReports(
          authState.user?.id, 1, 1
        );
        if (
          reportsResponse.success &&
          reportsResponse.data?.items &&
          reportsResponse.data.items.length > 0
        ) {
          const latestReport = reportsResponse.data.items[0];
          const stage = latestReport.stage ?? 0;
          setParkinsonStage(Math.min(3, Math.max(0, stage)));
          setDiagnosisLoaded(true);
          setDiagnosisDate(latestReport.createdAt);
          setDiagnosisConfidence(latestReport.confidence ?? 0);
        } else {
          setNoDiagnosisFound(true);
        }
      } catch {
        setNoDiagnosisFound(true);
      }
    } finally {
      setPageLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const address = `${city} ${stateVal} India`;
      const parkinsonStatus = parkinsonStage > 0 ? 1 : 0;

      const response = await axios.post(
        `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/lifestyle-ml/predict`,
        {
          gender,
          age,
          address,
          previous_condition: previousCondition,
          parkinson_status: parkinsonStatus,
          parkinson_stage: parkinsonStage,
        }
      );
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to get recommendations');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryIcon = (key: string) => {
    switch (key) {
      case 'exercise': return FireIcon;
      case 'diet': return HeartIcon;
      case 'sleep': return MoonIcon;
      case 'stress_management': return FaceSmileIcon;
      default: return SparklesIcon;
    }
  };

  const getCategoryGradient = (key: string) => {
    switch (key) {
      case 'exercise': return 'from-orange-500 to-red-500';
      case 'diet': return 'from-green-500 to-emerald-600';
      case 'sleep': return 'from-indigo-500 to-purple-600';
      case 'stress_management': return 'from-pink-500 to-rose-500';
      default: return 'from-blue-500 to-indigo-600';
    }
  };

  const getCategoryBg = (key: string) => {
    switch (key) {
      case 'exercise': return 'bg-orange-50 border-orange-200';
      case 'diet': return 'bg-green-50 border-green-200';
      case 'sleep': return 'bg-indigo-50 border-indigo-200';
      case 'stress_management': return 'bg-pink-50 border-pink-200';
      default: return 'bg-blue-50 border-blue-200';
    }
  };

  const getPriorityBadge = (priority: string) => {
    if (priority === 'high') return 'bg-red-100 text-red-700 border-red-300';
    return 'bg-amber-100 text-amber-700 border-amber-300';
  };

  const selectedStageInfo = PARKINSON_STAGES[parkinsonStage];

  if (pageLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto" />
          <p className="mt-4 text-gray-600">Loading your health data & diagnosis...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <SparklesIcon className="h-8 w-8 text-purple-600" />
            AI Lifestyle Recommendations
          </h1>
          <p className="mt-2 text-gray-600">
            Personalized health guidance powered by our ML model trained on <strong>12,000+</strong> Parkinson's health profiles
          </p>
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-purple-100 rounded-xl p-2">
              <CpuChipIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Your Health Profile</h2>
              <p className="text-sm text-gray-500">Your Parkinson's stage is auto-detected from your latest analysis</p>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Parkinson's Stage — READ-ONLY from system diagnosis */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                <ShieldCheckIcon className="inline h-4 w-4 mr-1 text-gray-400" />
                Parkinson's Diagnosis Stage
                <span className="ml-2 text-xs font-normal text-gray-400">(Auto-detected from your analysis)</span>
              </label>

              {noDiagnosisFound ? (
                <div className="bg-amber-50 border-2 border-amber-200 rounded-xl p-4 flex items-start gap-3">
                  <ExclamationTriangleIcon className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-amber-900">No diagnosis report found</p>
                    <p className="text-xs text-amber-700 mt-1">
                      Please complete a Parkinson's analysis first (upload DaT scan, handwriting, or voice data)
                      to get stage-specific recommendations. Defaulting to Stage 0 (Healthy).
                    </p>
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {PARKINSON_STAGES.map((stage) => {
                    const isActive = parkinsonStage === stage.value;
                    return (
                      <div
                        key={stage.value}
                        className={`py-4 px-4 rounded-xl border-2 font-medium text-center transition-all duration-200 ${isActive
                          ? `${stage.color} shadow-lg scale-[1.02] ring-2 ring-offset-2 ${stage.value === 0 ? 'ring-green-400' :
                            stage.value === 1 ? 'ring-yellow-400' :
                              stage.value === 2 ? 'ring-orange-400' : 'ring-red-400'
                          }`
                          : 'border-gray-100 bg-gray-50 text-gray-300 cursor-not-allowed opacity-50'
                          }`}
                      >
                        <span className="text-2xl block mb-1">{stage.emoji}</span>
                        <span className="text-sm font-bold block">{stage.statusLabel}</span>
                        <span className="text-xs opacity-75 block mt-0.5">Stage {stage.value}</span>
                      </div>
                    );
                  })}
                </div>
              )}

              {diagnosisLoaded && (
                <div className="flex items-center gap-4 mt-3 text-xs text-gray-400">
                  <span>
                    <CheckCircleIcon className="inline h-3.5 w-3.5 text-green-500 mr-1" />
                    Detected: <strong className="text-gray-600">{selectedStageInfo.label}</strong>
                  </span>
                  <span className="flex">
                    Confidence: <strong className="text-gray-600 ml-1 flex"><CountUp to={Number((diagnosisConfidence * 100).toFixed(1))} direction="up" duration={2} />%</strong>
                  </span>
                  {diagnosisDate && (
                    <span>
                      Analysis date: <strong className="text-gray-600">{new Date(diagnosisDate).toLocaleDateString()}</strong>
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Row 1: Gender, Age, Previous Condition */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              {/* Gender */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <UserIcon className="inline h-4 w-4 mr-1 text-gray-400" />
                  Gender
                </label>
                <div className="flex gap-3">
                  {['Male', 'Female'].map((g) => (
                    <button
                      type="button"
                      key={g}
                      onClick={() => setGender(g)}
                      className={`flex-1 py-3 px-4 rounded-xl border-2 font-medium transition-all duration-200 ${gender === g
                        ? 'border-purple-500 bg-purple-50 text-purple-700 shadow-md'
                        : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                        }`}
                    >
                      {g === 'Male' ? '👨' : '👩'} {g}
                    </button>
                  ))}
                </div>
              </div>

              {/* Age */}
              <div>
                <label htmlFor="age" className="block text-sm font-medium text-gray-700 mb-2">
                  <CalendarIcon className="inline h-4 w-4 mr-1 text-gray-400" />
                  Age
                </label>
                <input
                  id="age"
                  type="number"
                  min={18}
                  max={120}
                  value={age}
                  onChange={(e) => setAge(parseInt(e.target.value) || 30)}
                  className="w-full py-3 px-4 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all text-lg font-medium"
                />
                <p className="text-xs text-gray-400 mt-1">
                  Age group: {age < 45 ? '🟢 Young' : age < 55 ? '🟡 Middle-aged' : age < 65 ? '🟠 Senior' : age < 75 ? '🔴 Elderly' : '⚫ Very Elderly'}
                </p>
              </div>

              {/* Previous Health Condition */}
              <div>
                <label htmlFor="condition" className="block text-sm font-medium text-gray-700 mb-2">
                  <HeartIcon className="inline h-4 w-4 mr-1 text-gray-400" />
                  Previous Health Condition
                </label>
                <select
                  id="condition"
                  value={previousCondition}
                  onChange={(e) => setPreviousCondition(e.target.value)}
                  className="w-full py-3 px-4 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all bg-white"
                >
                  {HEALTH_CONDITIONS.map((c) => (
                    <option key={c.value} value={c.value}>{c.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Row 2: Location + Submit */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* City */}
              <div>
                <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-2">
                  <MapPinIcon className="inline h-4 w-4 mr-1 text-gray-400" />
                  City
                </label>
                <select
                  id="city"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  className="w-full py-3 px-4 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all bg-white"
                >
                  {CITIES.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              {/* State */}
              <div>
                <label htmlFor="state" className="block text-sm font-medium text-gray-700 mb-2">
                  <MapPinIcon className="inline h-4 w-4 mr-1 text-gray-400" />
                  State
                </label>
                <select
                  id="state"
                  value={stateVal}
                  onChange={(e) => setStateVal(e.target.value)}
                  className="w-full py-3 px-4 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all bg-white"
                >
                  {STATES.map((s) => (
                    <option key={s.value} value={s.value}>{s.label}</option>
                  ))}
                </select>
              </div>

              {/* Submit */}
              <div className="flex items-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 px-6 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <ArrowPathIcon className="h-5 w-5 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="h-5 w-5" />
                      Get Recommendations
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-8 bg-red-50 border-2 border-red-200 rounded-xl p-6">
            <div className="flex items-center gap-3">
              <ExclamationCircleIcon className="h-6 w-6 text-red-600" />
              <p className="text-red-800 font-medium">{error}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-8">
            {/* Summary Card */}
            <div className="bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 rounded-2xl p-8 text-white shadow-2xl">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <CpuChipIcon className="h-8 w-8" />
                  <h2 className="text-2xl font-bold">Your Personalized Recommendations</h2>
                </div>
                <div className="flex gap-2 flex-wrap">
                  <span className="bg-white/20 backdrop-blur-sm rounded-full px-4 py-1 text-sm font-medium">
                    🤖 ML Model
                  </span>
                  {result.llama_validated ? (
                    <span className={`backdrop-blur-sm rounded-full px-4 py-1 text-sm font-medium ${result.corrections_made
                      ? 'bg-yellow-400/30 text-yellow-100'
                      : 'bg-green-400/30 text-green-100'
                      }`}>
                      {result.corrections_made ? '✏️ Llama Refined' : '✅ Llama Verified'}
                    </span>
                  ) : (
                    <span className="bg-white/10 backdrop-blur-sm rounded-full px-4 py-1 text-sm font-medium text-white/60">
                      ⚠️ Llama Offline
                    </span>
                  )}
                  <span className="bg-white/20 backdrop-blur-sm rounded-full px-4 py-1 text-sm font-medium flex items-center">
                    <CountUp to={Number((result.model_accuracy * 100).toFixed(1))} direction="up" duration={2} className="mr-1" />% Accuracy
                  </span>
                </div>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 text-center">
                  <p className="text-xs text-blue-100">Gender</p>
                  <p className="font-bold">{result.input.gender === 'Male' ? '👨' : '👩'} {result.input.gender}</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 text-center">
                  <p className="text-xs text-blue-100">Age</p>
                  <p className="font-bold">{result.input.age} yrs</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 text-center">
                  <p className="text-xs text-blue-100">Location</p>
                  <p className="font-bold">{result.input.location?.city || 'N/A'}</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 text-center">
                  <p className="text-xs text-blue-100">Condition</p>
                  <p className="font-bold text-sm">{result.input.previous_condition === 'None' ? 'Healthy' : result.input.previous_condition}</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 text-center">
                  <p className="text-xs text-blue-100">Parkinson's</p>
                  <p className="font-bold">
                    {result.input.parkinson_status === 0 ? '🟢 No' : '🔴 Yes'}
                  </p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 text-center">
                  <p className="text-xs text-blue-100">PD Stage</p>
                  <p className="font-bold text-sm">
                    {PARKINSON_STAGES[result.input.parkinson_stage]?.emoji || ''}{' '}
                    {result.input.parkinson_stage_label}
                  </p>
                </div>
              </div>
            </div>

            {/* PD Warning Banner (for stage >= 2) */}
            {result.input.parkinson_stage >= 2 && (
              <div className="bg-orange-50 border-2 border-orange-300 rounded-xl p-5">
                <div className="flex items-start gap-3">
                  <ExclamationTriangleIcon className="h-6 w-6 text-orange-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-bold text-orange-900 mb-1">
                      {result.input.parkinson_stage === 3 ? '⚠️ Advanced Stage Care Notice' : '⚠️ Moderate Stage Care Notice'}
                    </h3>
                    <p className="text-sm text-orange-800">
                      At {result.input.parkinson_stage_label?.toLowerCase()}, the recommendations include
                      additional safety precautions. Always exercise under supervision and consult your
                      neurologist before changing your routine.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Recommendation Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {Object.entries(result.recommendations).map(([key, rec]) => {
                const Icon = getCategoryIcon(key);
                const gradient = getCategoryGradient(key);
                const bgClass = getCategoryBg(key);
                const priorityClass = getPriorityBadge(rec.priority);

                return (
                  <div
                    key={key}
                    className={`rounded-2xl border-2 overflow-hidden shadow-md hover:shadow-xl transition-all duration-300 ${bgClass}`}
                  >
                    {/* Card Header */}
                    <div className={`bg-gradient-to-r ${gradient} px-6 py-4`}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="bg-white/20 backdrop-blur-sm rounded-xl p-2">
                            <Icon className="h-6 w-6 text-white" />
                          </div>
                          <h3 className="text-lg font-bold text-white">{rec.category}</h3>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${priorityClass}`}>
                          {rec.priority.toUpperCase()}
                        </span>
                      </div>
                    </div>

                    {/* Main Recommendation */}
                    <div className="px-6 py-4">
                      <div className="bg-white rounded-xl p-4 border border-gray-200 mb-4 shadow-sm">
                        <div className="flex items-center gap-2 mb-1">
                          {result.corrections_made ? (
                            <>
                              <span className="text-base">🦙</span>
                              <span className="text-xs font-semibold text-orange-600 uppercase tracking-wide">Llama Corrected</span>
                            </>
                          ) : (
                            <>
                              <CheckCircleIcon className="h-5 w-5 text-green-600" />
                              <span className="text-xs font-semibold text-green-600 uppercase tracking-wide">
                                {result.llama_validated ? 'Llama Verified ✓' : 'ML Recommended'}
                              </span>
                            </>
                          )}
                        </div>
                        <p className="text-lg font-bold text-gray-900">{rec.recommendation}</p>
                      </div>

                      {/* Detailed Tips */}
                      <h4 className="text-sm font-semibold text-gray-600 mb-3 uppercase tracking-wide">Action Items</h4>
                      <ul className="space-y-3">
                        {rec.details.map((detail, idx) => (
                          <li key={idx} className="flex items-start gap-3 group">
                            <div className="flex-shrink-0 mt-1">
                              <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${gradient} group-hover:scale-150 transition-transform duration-200`} />
                            </div>
                            <p className="text-gray-700 text-sm leading-relaxed">{detail}</p>
                          </li>
                        ))}
                      </ul>

                      {/* Llama AI Note */}
                      {rec.ai_note && (
                        <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
                          <div className="flex items-start gap-2">
                            <span className="text-base flex-shrink-0">🦙</span>
                            <div>
                              <span className="text-xs font-bold text-blue-700 uppercase tracking-wide">Llama 3.2 Note</span>
                              <p className="text-xs text-blue-800 mt-0.5 leading-relaxed">{rec.ai_note}</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Llama General Advice */}
            {result.general_advice && (
              <div className="bg-blue-50 border-2 border-blue-200 rounded-2xl p-6">
                <div className="flex items-start gap-3">
                  <span className="text-3xl flex-shrink-0">🦙</span>
                  <div>
                    <h3 className="font-bold text-blue-900 mb-2 flex items-center gap-2">
                      Llama 3.2 — Overall Assessment
                      {result.corrections_made && (
                        <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full font-medium">
                          Corrections Applied
                        </span>
                      )}
                    </h3>
                    <p className="text-sm text-blue-800 leading-relaxed">{result.general_advice}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Model Info */}
            <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-center gap-3">
              <CpuChipIcon className="h-5 w-5 text-green-600" />
              <p className="text-sm text-green-800">
                ML model trained on <strong>12,000 health profiles</strong> (<span className="inline-flex"><CountUp to={Number((result.model_accuracy * 100).toFixed(1))} direction="up" duration={2} />% accuracy</span>)
                {result.llama_validated && ' → Validated by Llama 3.2'}
                . PD stage auto-detected from your latest diagnosis.
              </p>
            </div>

            {/* Disclaimer */}
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
              <div className="flex items-start gap-3">
                <ShieldCheckIcon className="h-6 w-6 text-amber-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-amber-800">
                  <p className="font-semibold mb-1">Medical Disclaimer</p>
                  <p>
                    These AI-generated recommendations are based on patterns in health data and are for
                    informational purposes only. Always consult your neurologist and healthcare provider
                    before making changes to your lifestyle, diet, or treatment plan.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!result && !loading && !error && (
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-16 text-center">
            <SparklesIcon className="h-20 w-20 text-purple-300 mx-auto mb-6" />
            <h3 className="text-2xl font-bold text-gray-900 mb-3">
              Get Personalized Lifestyle Recommendations
            </h3>
            <p className="text-gray-500 max-w-lg mx-auto mb-8">
              Your Parkinson's stage is automatically detected from your latest analysis.
              Fill in your personal details and click "Get Recommendations" for tailored
              exercise, diet, sleep, and stress management guidance.
            </p>
            <div className="flex justify-center gap-8 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <FireIcon className="h-5 w-5 text-orange-400" /> Exercise
              </div>
              <div className="flex items-center gap-2">
                <HeartIcon className="h-5 w-5 text-green-400" /> Diet
              </div>
              <div className="flex items-center gap-2">
                <MoonIcon className="h-5 w-5 text-indigo-400" /> Sleep
              </div>
              <div className="flex items-center gap-2">
                <FaceSmileIcon className="h-5 w-5 text-pink-400" /> Stress
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecommendationsPage;
