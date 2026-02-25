/**
 * Longitudinal Neuro-Motor Modeling – Dashboard Page
 *
 * Full-page view showing:
 *  1. Risk Evolution Gauge  (current category + score)
 *  2. Biomarker Trend Cards (slope, direction, acceleration per marker)
 *  3. Cross-Modality Consistency Panel
 *  4. Biomarker Time-Series Chart
 *  5. Clinical Findings & Recommendations
 *  6. Assessment History Sparkline
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { longitudinalService } from '../services/longitudinal';
import type {
  RiskAssessment,
  BiomarkerTrend,
  CrossModalityData,
  TimelinePoint,
  AvailableBiomarker,
  FullAssessmentData,
  ProgressionCategory,
} from '../types/longitudinal';
import {
  PROGRESSION_LABELS,
  PROGRESSION_COLORS,
  DIRECTION_ICONS,
  MODALITY_LABELS,
} from '../types/longitudinal';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Title,
  Tooltip,
  Legend,
);

// ═══════════════════════════════════════════════════════════════════════════
// Sub-components
// ═══════════════════════════════════════════════════════════════════════════

/** Animated circular gauge for the risk score. */
function RiskGauge({
  score,
  category,
}: {
  score: number;
  category: ProgressionCategory;
}) {
  const pct = Math.round(score * 100);
  const color = PROGRESSION_COLORS[category];
  const circumference = 2 * Math.PI * 54;
  const dashOffset = circumference * (1 - score);

  return (
    <div className="flex flex-col items-center">
      <svg width="140" height="140" viewBox="0 0 120 120">
        {/* Background circle */}
        <circle
          cx="60"
          cy="60"
          r="54"
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="10"
        />
        {/* Coloured arc */}
        <circle
          cx="60"
          cy="60"
          r="54"
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          transform="rotate(-90 60 60)"
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
        <text
          x="60"
          y="55"
          textAnchor="middle"
          className="text-2xl font-bold"
          fill={color}
          fontSize="28"
        >
          {pct}%
        </text>
        <text
          x="60"
          y="75"
          textAnchor="middle"
          fill="#6b7280"
          fontSize="10"
        >
          Risk Score
        </text>
      </svg>
      <span
        className="mt-2 inline-block rounded-full px-4 py-1 text-sm font-semibold text-white"
        style={{ backgroundColor: color }}
      >
        {PROGRESSION_LABELS[category]}
      </span>
    </div>
  );
}

