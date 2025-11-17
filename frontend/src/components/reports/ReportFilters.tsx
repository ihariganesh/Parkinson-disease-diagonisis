import { FunnelIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { useState } from 'react';

interface ReportFiltersProps {
  dateRange: { start: Date | null; end: Date | null };
  onDateRangeChange: (range: { start: Date | null; end: Date | null }) => void;
  onApplyFilters: () => void;
}

const ReportFilters = ({ dateRange, onDateRangeChange, onApplyFilters }: ReportFiltersProps) => {
  const [showFilters, setShowFilters] = useState(false);

  const handleClearFilters = () => {
    onDateRangeChange({ start: null, end: null });
    onApplyFilters();
  };

  const hasActiveFilters = dateRange.start !== null || dateRange.end !== null;

  return (
    <div className="mb-6">
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 text-gray-700 hover:text-gray-900"
          >
            <FunnelIcon className="h-5 w-5" />
            <span className="font-medium">Filters</span>
            {hasActiveFilters && (
              <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                Active
              </span>
            )}
          </button>
          {hasActiveFilters && (
            <button
              onClick={handleClearFilters}
              className="text-sm text-red-600 hover:text-red-700 flex items-center gap-1"
            >
              <XMarkIcon className="h-4 w-4" />
              Clear Filters
            </button>
          )}
        </div>

        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={dateRange.start?.toISOString().split('T')[0] || ''}
                  onChange={(e) =>
                    onDateRangeChange({
                      ...dateRange,
                      start: e.target.value ? new Date(e.target.value) : null,
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={dateRange.end?.toISOString().split('T')[0] || ''}
                  onChange={(e) =>
                    onDateRangeChange({
                      ...dateRange,
                      end: e.target.value ? new Date(e.target.value) : null,
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            <div className="mt-4 flex justify-end">
              <button
                onClick={onApplyFilters}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Apply Filters
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportFilters;
