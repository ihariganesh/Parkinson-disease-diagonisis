import type { DiagnosisReport, MedicalData } from '../../types';
import {
  ClockIcon,
  DocumentTextIcon,
  BeakerIcon,
  MicrophoneIcon,
  PencilIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

interface AnalysisTimelineProps {
  reports: DiagnosisReport[];
  uploads: MedicalData[];
}

interface TimelineEvent {
  id: string;
  type: 'report' | 'upload';
  date: Date;
  title: string;
  description: string;
  icon: any;
  color: string;
  data: any;
}

const AnalysisTimeline = ({ reports, uploads }: AnalysisTimelineProps) => {
  // Combine reports and uploads into timeline events
  const events: TimelineEvent[] = [
    ...reports.map(report => ({
      id: report.id,
      type: 'report' as const,
      date: new Date(report.createdAt),
      title: 'Comprehensive Diagnosis Report',
      description: `Stage ${report.stage} - ${(report.confidence * 100).toFixed(1)}% confidence`,
      icon: DocumentTextIcon,
      color: 'blue',
      data: report,
    })),
    ...uploads.map(upload => ({
      id: upload.id,
      type: 'upload' as const,
      date: new Date(upload.uploadedAt),
      title: getUploadTitle(upload.type),
      description: upload.fileName,
      icon: getUploadIcon(upload.type),
      color: getUploadColor(upload.type),
      data: upload,
    })),
  ].sort((a, b) => b.date.getTime() - a.date.getTime()); // Sort by most recent first

  function getUploadTitle(type: string): string {
    const titles: Record<string, string> = {
      handwriting: 'Handwriting Analysis',
      voice: 'Voice Analysis',
      dat_scan: 'DaT Scan Analysis',
      doctor_notes: 'Medical Report Upload',
    };
    return titles[type] || 'Medical Data Upload';
  }

  function getUploadIcon(type: string) {
    const icons: Record<string, any> = {
      handwriting: PencilIcon,
      voice: MicrophoneIcon,
      dat_scan: BeakerIcon,
      doctor_notes: DocumentTextIcon,
    };
    return icons[type] || DocumentTextIcon;
  }

  function getUploadColor(type: string): string {
    const colors: Record<string, string> = {
      handwriting: 'purple',
      voice: 'pink',
      dat_scan: 'indigo',
      doctor_notes: 'gray',
    };
    return colors[type] || 'gray';
  }

  const colorClasses: Record<string, { bg: string; text: string; border: string }> = {
    blue: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
    purple: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
    pink: { bg: 'bg-pink-50', text: 'text-pink-700', border: 'border-pink-200' },
    indigo: { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200' },
    gray: { bg: 'bg-gray-50', text: 'text-gray-700', border: 'border-gray-200' },
  };

  if (events.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <ClockIcon className="h-12 w-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-600">No analysis history available yet.</p>
        <p className="text-sm text-gray-500 mt-2">
          Your analyses and uploads will appear here.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <div className="space-y-4">
          {events.map((event, index) => {
            const colors = colorClasses[event.color];
            const Icon = event.icon;

            return (
              <div key={event.id} className="flex gap-4">
                {/* Timeline line */}
                <div className="flex flex-col items-center">
                  <div className={`p-2 rounded-full ${colors.bg} ${colors.border} border-2`}>
                    <Icon className={`h-5 w-5 ${colors.text}`} />
                  </div>
                  {index < events.length - 1 && (
                    <div className="w-0.5 h-full bg-gray-200 mt-2" />
                  )}
                </div>

                {/* Event content */}
                <div className="flex-1 pb-8">
                  <div className={`p-4 rounded-lg border ${colors.bg} ${colors.border}`}>
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-gray-900">{event.title}</h3>
                      <span className="text-xs text-gray-500">
                        {event.date.toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{event.description}</p>

                    {/* Additional info for reports */}
                    {event.type === 'report' && event.data.doctorVerified && (
                      <div className="mt-2 flex items-center gap-1 text-xs text-green-600">
                        <CheckCircleIcon className="h-4 w-4" />
                        <span>Doctor Verified</span>
                      </div>
                    )}

                    {/* Additional info for uploads */}
                    {event.type === 'upload' && (
                      <div className="mt-2 text-xs text-gray-500">
                        {event.data.processedAt ? (
                          <span className="text-green-600">✓ Processed</span>
                        ) : (
                          <span className="text-yellow-600">⏳ Processing</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default AnalysisTimeline;