/** Single trend card for a biomarker. */
function TrendCard({ trend }: { trend: BiomarkerTrend }) {
  const dirIcon = DIRECTION_ICONS[trend.direction];
  const isWorsening = trend.direction === 'worsening';
  const isImproving = trend.direction === 'improving';

  const borderColor = isWorsening
    ? 'border-red-400'
    : isImproving
      ? 'border-emerald-400'
      : 'border-gray-300';

  const bgColor = isWorsening
    ? 'bg-red-50'
    : isImproving
      ? 'bg-emerald-50'
      : 'bg-gray-50';

  return (
    <div
      className={`rounded-xl border-2 ${borderColor} ${bgColor} p-4 shadow-sm transition-shadow hover:shadow-md`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-gray-500">
            {MODALITY_LABELS[trend.modality] ?? trend.modality}
          </p>
          <p className="mt-1 text-sm font-semibold text-gray-800">
            {trend.biomarker.replace(/_/g, ' ')}
          </p>
        </div>
        <span className="text-2xl" title={trend.direction}>
          {dirIcon}
        </span>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-gray-600">
        <div>
          <span className="font-medium">Slope:</span>{' '}
          {trend.slope >= 0 ? '+' : ''}
          {trend.slope.toFixed(4)}/mo
        </div>
        <div>
          <span className="font-medium">R²:</span>{' '}
          {trend.r_squared?.toFixed(2) ?? '–'}
        </div>
        {trend.acceleration !== null && (
          <div className="col-span-2">
            <span className="font-medium">Acceleration:</span>{' '}
            {trend.acceleration >= 0 ? '+' : ''}
            {trend.acceleration.toFixed(4)}/mo²
          </div>
        )}
        <div>
          <span className="font-medium">Baseline:</span>{' '}
          {trend.baseline_value?.toFixed(3) ?? '–'}
        </div>
        <div>
          <span className="font-medium">Latest:</span>{' '}
          {trend.latest_value?.toFixed(3) ?? '–'}
        </div>
      </div>

      <div className="mt-2 text-[10px] text-gray-400">
        {trend.observation_count} observations
      </div>
    </div>
  );
}

/** Cross-modality consistency panel. */
function CrossModalityPanel({ data }: { data: CrossModalityData }) {
  const agreementPct = Math.round(data.agreement_score * 100);
  const consistencyPct = Math.round(data.directional_consistency * 100);

  return (
    <div className="rounded-2xl border border-indigo-200 bg-indigo-50 p-5">
      <h3 className="mb-3 text-sm font-bold uppercase tracking-wider text-indigo-700">
        Cross-Modality Consistency
      </h3>

      <div className="mb-4 flex items-center gap-6">
        {/* Agreement bar */}
        <div className="flex-1">
          <div className="flex justify-between text-xs text-gray-600">
            <span>Agreement</span>
            <span className="font-semibold">{agreementPct}%</span>
          </div>
          <div className="mt-1 h-2 overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full rounded-full bg-indigo-500 transition-all duration-700"
              style={{ width: `${agreementPct}%` }}
            />
          </div>
        </div>

        {/* Directional consistency bar */}
        <div className="flex-1">
          <div className="flex justify-between text-xs text-gray-600">
            <span>Direction Match</span>
            <span className="font-semibold">{consistencyPct}%</span>
          </div>
          <div className="mt-1 h-2 overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full rounded-full bg-purple-500 transition-all duration-700"
              style={{ width: `${consistencyPct}%` }}
            />
          </div>
        </div>
      </div>

      {/* Per-modality direction chips */}
      <div className="flex flex-wrap gap-2">
        {Object.entries(data.modality_directions).map(([mod, dir]) => {
          const chipColor =
            dir === 'worsening'
              ? 'bg-red-100 text-red-700'
              : dir === 'improving'
                ? 'bg-emerald-100 text-emerald-700'
                : 'bg-gray-100 text-gray-600';
          return (
            <span
              key={mod}
              className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium ${chipColor}`}
            >
              {MODALITY_LABELS[mod] ?? mod}{' '}
              {DIRECTION_ICONS[dir as keyof typeof DIRECTION_ICONS] ?? '–'}
            </span>
          );
        })}
      </div>

      {/* Pairwise correlations */}
      {data.pairwise_correlations &&
        Object.keys(data.pairwise_correlations).length > 0 && (
          <div className="mt-3 text-xs text-gray-500">
            <span className="font-semibold">Pairwise: </span>
            {Object.entries(data.pairwise_correlations).map(
              ([pair, val], i) => (
                <span key={pair}>
                  {i > 0 && ' · '}
                  {pair.replace(/_/g, ' ↔ ')}: {val > 0 ? '+' : ''}
                  {val.toFixed(1)}
                </span>
              ),
            )}
          </div>
        )}
    </div>
  );
}

/** Biomarker time-series line chart. */
function TimelineChart({
  data,
  selectedBiomarker,
}: {
  data: TimelinePoint[];
  selectedBiomarker: string | null;
}) {
  const filtered = selectedBiomarker
    ? data.filter((d) => d.biomarker === selectedBiomarker)
    : data;

  // Group by biomarker
  const groups: Record<string, TimelinePoint[]> = {};
  for (const pt of filtered) {
    (groups[pt.biomarker] ??= []).push(pt);
  }

  const palette = [
    '#6366f1',
    '#f59e0b',
    '#10b981',
    '#ef4444',
    '#8b5cf6',
    '#ec4899',
    '#14b8a6',
    '#f97316',
  ];

  const datasets = Object.entries(groups).map(([name, pts], idx) => ({
    label: name.replace(/_/g, ' '),
    data: pts.map((p) => ({ x: p.recorded_at, y: p.value })),
    borderColor: palette[idx % palette.length],
    backgroundColor: palette[idx % palette.length] + '20',
    tension: 0.3,
    pointRadius: 3,
    fill: false,
  }));

  const labels = [
    ...new Set(filtered.map((d) => new Date(d.recorded_at).toLocaleDateString())),
  ];

  const chartData = {
    labels,
    datasets: datasets.map((ds) => ({
      ...ds,
      data: ds.data.map((d) => d.y),
    })),
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' as const, labels: { boxWidth: 12 } },
      title: { display: false },
    },
    scales: {
      y: { beginAtZero: false },
    },
  };

  if (datasets.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-gray-400">
        No time-series data yet. Run analyses to populate.
      </div>
    );
  }

  return (
    <div className="h-72">
      <Line data={chartData} options={options} />
    </div>
  );
}

/** Risk history sparkline. */
function AssessmentHistory({
  history,
}: {
  history: RiskAssessment[];
}) {
  if (history.length < 2) return null;

  const sorted = [...history].reverse();
  const labels = sorted.map((a) =>
    new Date(a.computed_at).toLocaleDateString(),
  );
  const scores = sorted.map((a) => a.risk_score * 100);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Risk Score %',
        data: scores,
        borderColor: '#6366f1',
        backgroundColor: '#6366f120',
        tension: 0.4,
        fill: true,
        pointRadius: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
    },
    scales: {
      y: { min: 0, max: 100, ticks: { stepSize: 25 } },
    },
  };

  return (
    <div className="h-48">
      <Line data={chartData} options={options} />
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Main Page
// ═══════════════════════════════════════════════════════════════════════════

export default function LongitudinalDashboard() {
  const [loading, setLoading] = useState(true);
  const [assessing, setAssessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [assessment, setAssessment] = useState<RiskAssessment | null>(null);
  const [trends, setTrends] = useState<BiomarkerTrend[]>([]);
  const [crossModality, setCrossModality] = useState<CrossModalityData | null>(
    null,
  );
  const [timeline, setTimeline] = useState<TimelinePoint[]>([]);
  const [history, setHistory] = useState<RiskAssessment[]>([]);
  const [availableBiomarkers, setAvailableBiomarkers] = useState<
    AvailableBiomarker[]
  >([]);
  const [selectedBiomarker, setSelectedBiomarker] = useState<string | null>(
    null,
  );

  // ── Fetch all data on mount ────────────────────────────────────────
  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [
        assessRes,
        trendsRes,
        cmRes,
        timelineRes,
        historyRes,
        bioRes,
      ] = await Promise.all([
        longitudinalService.getLatestAssessment(),
        longitudinalService.getLatestTrends(),
        longitudinalService.getLatestCrossModality(),
        longitudinalService.getTimeline(),
        longitudinalService.getAssessmentHistory(),
        longitudinalService.getAvailableBiomarkers(),
      ]);

      setAssessment((assessRes as any)?.data ?? null);
      setTrends((trendsRes as any)?.data ?? []);
      setCrossModality((cmRes as any)?.data ?? null);
      setTimeline((timelineRes as any)?.data ?? []);
      setHistory((historyRes as any)?.data ?? []);
      setAvailableBiomarkers((bioRes as any)?.data ?? []);
    } catch (err: any) {
      setError(err.message || 'Failed to load longitudinal data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  // ── Run new assessment ─────────────────────────────────────────────
  const handleRunAssessment = async () => {
    setAssessing(true);
    setError(null);
    try {
      const res = await longitudinalService.runAssessment(6);
      const data = (res as any)?.data as FullAssessmentData | undefined;
      if (data) {
        setAssessment(data.assessment);
        setTrends(data.trends);
        setCrossModality(data.cross_modality);
      }
      // Re-fetch timeline & history
      const [timelineRes, historyRes] = await Promise.all([
        longitudinalService.getTimeline(),
        longitudinalService.getAssessmentHistory(),
      ]);
      setTimeline((timelineRes as any)?.data ?? []);
      setHistory((historyRes as any)?.data ?? []);
    } catch (err: any) {
      setError(err.message || 'Assessment failed');
    } finally {
      setAssessing(false);
    }
  };

  // ── Grouped trends by modality ─────────────────────────────────────
  const trendsByModality = useMemo(() => {
    const map: Record<string, BiomarkerTrend[]> = {};
    for (const t of trends) {
      (map[t.modality] ??= []).push(t);
    }
    return map;
  }, [trends]);

  // ── Render ─────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 animate-spin rounded-full border-4 border-indigo-200 border-t-indigo-600" />
          <p className="mt-4 text-gray-500">
            Loading longitudinal analysis…
          </p>
        </div>
      </div>
    );
  }

  const hasData = assessment || trends.length > 0 || timeline.length > 0;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* ── Header ─────────────────────────────────────────────────── */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Longitudinal Neuro-Motor Analysis
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Modeling disease <em>evolution</em>, not just presence — tracking
            rate of change, cross-modality consistency, and trend acceleration.
          </p>
        </div>

        <button
          onClick={handleRunAssessment}
          disabled={assessing}
          className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow transition hover:bg-indigo-700 disabled:opacity-50"
        >
          {assessing ? (
            <>
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Analyzing…
            </>
          ) : (
            'Run Assessment'
          )}
        </button>
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* ── Empty state ────────────────────────────────────────────── */}
      {!hasData && (
        <div className="rounded-2xl border-2 border-dashed border-gray-300 py-20 text-center">
          <svg
            className="mx-auto h-16 w-16 text-gray-300"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 48 48"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M12 36V18m8 18V12m8 24V24m8 12V6"
            />
          </svg>
          <h3 className="mt-4 text-lg font-semibold text-gray-700">
            No longitudinal data yet
          </h3>
          <p className="mt-2 text-sm text-gray-500">
            Complete analyses (handwriting, voice, DaT scan) over time to
            populate your progression profile. Then click{' '}
            <strong>Run Assessment</strong> to compute trends.
          </p>
        </div>
      )}

      {hasData && (
        <>
          {/* ── Row 1: Risk Gauge + Key Metrics + Delta ────────────── */}
          {assessment && (
            <div className="mb-8 grid gap-6 lg:grid-cols-3">
              {/* Gauge */}
              <div className="flex items-center justify-center rounded-2xl border bg-white p-6 shadow-sm">
                <RiskGauge
                  score={assessment.risk_score}
                  category={assessment.progression_category}
                />
              </div>

              {/* Key numbers */}
              <div className="grid grid-cols-2 gap-4 rounded-2xl border bg-white p-6 shadow-sm">
                <MetricBox
                  label="Avg Velocity"
                  value={
                    assessment.avg_slope !== null
                      ? `${assessment.avg_slope >= 0 ? '+' : ''}${assessment.avg_slope.toFixed(4)}/mo`
                      : '–'
                  }
                  sub="Biomarker slope"
                />
                <MetricBox
                  label="Acceleration"
                  value={
                    assessment.avg_acceleration !== null
                      ? `${assessment.avg_acceleration >= 0 ? '+' : ''}${assessment.avg_acceleration.toFixed(4)}/mo²`
                      : '–'
                  }
                  sub="Δ slope"
                />
                <MetricBox
                  label="Agreement"
                  value={
                    assessment.cross_modality_agreement !== null
                      ? `${Math.round(assessment.cross_modality_agreement * 100)}%`
                      : '–'
                  }
                  sub="Cross-modality"
                />
                <MetricBox
                  label="Data Span"
                  value={
                    assessment.months_of_data !== null
                      ? `${assessment.months_of_data.toFixed(1)} mo`
                      : '–'
                  }
                  sub="Longitudinal"
                />
              </div>

              {/* Confidence + delta */}
              <div className="flex flex-col justify-center gap-4 rounded-2xl border bg-white p-6 shadow-sm">
                <div className="text-center">
                  <p className="text-xs font-medium uppercase tracking-wider text-gray-500">
                    Confidence
                  </p>
                  <p className="mt-1 text-3xl font-bold text-gray-800">
                    {Math.round(assessment.confidence * 100)}%
                  </p>
                </div>
                {assessment.risk_delta !== null && (
                  <div className="text-center">
                    <p className="text-xs font-medium uppercase tracking-wider text-gray-500">
                      Risk Δ since last
                    </p>
                    <p
                      className={`mt-1 text-2xl font-bold ${
                        assessment.risk_delta > 0
                          ? 'text-red-600'
                          : assessment.risk_delta < 0
                            ? 'text-emerald-600'
                            : 'text-gray-600'
                      }`}
                    >
                      {assessment.risk_delta > 0 ? '+' : ''}
                      {(assessment.risk_delta * 100).toFixed(1)}%
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ── Row 2: Biomarker Trend Cards ───────────────────────── */}
          {trends.length > 0 && (
            <section className="mb-8">
              <h2 className="mb-4 text-lg font-bold text-gray-800">
                Biomarker Trends
                <span className="ml-2 text-sm font-normal text-gray-500">
                  (Rate of Change per Modality)
                </span>
              </h2>
              {Object.entries(trendsByModality).map(([mod, modTrends]) => (
                <div key={mod} className="mb-4">
                  <h3 className="mb-2 text-sm font-semibold uppercase tracking-wider text-gray-600">
                    {MODALITY_LABELS[mod] ?? mod}
                  </h3>
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                    {modTrends.map((t) => (
                      <TrendCard
                        key={`${t.modality}-${t.biomarker}`}
                        trend={t}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </section>
          )}

          {/* ── Row 3: Cross-Modality Consistency ──────────────────── */}
          {crossModality && (
            <section className="mb-8">
              <CrossModalityPanel data={crossModality} />
            </section>
          )}

          {/* ── Row 4: Time-Series Chart ───────────────────────────── */}
          <section className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-lg font-bold text-gray-800">
                Biomarker Timeline
              </h2>
              <select
                aria-label="Filter biomarker"
                value={selectedBiomarker ?? ''}
                onChange={(e) =>
                  setSelectedBiomarker(e.target.value || null)
                }
                className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-400"
              >
                <option value="">All biomarkers</option>
                {availableBiomarkers.map((b) => (
                  <option key={b.name} value={b.name}>
                    {b.name.replace(/_/g, ' ')} ({b.modality})
                  </option>
                ))}
              </select>
            </div>
            <TimelineChart
              data={timeline}
              selectedBiomarker={selectedBiomarker}
            />
          </section>

          {/* ── Row 5: Clinical Findings & Recommendations ─────────── */}
          {assessment && (
            <div className="mb-8 grid gap-6 lg:grid-cols-2">
              {/* Findings */}
              {assessment.key_findings &&
                assessment.key_findings.length > 0 && (
                  <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6">
                    <h3 className="mb-3 text-sm font-bold uppercase tracking-wider text-amber-700">
                      Key Findings
                    </h3>
                    <ul className="space-y-2">
                      {assessment.key_findings.map((f, i) => (
                        <li
                          key={i}
                          className="flex items-start gap-2 text-sm text-gray-700"
                        >
                          <span className="mt-0.5 text-amber-500">●</span>
                          {f}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

              {/* Recommendations */}
              {assessment.recommendations &&
                assessment.recommendations.length > 0 && (
                  <div className="rounded-2xl border border-blue-200 bg-blue-50 p-6">
                    <h3 className="mb-3 text-sm font-bold uppercase tracking-wider text-blue-700">
                      Recommendations
                    </h3>
                    <ul className="space-y-2">
                      {assessment.recommendations.map((r, i) => (
                        <li
                          key={i}
                          className="flex items-start gap-2 text-sm text-gray-700"
                        >
                          <span className="mt-0.5 text-blue-500">▸</span>
                          {r}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
            </div>
          )}

          {/* ── Row 6: Clinical summary ────────────────────────────── */}
          {assessment?.clinical_summary && (
            <div className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
              <h3 className="mb-2 text-sm font-bold uppercase tracking-wider text-gray-600">
                Clinical Summary
              </h3>
              <p className="text-sm leading-relaxed text-gray-700">
                {assessment.clinical_summary}
              </p>
            </div>
          )}

          {/* ── Row 7: Assessment History ───────────────────────────── */}
          {history.length > 1 && (
            <section className="rounded-2xl border bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-bold text-gray-800">
                Risk Score History
              </h2>
              <AssessmentHistory history={history} />
            </section>
          )}
        </>
      )}
    </div>
  );
}

// ─── Tiny helper ─────────────────────────────────────────────────────────

function MetricBox({
  label,
  value,
  sub,
}: {
  label: string;
  value: string;
  sub: string;
}) {
  return (
    <div className="text-center">
      <p className="text-[10px] font-medium uppercase tracking-wider text-gray-400">
        {label}
      </p>
      <p className="mt-0.5 text-lg font-bold text-gray-800">{value}</p>
      <p className="text-[10px] text-gray-400">{sub}</p>
    </div>
  );
}
