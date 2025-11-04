import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import {
  CloudArrowUpIcon,
  DocumentTextIcon,
  XMarkIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/outline";
import { medicalService } from "../../services";
import { LoadingSpinner, Alert, ProgressBar } from "../common";
import type { UploadProgress } from "../../types";

const dataTypes = [
  { value: "handwriting", label: "Handwriting Sample", accept: "image/*" },
  { value: "voice", label: "Voice Recording", accept: "audio/*" },
  { value: "ecg", label: "ECG Data", accept: ".csv,.txt,.json" },
  // { value: "mri", label: "MRI Scan", accept: "image/*" }, // removed during cleanup
  {
    value: "doctor_notes",
    label: "Doctor Notes",
    accept: ".pdf,.doc,.docx,.txt",
  },
];

export default function DataUpload() {
  const [selectedType, setSelectedType] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [...prev, ...acceptedFiles]);
    setError("");
  }, []);

  const selectedTypeConfig = dataTypes.find(
    (type) => type.value === selectedType
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: selectedTypeConfig?.accept
      ? { [selectedTypeConfig.accept]: [] }
      : undefined,
    disabled: !selectedType || isUploading,
    maxSize: 100 * 1024 * 1024, // 100MB
  });

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (!selectedType || files.length === 0) {
      setError("Please select a data type and add files");
      return;
    }

    setIsUploading(true);
    setError("");
    setSuccess("");

    const progress: UploadProgress[] = files.map((file) => ({
      fileName: file.name,
      progress: 0,
      status: "uploading",
    }));
    setUploadProgress(progress);

    try {
      const uploadPromises = files.map(async (file, index) => {
        try {
          const metadata = {
            originalName: file.name,
            size: file.size,
            type: file.type,
          };

          await medicalService.uploadMedicalData(
            file,
            selectedType,
            metadata,
            (progressPercent) => {
              setUploadProgress((prev) =>
                prev.map((item, i) =>
                  i === index ? { ...item, progress: progressPercent } : item
                )
              );
            }
          );

          setUploadProgress((prev) =>
            prev.map((item, i) =>
              i === index
                ? { ...item, status: "completed", progress: 100 }
                : item
            )
          );
        } catch (err) {
          setUploadProgress((prev) =>
            prev.map((item, i) =>
              i === index
                ? {
                    ...item,
                    status: "error",
                    error: err instanceof Error ? err.message : "Upload failed",
                  }
                : item
            )
          );
          throw err;
        }
      });

      await Promise.all(uploadPromises);
      setSuccess(`Successfully uploaded ${files.length} file(s)`);
      setFiles([]);
      setSelectedType("");

      // Clear progress after a delay
      setTimeout(() => {
        setUploadProgress([]);
      }, 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Upload Medical Data
        </h1>
        <p className="mt-2 text-gray-600">
          Upload your medical data for analysis and diagnosis
        </p>
      </div>

      {error && (
        <Alert
          type="error"
          message={error}
          onClose={() => setError("")}
          className="mb-6"
        />
      )}

      {success && (
        <Alert
          type="success"
          message={success}
          onClose={() => setSuccess("")}
          className="mb-6"
        />
      )}

      <div className="space-y-6">
        {/* Data Type Selection */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-xl font-semibold text-gray-900">
              Select Data Type
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {dataTypes.map((type) => (
              <button
                key={type.value}
                onClick={() => setSelectedType(type.value)}
                className={`p-4 border-2 rounded-lg text-left transition-all duration-200 ${
                  selectedType === type.value
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
                disabled={isUploading}
              >
                <h3 className="font-medium text-gray-900">{type.label}</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Supported: {type.accept}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* File Upload */}
        {selectedType && (
          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-gray-900">
                Upload Files
              </h2>
            </div>

            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors duration-200 ${
                isDragActive
                  ? "border-blue-400 bg-blue-50"
                  : "border-gray-300 hover:border-gray-400"
              } ${isUploading ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              <input {...getInputProps()} />
              <CloudArrowUpIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              {isDragActive ? (
                <p className="text-blue-600">Drop the files here...</p>
              ) : (
                <div>
                  <p className="text-gray-600 mb-2">
                    Drag and drop files here, or click to select
                  </p>
                  <p className="text-sm text-gray-500">
                    Supported formats: {selectedTypeConfig?.accept}
                  </p>
                  <p className="text-sm text-gray-500">
                    Maximum file size: 100MB
                  </p>
                </div>
              )}
            </div>

            {/* File List */}
            {files.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Selected Files ({files.length})
                </h3>
                <div className="space-y-3">
                  {files.map((file, index) => (
                    <div
                      key={`${file.name}-${index}`}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-center">
                        <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {file.name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {(file.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                      </div>
                      {!isUploading && (
                        <button
                          onClick={() => removeFile(index)}
                          className="text-gray-400 hover:text-red-500"
                          title="Remove file"
                        >
                          <XMarkIcon className="h-5 w-5" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Upload Progress */}
            {uploadProgress.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Upload Progress
                </h3>
                <div className="space-y-3">
                  {uploadProgress.map((item, index) => (
                    <div key={index} className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-900">
                          {item.fileName}
                        </span>
                        <div className="flex items-center">
                          {item.status === "completed" && (
                            <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                          )}
                          {item.status === "uploading" && (
                            <LoadingSpinner size="sm" className="mr-2" />
                          )}
                          <span
                            className={`text-sm font-medium ${
                              item.status === "completed"
                                ? "text-green-600"
                                : item.status === "error"
                                ? "text-red-600"
                                : "text-blue-600"
                            }`}
                          >
                            {item.status === "completed"
                              ? "Completed"
                              : item.status === "error"
                              ? "Failed"
                              : "Uploading"}
                          </span>
                        </div>
                      </div>
                      {item.status !== "error" && (
                        <ProgressBar
                          progress={item.progress}
                          showPercentage={false}
                        />
                      )}
                      {item.error && (
                        <p className="text-sm text-red-600 mt-1">
                          {item.error}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Upload Button */}
            {files.length > 0 && (
              <div className="mt-6">
                <button
                  onClick={uploadFiles}
                  disabled={isUploading}
                  className="btn-primary w-full flex items-center justify-center"
                >
                  {isUploading ? (
                    <>
                      <LoadingSpinner
                        size="sm"
                        color="white"
                        className="mr-2"
                      />
                      Uploading...
                    </>
                  ) : (
                    `Upload ${files.length} File(s)`
                  )}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Instructions */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-xl font-semibold text-gray-900">
              Upload Guidelines
            </h2>
          </div>
          <div className="space-y-4 text-sm text-gray-600">
            <div>
              <h3 className="font-medium text-gray-900">
                Handwriting Samples:
              </h3>
              <p>
                Upload clear images of handwriting tasks (spirals, waves,
                sentences). Ensure good lighting and contrast.
              </p>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Voice Recordings:</h3>
              <p>
                Record clear audio files with sustained vowels, reading
                passages, or speech tasks. Minimize background noise.
              </p>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">ECG Data:</h3>
              <p>
                Upload ECG readings in CSV, TXT, or JSON format with proper time
                series data.
              </p>
            </div>
            {/* MRI section removed during cleanup */}
            <div>
              <h3 className="font-medium text-gray-900">Doctor Notes:</h3>
              <p>
                Upload medical reports, consultation notes, or clinical
                assessments in PDF or document format.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
