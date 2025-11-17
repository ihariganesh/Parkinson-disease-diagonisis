import type { DiagnosisReport } from '../../types';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface ProgressChartsProps {
  reports: DiagnosisReport[];
}

const ProgressCharts = ({ reports }: ProgressChartsProps) => {
  // Sort reports by date
  const sortedReports = [...reports].sort(
    (a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
  );

  // Prepare data for confidence chart
  const confidenceData = {
    labels: sortedReports.map((r) =>
      new Date(r.createdAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    ),
    datasets: [
      {
        label: 'Confidence Score (%)',
        data: sortedReports.map((r) => (r.confidence * 100).toFixed(1)),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  // Prepare data for stage progression
  const stageData = {
    labels: sortedReports.map((r) =>
      new Date(r.createdAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    ),
    datasets: [
      {
        label: 'Stage',
        data: sortedReports.map((r) => r.stage),
        borderColor: 'rgb(168, 85, 247)',
        backgroundColor: 'rgba(168, 85, 247, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  // Prepare data for fusion score
  const fusionData = {
    labels: sortedReports.map((r) =>
      new Date(r.createdAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    ),
    datasets: [
      {
        label: 'Fusion Score (%)',
        data: sortedReports.map((r) => (r.fusionScore * 100).toFixed(1)),
        borderColor: 'rgb(236, 72, 153)',
        backgroundColor: 'rgba(236, 72, 153, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
      },
    },
  };

  const stageChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 4,
        ticks: {
          stepSize: 1,
        },
      },
    },
  };

  if (sortedReports.length < 2) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <p className="text-gray-600">Need at least 2 reports to show progress trends.</p>
        <p className="text-sm text-gray-500 mt-2">
          Complete more analyses to track your progress over time.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Confidence Score Trend */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Confidence Score Trend
          </h3>
          <div className="h-64">
            <Line data={confidenceData} options={chartOptions} />
          </div>
          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <div className="bg-blue-50 rounded p-3">
              <p className="text-xs text-gray-600">Latest</p>
              <p className="text-lg font-bold text-blue-700">
                {(sortedReports[sortedReports.length - 1].confidence * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-green-50 rounded p-3">
              <p className="text-xs text-gray-600">Average</p>
              <p className="text-lg font-bold text-green-700">
                {(
                  sortedReports.reduce((acc, r) => acc + r.confidence, 0) /
                  sortedReports.length *
                  100
                ).toFixed(1)}
                %
              </p>
            </div>
            <div className="bg-purple-50 rounded p-3">
              <p className="text-xs text-gray-600">Trend</p>
              <p className="text-lg font-bold text-purple-700">
                {sortedReports[sortedReports.length - 1].confidence >
                sortedReports[0].confidence
                  ? '📈 Up'
                  : '📉 Down'}
              </p>
            </div>
          </div>
        </div>

        {/* Stage Progression */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Stage Progression</h3>
          <div className="h-64">
            <Line data={stageData} options={stageChartOptions} />
          </div>
          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <div className="bg-purple-50 rounded p-3">
              <p className="text-xs text-gray-600">Current</p>
              <p className="text-lg font-bold text-purple-700">
                Stage {sortedReports[sortedReports.length - 1].stage}
              </p>
            </div>
            <div className="bg-orange-50 rounded p-3">
              <p className="text-xs text-gray-600">Initial</p>
              <p className="text-lg font-bold text-orange-700">
                Stage {sortedReports[0].stage}
              </p>
            </div>
            <div className="bg-pink-50 rounded p-3">
              <p className="text-xs text-gray-600">Change</p>
              <p className="text-lg font-bold text-pink-700">
                {sortedReports[sortedReports.length - 1].stage === sortedReports[0].stage
                  ? '→ Stable'
                  : sortedReports[sortedReports.length - 1].stage > sortedReports[0].stage
                  ? '⚠️ Higher'
                  : '✓ Lower'}
              </p>
            </div>
          </div>
        </div>

        {/* Fusion Score Trend */}
        <div className="lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Multimodal Fusion Score Trend
          </h3>
          <div className="h-64">
            <Line data={fusionData} options={chartOptions} />
          </div>
          <div className="mt-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4">
            <div className="grid grid-cols-4 gap-4 text-center">
              <div>
                <p className="text-xs text-gray-600">Latest Score</p>
                <p className="text-xl font-bold text-blue-700">
                  {(sortedReports[sortedReports.length - 1].fusionScore * 100).toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Average Score</p>
                <p className="text-xl font-bold text-green-700">
                  {(
                    sortedReports.reduce((acc, r) => acc + r.fusionScore, 0) /
                    sortedReports.length *
                    100
                  ).toFixed(1)}
                  %
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Total Reports</p>
                <p className="text-xl font-bold text-purple-700">{sortedReports.length}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Time Span</p>
                <p className="text-xl font-bold text-pink-700">
                  {Math.ceil(
                    (new Date(sortedReports[sortedReports.length - 1].createdAt).getTime() -
                      new Date(sortedReports[0].createdAt).getTime()) /
                      (1000 * 60 * 60 * 24)
                  )}{' '}
                  days
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressCharts;
