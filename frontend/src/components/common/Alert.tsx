import type { ReactNode } from "react";
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";

interface AlertProps {
  type: "success" | "error" | "warning" | "info";
  title?: string;
  message: string;
  onClose?: () => void;
  className?: string;
  children?: ReactNode;
}

const alertStyles = {
  success: {
    container: "bg-green-50 border-green-200 text-green-800",
    icon: CheckCircleIcon,
    iconColor: "text-green-400",
  },
  error: {
    container: "bg-red-50 border-red-200 text-red-800",
    icon: XCircleIcon,
    iconColor: "text-red-400",
  },
  warning: {
    container: "bg-yellow-50 border-yellow-200 text-yellow-800",
    icon: ExclamationTriangleIcon,
    iconColor: "text-yellow-400",
  },
  info: {
    container: "bg-blue-50 border-blue-200 text-blue-800",
    icon: InformationCircleIcon,
    iconColor: "text-blue-400",
  },
};

export function Alert({
  type,
  title,
  message,
  onClose,
  className = "",
  children,
}: AlertProps) {
  const style = alertStyles[type];
  const IconComponent = style.icon;

  return (
    <div className={`border rounded-lg p-4 ${style.container} ${className}`}>
      <div className="flex">
        <div className="flex-shrink-0">
          <IconComponent className={`h-5 w-5 ${style.iconColor}`} />
        </div>
        <div className="ml-3 flex-1">
          {title && <h3 className="text-sm font-medium">{title}</h3>}
          <div className={`text-sm ${title ? "mt-1" : ""}`}>
            <p>{message}</p>
            {children}
          </div>
        </div>
        {onClose && (
          <div className="ml-auto pl-3">
            <button
              onClick={onClose}
              className="inline-flex rounded-md p-1.5 hover:bg-opacity-20 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-green-50 focus:ring-green-600"
              title="Close alert"
            >
              <XMarkIcon className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  type?: "danger" | "warning" | "info";
}

export function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  onConfirm,
  onCancel,
  type = "danger",
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  const confirmButtonClass =
    type === "danger"
      ? "btn-danger"
      : type === "warning"
      ? "bg-yellow-600 hover:bg-yellow-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200 ease-in-out"
      : "btn-primary";

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3 text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
          <div className="mt-2 px-7 py-3">
            <p className="text-sm text-gray-500">{message}</p>
          </div>
          <div className="flex gap-3 mt-4">
            <button onClick={onCancel} className="btn-secondary flex-1">
              {cancelLabel}
            </button>
            <button
              onClick={onConfirm}
              className={`${confirmButtonClass} flex-1`}
            >
              {confirmLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Default export for easier importing
export default Alert;
