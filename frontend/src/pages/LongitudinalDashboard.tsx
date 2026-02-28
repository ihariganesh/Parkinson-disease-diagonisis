import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/api'; // Or standard fetch/axios config
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  BarChart,
  Bar,
} from 'recharts';
import {
  ArrowTrendingUpIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  ChartBarSquareIcon,
  HeartIcon,
  CpuChipIcon,
} from '@heroicons/react/24/outline';
import { Alert, LoadingSpinner } from '../components/common';
import CountUp from '../components/common/CountUp';

interface TimeSeriesPoint {
  timestamp: string;
  modality: string;
  biomarker: string;
  value: number;
}

interface LongitudinalData {
  risk_score: number;
  velocity: number;
  acceleration: number;
  agreement: number;
  confidence: number;
  risk_delta_since_last: number;
  data_span_months: number;
  time_series_data: TimeSeriesPoint[];
  risk_stage: string;
}

export default function LongitudinalDashboard() {
  const { state } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<LongitudinalData | null>(null);

  useEffect(() => {
    async function loadData() {
      if (!state.user?.id) return;
      try {
        setLoading(true);
        // The endpoint we just created
        const res: unknown = await apiClient.get(`/patients/${state.user.id}/progression`);
        // apiClient unwraps axios response.data. If the backend returns { risk_score: ... }, res IS the data.
        setData((res as { data?: LongitudinalData }).data || (res as LongitudinalData));
      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('Failed to load progression data');
        }
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [state.user?.id]);

  // Aggregation for the Time-series Line Chart
  const timelineData = useMemo(() => {
    if (!data?.time_series_data) return [];

    // Group values by date (YYYY-MM-DD)
    const groups: Record<string, Record<string, string | number>> = {};

    data.time_series_data.forEach((pt: TimeSeriesPoint) => {
      // Just take the date part
      const dateKey = new Date(pt.timestamp).toISOString().split('T')[0];
      if (!groups[dateKey]) {
        groups[dateKey] = { date: dateKey };
      }

      // Keep a running average for each modality per day
      if (!groups[dateKey][pt.modality]) {
        groups[dateKey][pt.modality] = pt.value;
        groups[dateKey][pt.modality + "_count"] = 1;
      } else {
        (groups[dateKey][pt.modality] as number) += pt.value;
        (groups[dateKey][pt.modality + "_count"] as number) += 1;
      }

      // Calculate 'overall' proxy
      if (!groups[dateKey].overall) {
        groups[dateKey].overall = pt.value;
        groups[dateKey].overall_count = 1;
      } else {
        (groups[dateKey].overall as number) += pt.value;
        (groups[dateKey].overall_count as number) += 1;
      }
    });

    // Average them out
    return Object.values(groups).map((g: Record<string, string | number>) => {
      const res: Record<string, string | number> = { date: g.date as string };
      if (g.handwriting) res.handwriting = (g.handwriting as number) / (g.handwriting_count as number);
      if (g.voice) res.voice = (g.voice as number) / (g.voice_count as number);
      if (g.dat_scan) res.dat_scan = (g.dat_scan as number) / (g.dat_scan_count as number);
      if (g.overall) res.overall = (g.overall as number) / (g.overall_count as number);
      return res;
    }).sort((a, b) => new Date(a.date as string).getTime() - new Date(b.date as string).getTime());
  }, [data]);


  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <Alert type="error" message={error} onClose={() => setError(null)} />
      </div>
    );
  }

  if (!data) return null;

  // Formatting helpers
  const riskColor =
    data.risk_stage === 'Stable' ? 'text-emerald-600 bg-emerald-100' :
      data.risk_stage === 'Emerging Risk' ? 'text-amber-600 bg-amber-100' :
        data.risk_stage === 'Progressive Risk' ? 'text-orange-600 bg-orange-100' :
          'text-rose-600 bg-rose-100';

  const formatPercent = (val: number) => `${Math.round(val * 100)}%`;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 font-sans bg-slate-50 min-h-screen">

      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-3">
          <ChartBarSquareIcon className="h-8 w-8 text-indigo-600" />
          Longitudinal Progression Engine
        </h1>
        <p className="mt-2 text-slate-500 font-medium max-w-3xl">
          Advanced temporal modeling of neuro-motor biomarkers. This engine calculates rate of change, cross-modality agreement, and acceleration to determine clinical progression phase.
        </p>
      </div>

      {/* SECTION 1: Progression Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <div className="bg-white rounded-3xl p-6 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-slate-100 flex flex-col justify-between">
          <div>
            <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Current Stage</p>
            <h3 className="text-xl font-extrabold text-slate-800">{data.risk_stage}</h3>
          </div>
          <div className={`mt-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-bold w-max ${riskColor}`}>
            {data.risk_stage === 'Stable' ? <ShieldCheckIcon className="h-5 w-5" /> : <ExclamationTriangleIcon className="h-5 w-5" />}
            Status Indicator
          </div>
        </div>

        <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-3xl p-6 shadow-lg text-white flex items-center gap-6">
          <div className="relative w-20 h-20 shrink-0">
            <svg className="w-full h-full transform -rotate-90">
              <circle cx="40" cy="40" r="36" fill="transparent" stroke="rgba(255,255,255,0.2)" strokeWidth="8" />
              <circle cx="40" cy="40" r="36" fill="transparent" stroke="white" strokeWidth="8"
                strokeDasharray={2 * Math.PI * 36}
                strokeDashoffset={2 * Math.PI * 36 * (1 - (data.risk_score || 0))}
                className="transition-all duration-1000 ease-out" />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center flex-col">
              <span className="text-xl font-extrabold flex items-center justify-center">
                <CountUp to={Math.round(data.risk_score * 100)} direction="up" duration={2} />%
              </span>
            </div>
          </div>
          <div>
            <p className="text-indigo-100 text-sm font-bold uppercase tracking-wider mb-1">Risk Score</p>
            <p className="text-sm font-medium text-indigo-50 leading-tight">Composite probability based on recent readings.</p>
          </div>
        </div>

        <div className="bg-white rounded-3xl p-6 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-slate-100 flex flex-col justify-center">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1 flex items-center gap-2">
            <ArrowTrendingUpIcon className="h-4 w-4" /> Trend Velocity
          </p>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Progression Velocity</p>
          <span className="text-4xl font-extrabold text-slate-800 flex items-center justify-center">{data.velocity > 0 ? '+' : ''}<CountUp to={Number(data.velocity.toFixed(3))} direction="up" duration={2} /></span>
          <div className="mt-4 text-sm font-medium">
            <span className="text-slate-500 mr-2 flex items-center justify-center">
              Accel: <span className={`${data.acceleration > 0 ? "text-rose-500 font-bold" : "text-emerald-500 font-bold"} ml-1 flex`}><CountUp to={Number(data.acceleration.toFixed(4))} direction="up" duration={2} /></span>/mo²
            </span>
          </div>
        </div>

        <div className="bg-white rounded-3xl p-6 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-slate-100 flex flex-col justify-center">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1 flex items-center gap-2">
            <HeartIcon className="h-4 w-4" /> Data Reliability
          </p>
          <div className="grid grid-cols-2 gap-4 mt-3">
            <div>
              <p className="text-2xl font-extrabold text-indigo-600 flex">
                <CountUp to={Math.round(data.agreement * 100)} direction="up" duration={2} />%
              </p>
              <p className="text-[10px] font-bold text-slate-500 uppercase mt-1">Agreement</p>
            </div>
            <div>
              <p className="text-2xl font-extrabold text-purple-600 flex">
                <CountUp to={Math.round(data.confidence * 100)} direction="up" duration={2} />%
              </p>
              <p className="text-[10px] font-bold text-slate-500 uppercase mt-1">Confidence</p>
            </div>
          </div>
        </div>
      </div>

      {timelineData.length === 0 ? (
        <div className="bg-white p-12 rounded-3xl shadow-sm border border-slate-200 text-center">
          <ChartBarSquareIcon className="h-16 w-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-slate-700">Insufficient Data Span</h3>
          <p className="text-slate-500 mt-2">The progression engine requires at least two distinct data points over time to map velocity and acceleration.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">

          {/* SECTION 2: Biomarker Timeline Chart */}
          <div className="lg:col-span-2 bg-white rounded-3xl p-6 sm:p-8 shadow-[0_2px_20px_-5px_rgba(6,81,237,0.15)] border border-purple-100">
            <h2 className="text-lg font-extrabold text-slate-800 mb-6">Biomarker Trajectories</h2>
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={timelineData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dy={10} minTickGap={30} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dx={-10} domain={['auto', 'auto']} />
                  <Tooltip
                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)' }}
                    itemStyle={{ fontWeight: 'bold' }}
                  />
                  <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px', fontSize: '13px', fontWeight: 'bold' }} />

                  <Line type="monotone" name="Handwriting" dataKey="handwriting" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} activeDot={{ r: 6 }} connectNulls />
                  <Line type="monotone" name="Voice" dataKey="voice" stroke="#10b981" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} activeDot={{ r: 6 }} connectNulls />
                  <Line type="monotone" name="DaT Scan" dataKey="dat_scan" stroke="#f43f5e" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} activeDot={{ r: 6 }} connectNulls />
                  <Line type="monotone" name="Composite Overall" dataKey="overall" stroke="#3b82f6" strokeWidth={4} strokeDasharray="5 5" dot={false} connectNulls />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* SECTION 3 & 4: Modality Visuals & AI Intel */}
          <div className="space-y-8">

            {/* Modality Shift */}
            <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-200">
              <h2 className="text-md font-extrabold text-slate-800 mb-4">Modality Distribution</h2>
              <div className="h-44 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={timelineData.slice(-5)} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8' }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8' }} />
                    <Tooltip cursor={{ fill: '#f8fafc' }} contentStyle={{ borderRadius: '12px', fontSize: '12px' }} />
                    <Bar dataKey="handwriting" stackId="a" fill="#c4b5fd" radius={[0, 0, 4, 4]} />
                    <Bar dataKey="voice" stackId="a" fill="#6ee7b7" />
                    <Bar dataKey="dat_scan" stackId="a" fill="#fda4af" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* AI Interpretation */}
            <div className="bg-gradient-to-b from-indigo-50 to-white rounded-3xl p-6 shadow-sm border border-indigo-100 relative overflow-hidden">
              <CpuChipIcon className="h-24 w-24 text-indigo-600/5 absolute -top-4 -right-4" />
              <h2 className="text-md font-extrabold text-indigo-900 mb-3 flex items-center gap-2 relative z-10">
                <SparklesIcon className="h-5 w-5 text-indigo-600" />
                AI Interpretation
              </h2>
              <div className="relative z-10 space-y-3 text-sm text-slate-700 font-medium">
                <p>
                  Based on {Math.round(data.data_span_months)} months of data, the engine detects a
                  <strong className={data.velocity > 0 ? "text-rose-600" : "text-emerald-600"}> {data.velocity > 0 ? "positive" : "negative"} velocity </strong>
                  of <span className="inline-flex"><CountUp to={Number(data.velocity.toFixed(3))} direction="up" duration={2} /></span>.
                </p>
                <p>
                  Cross-modality indicators show {formatPercent(data.agreement)} agreement,
                  resulting in a <strong className="text-indigo-700">{data.risk_stage}</strong> mapping.
                </p>
                {data.acceleration > 0.05 && (
                  <div className="mt-4 p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs font-bold leading-relaxed">
                    Acceleration detected. Motor symptom degradation is happening at a faster rate than the previous calculation window.
                  </div>
                )}
                {data.acceleration <= 0.05 && data.velocity > 0 && (
                  <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-xl text-amber-800 text-xs font-bold leading-relaxed">
                    Progression is linear. No significant acceleration shifts detected in recent timelines.
                  </div>
                )}
              </div>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}

function SparklesIcon(props: React.ComponentProps<'svg'>) {
  return (
    <svg fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09l2.846.813-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" />
    </svg>
  )
}
