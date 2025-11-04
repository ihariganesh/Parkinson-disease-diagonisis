import type { ReactNode } from "react";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  color?: "blue" | "gray" | "white";
  className?: string;
}

export function LoadingSpinner({
  size = "md",
  color = "blue",
  className = "",
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-8 w-8",
  };

  const colorClasses = {
    blue: "text-blue-600",
    gray: "text-gray-400",
    white: "text-white",
  };

  return (
    <div
      className={`animate-spin ${sizeClasses[size]} ${colorClasses[color]} ${className}`}
    >
      <svg
        className="w-full h-full"
        fill="none"
        viewBox="0 0 24 24"
        aria-label="Loading"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>
  );
}

interface LoadingOverlayProps {
  isLoading: boolean;
  message?: string;
  children: ReactNode;
}

export function LoadingOverlay({
  isLoading,
  message = "Loading...",
  children,
}: LoadingOverlayProps) {
  return (
    <div className="relative">
      {children}
      {isLoading && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-50">
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="mt-2 text-gray-600">{message}</p>
          </div>
        </div>
      )}
    </div>
  );
}

interface ProgressBarProps {
  progress: number;
  className?: string;
  showPercentage?: boolean;
}

export function ProgressBar({
  progress,
  className = "",
  showPercentage = true,
}: ProgressBarProps) {
  const clampedProgress = Math.max(0, Math.min(100, progress));
  const roundedProgress = Math.round(progress);

  return (
    <div className={`w-full ${className}`}>
      <div className="flex justify-between mb-1">
        {showPercentage && (
          <span className="text-sm font-medium text-gray-700">
            {roundedProgress}%
          </span>
        )}
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${clampedProgress}%` }}
          role="progressbar"
          aria-label="Progress"
          {...{
            "aria-valuenow": roundedProgress,
            "aria-valuemin": 0,
            "aria-valuemax": 100,
          }}
        />
      </div>
    </div>
  );
}

// Default export for easier importing
export default LoadingSpinner;
