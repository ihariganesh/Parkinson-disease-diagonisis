import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { medicalService } from '../services/medical';
import type { DiagnosisReport, MedicalData } from '../types';
import {
  DocumentTextIcon,
  ChartBarIcon,
  ArrowDownTrayIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ArrowTrendingUpIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline';
import ReportCard from '../components/reports/ReportCard.tsx';
import AnalysisTimeline from '../components/reports/AnalysisTimeline.tsx';
import UploadedFilesList from '../components/reports/UploadedFilesList.tsx';
import ProgressCharts from '../components/reports/ProgressCharts.tsx';
import ReportDetailsModal from '../components/reports/ReportDetailsModal.tsx';
import LifestyleRecommendationsView from '../components/reports/LifestyleRecommendationsView.tsx';
import ReportFilters from '../components/reports/ReportFilters.tsx';

type TabType = 'all' | 'diagnosis' | 'handwriting' | 'voice' | 'dat_scan';

const ReportsPage = () => {
  const { state } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('all');
  const [reports, setReports] = useState<DiagnosisReport[]>([]);
  const [uploads, setUploads] = useState<MedicalData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedReport, setSelectedReport] = useState<DiagnosisReport | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [dateRange, setDateRange] = useState<{ start: Date | null; end: Date | null }>({
    start: null,
    end: null,
  });
  const [selectedReportIds, setSelectedReportIds] = useState<Set<string>>(new Set());
  const [isSelectionMode, setIsSelectionMode] = useState(false);

  useEffect(() => {
    loadReportsData();
  }, []);

  const loadReportsData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [reportsResponse, uploadsResponse] = await Promise.all([
        medicalService.getDiagnosisReports(state.user?.id, 1, 50),
        medicalService.getMedicalData(state.user?.id, undefined, 1, 50),
      ]);

      if (reportsResponse.success && reportsResponse.data) {
        setReports(reportsResponse.data.items || []);
      }

      if (uploadsResponse.success && uploadsResponse.data) {
        setUploads(uploadsResponse.data.items || []);
      }
    } catch (err: any) {
      console.error('Error loading reports:', err);
      setError(err.message || 'Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  const handleViewReport = (report: DiagnosisReport) => {
    setSelectedReport(report);
    setShowDetailsModal(true);
  };

  const handleCloseModal = () => {
    setShowDetailsModal(false);
    setSelectedReport(null);
  };

  const handleExportReport = async (reportId: string) => {
    try {
      // TODO: Implement PDF export
      console.log('Exporting report:', reportId);
      alert('PDF export feature coming soon!');
    } catch (err) {
      console.error('Export error:', err);
    }
  };

  const handleShareReport = async (reportId: string) => {
    try {
      // TODO: Implement share functionality
      console.log('Sharing report:', reportId);
      alert('Share feature coming soon!');
    } catch (err) {
      console.error('Share error:', err);
    }
  };

  const handleDeleteReport = async (reportId: string) => {
    try {
      // Confirm deletion
      if (!window.confirm('Are you sure you want to delete this diagnosis report? This action cannot be undone.')) {
        return;
      }

      const response = await medicalService.deleteDiagnosisReport(reportId);
      
      if (response.success) {
        // Remove report from state
        setReports(reports.filter(r => r.id !== reportId));
        alert('Report deleted successfully!');
      } else {
        alert(response.error || 'Failed to delete report');
      }
    } catch (err: any) {
      console.error('Delete error:', err);
      alert(err.message || 'Failed to delete report');
    }
  };

  const handleToggleSelection = (reportId: string) => {
    const newSelected = new Set(selectedReportIds);
    if (newSelected.has(reportId)) {
      newSelected.delete(reportId);
    } else {
      newSelected.add(reportId);
    }
    setSelectedReportIds(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedReportIds.size === filteredReports.length) {
      setSelectedReportIds(new Set());
    } else {
      setSelectedReportIds(new Set(filteredReports.map(r => r.id)));
    }
  };

  const handleBulkDelete = async () => {
    console.log('[DEBUG] handleBulkDelete called, selected:', selectedReportIds.size);
    
    if (selectedReportIds.size === 0) {
      alert('Please select at least one report to delete');
      return;
    }

    const count = selectedReportIds.size;
    console.log('[DEBUG] Confirming deletion of', count, 'reports');
    
    if (!window.confirm(`Are you sure you want to delete ${count} report(s)? This action cannot be undone.`)) {
      console.log('[DEBUG] User cancelled deletion');
      return;
    }

    try {
      const reportIdsArray = Array.from(selectedReportIds);
      console.log('[DEBUG] Sending delete request for report IDs:', reportIdsArray);
      
      const response = await medicalService.bulkDeleteDiagnosisReports(reportIdsArray);
      console.log('[DEBUG] Delete response:', response);
      
      if (response.success) {
        // Remove deleted reports from state
        setReports(reports.filter(r => !selectedReportIds.has(r.id)));
        setSelectedReportIds(new Set());
        setIsSelectionMode(false);
        const deletedCount = (response as any).deleted_count || count;
        alert(`Successfully deleted ${deletedCount} report(s)!`);
        
        // Reload reports to ensure UI is in sync with backend
        await loadReportsData();
      } else {
        console.error('[ERROR] Delete failed:', response.error);
        alert(response.error || 'Failed to delete reports');
      }
    } catch (err: any) {
      console.error('[ERROR] Bulk delete error:', err);
      alert(err.message || 'Failed to delete reports');
    }
  };

  const handleCancelSelection = () => {
    setSelectedReportIds(new Set());
    setIsSelectionMode(false);
  };

  const tabs = [
    { id: 'all' as TabType, name: 'All Reports', icon: DocumentTextIcon },
    { id: 'diagnosis' as TabType, name: 'Diagnosis', icon: CheckCircleIcon },
    { id: 'handwriting' as TabType, name: 'Handwriting', icon: DocumentTextIcon },
    { id: 'voice' as TabType, name: 'Voice', icon: ChartBarIcon },
    { id: 'dat_scan' as TabType, name: 'DaT Scan', icon: ChartBarIcon },
  ];

  // Filter reports based on active tab
  const filteredReports = reports.filter(() => {
    if (activeTab === 'all') return true;
    // Add filtering logic based on report type when available
    return true;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your reports...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <DocumentTextIcon className="h-8 w-8 text-blue-600" />
                Medical Reports & Analysis History
              </h1>
              <p className="mt-2 text-gray-600">
                View your diagnosis reports, analysis history, and medical records
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => loadReportsData()}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
              >
                <ClockIcon className="h-5 w-5" />
                Refresh
              </button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Reports</p>
                  <p className="text-2xl font-bold text-gray-900">{reports.length}</p>
                </div>
                <DocumentTextIcon className="h-8 w-8 text-blue-600" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Verified Reports</p>
                  <p className="text-2xl font-bold text-green-600">
                    {reports.filter(r => r.doctorVerified).length}
                  </p>
                </div>
                <CheckCircleIcon className="h-8 w-8 text-green-600" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Uploads</p>
                  <p className="text-2xl font-bold text-purple-600">{uploads.length}</p>
                </div>
                <ArrowDownTrayIcon className="h-8 w-8 text-purple-600" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Latest Analysis</p>
                  <p className="text-sm font-medium text-gray-900">
                    {reports.length > 0
                      ? new Date(reports[0].createdAt).toLocaleDateString()
                      : 'No data'}
                  </p>
                </div>
                <CalendarIcon className="h-8 w-8 text-indigo-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                    ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <tab.icon className="h-5 w-5" />
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Filters */}
        <ReportFilters
          dateRange={dateRange}
          onDateRangeChange={setDateRange}
          onApplyFilters={() => loadReportsData()}
        />

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <ExclamationCircleIcon className="h-6 w-6 text-red-600 flex-shrink-0" />
            <div>
              <h3 className="font-medium text-red-900">Error Loading Reports</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="space-y-8">
          {/* 1. Diagnosis Reports Section */}
          <section>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <DocumentTextIcon className="h-6 w-6 text-blue-600" />
                Recent Diagnosis Reports
              </h2>
              
              {/* Bulk Actions Toolbar */}
              <div className="flex items-center gap-3">
                {!isSelectionMode ? (
                  <button
                    onClick={() => setIsSelectionMode(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                  >
                    Select Multiple
                  </button>
                ) : (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">
                      {selectedReportIds.size} selected
                    </span>
                    <button
                      onClick={handleSelectAll}
                      className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                    >
                      {selectedReportIds.size === filteredReports.length ? 'Deselect All' : 'Select All'}
                    </button>
                    <button
                      onClick={handleBulkDelete}
                      disabled={selectedReportIds.size === 0}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Delete Selected ({selectedReportIds.size})
                    </button>
                    <button
                      onClick={handleCancelSelection}
                      className="px-3 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors text-sm"
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            </div>
            
            {filteredReports.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-8 text-center">
                <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600">No diagnosis reports available yet.</p>
                <p className="text-sm text-gray-500 mt-2">
                  Complete a comprehensive analysis to generate your first report.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {filteredReports.map(report => (
                  <div key={report.id} className="relative">
                    {isSelectionMode && (
                      <div className="absolute top-4 left-4 z-10">
                        <label className="flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={selectedReportIds.has(report.id)}
                            onChange={() => handleToggleSelection(report.id)}
                            className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                            aria-label={`Select report from ${new Date(report.createdAt).toLocaleDateString()}`}
                          />
                        </label>
                      </div>
                    )}
                    <ReportCard
                      report={report}
                      onView={handleViewReport}
                      onExport={handleExportReport}
                      onShare={handleShareReport}
                      onDelete={handleDeleteReport}
                    />
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* 2. Progress Tracking Charts */}
          {reports.length > 0 && (
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <ArrowTrendingUpIcon className="h-6 w-6 text-green-600" />
                Progress Tracking
              </h2>
              <ProgressCharts reports={reports} />
            </section>
          )}

          {/* 3. Analysis Timeline */}
          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ClockIcon className="h-6 w-6 text-purple-600" />
              Analysis History Timeline
            </h2>
            <AnalysisTimeline reports={reports} uploads={uploads} />
          </section>

          {/* 4. Uploaded Files */}
          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ArrowDownTrayIcon className="h-6 w-6 text-indigo-600" />
              Uploaded Medical Files
            </h2>
            <UploadedFilesList uploads={uploads} onRefresh={loadReportsData} />
          </section>

          {/* 5. Lifestyle Recommendations */}
          {reports.length > 0 && reports[0] && (
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                AI-Powered Lifestyle Recommendations
              </h2>
              <LifestyleRecommendationsView reportId={reports[0].id} />
            </section>
          )}
        </div>
      </div>

      {/* Report Details Modal */}
      {showDetailsModal && selectedReport && (
        <ReportDetailsModal
          report={selectedReport}
          onClose={handleCloseModal}
          onExport={handleExportReport}
          onShare={handleShareReport}
        />
      )}
    </div>
  );
};

export default ReportsPage;
