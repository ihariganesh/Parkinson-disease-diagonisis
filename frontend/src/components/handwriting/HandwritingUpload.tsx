import { useState, useRef } from 'react';
import { Upload, Camera, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

interface HandwritingUploadProps {
  onUploadComplete: (result: any) => void;
  onCancel: () => void;
  isAuthenticated?: boolean;
}

interface Prompt {
  id: string;
  type: string;
  title: string;
  description: string;
  instruction: string;
  reference_image?: string;
  sentence_prompt?: string;
}

const HandwritingUpload: React.FC<HandwritingUploadProps> = ({ onUploadComplete, onCancel, isAuthenticated = false }) => {
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const prompts: Prompt[] = [
    {
      id: 'spiral',
      type: 'spiral',
      title: 'Draw a Spiral',
      description: 'Please draw a spiral similar to the reference pattern shown below',
      instruction: 'Start from the center and draw outward in a smooth spiral motion',
      reference_image: '/static/references/spiral_reference.png'
    },
    {
      id: 'wave',
      type: 'wave',
      title: 'Draw a Wave Pattern',
      description: 'Please draw a wave pattern similar to the reference shown below',
      instruction: 'Draw smooth, continuous waves from left to right',
      reference_image: '/static/references/wave_reference.png'
    },
    {
      id: 'sentence_spiral',
      type: 'spiral',
      title: 'Write Sentence + Draw Spiral',
      description: 'First write the sentence clearly, then draw a spiral below it',
      instruction: 'Write the sentence in your normal handwriting, then draw a smooth spiral',
      sentence_prompt: 'Today is a beautiful sunny day and I feel great.'
    }
  ];

  const handlePromptSelect = (prompt: Prompt) => {
    setSelectedPrompt(prompt);
    setError(null);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      // Validate file type
      if (!selectedFile.type.startsWith('image/')) {
        setError('Please select an image file');
        return;
      }

      // Validate file size (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }

      setFile(selectedFile);
      setError(null);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!selectedPrompt || !file) {
      setError('Please select a prompt and upload an image');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('drawing_type', selectedPrompt.type);
      if (selectedPrompt.sentence_prompt) {
        formData.append('sentence_prompt', selectedPrompt.sentence_prompt);
      }

      const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
      const endpoint = isAuthenticated ? `${baseURL}/handwriting/upload` : `${baseURL}/handwriting/demo/upload`;
      const headers: any = {};
      
      if (isAuthenticated) {
        const token = localStorage.getItem('auth_token');
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers,
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      onUploadComplete(result);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleCamera = () => {
    // In a real app, this would open camera capture
    // For now, just trigger file input
    fileInputRef.current?.click();
  };

  if (!selectedPrompt) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Handwriting Analysis
          </h2>
          <p className="text-gray-600">
            Choose a drawing task to help us analyze your handwriting patterns for Parkinson's screening.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {prompts.map((prompt) => (
            <div
              key={prompt.id}
              className="border border-gray-200 rounded-lg p-6 cursor-pointer hover:border-blue-500 hover:shadow-md transition-all"
              onClick={() => handlePromptSelect(prompt)}
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {prompt.title}
              </h3>
              <p className="text-gray-600 mb-4">
                {prompt.description}
              </p>
              {prompt.sentence_prompt && (
                <div className="bg-blue-50 p-3 rounded-md mb-4">
                  <p className="text-sm font-medium text-blue-900 mb-1">
                    Write this sentence:
                  </p>
                  <p className="text-blue-800 italic">
                    "{prompt.sentence_prompt}"
                  </p>
                </div>
              )}
              <div className="flex items-center text-blue-600 font-medium">
                Select this task
                <CheckCircle className="w-4 h-4 ml-2" />
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 text-center">
          <button
            onClick={onCancel}
            className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="mb-6">
        <button
          onClick={() => setSelectedPrompt(null)}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to task selection
        </button>
        
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {selectedPrompt.title}
        </h2>
        <p className="text-gray-600 mb-4">
          {selectedPrompt.description}
        </p>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-blue-900 mb-2">Instructions:</h3>
        <p className="text-blue-800 mb-3">{selectedPrompt.instruction}</p>
        
        {selectedPrompt.sentence_prompt && (
          <div className="bg-white border border-blue-300 rounded-md p-3">
            <p className="font-medium text-blue-900 mb-1">Write this sentence:</p>
            <p className="text-lg text-blue-800 italic">
              "{selectedPrompt.sentence_prompt}"
            </p>
          </div>
        )}
      </div>

      {/* Reference Image */}
      {selectedPrompt.reference_image && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-gray-700 mb-2">Reference Pattern:</h3>
          <div className="bg-white border-2 border-gray-300 rounded-lg p-4 flex items-center justify-center">
            <img 
              src="/spiral-reference.png" 
              alt="Reference spiral pattern"
              className="max-h-40 max-w-full object-contain rounded-lg"
            />
          </div>
        </div>
      )}

      {/* File Upload */}
      <div className="border border-gray-200 rounded-lg p-6 mb-6">
        <h3 className="font-semibold text-gray-900 mb-4">Upload Your Drawing</h3>
        
        {!file ? (
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <div className="flex flex-col items-center">
              <Upload className="w-12 h-12 text-gray-400 mb-4" />
              <p className="text-gray-600 mb-4">
                Upload a clear photo or scan of your drawing
              </p>
              <div className="flex gap-4">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
                >
                  <Upload className="w-4 h-4" />
                  Choose File
                </button>
                <button
                  onClick={handleCamera}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                >
                  <Camera className="w-4 h-4" />
                  Take Photo
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-md">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="text-green-800">{file.name}</span>
              </div>
              <button
                onClick={() => {
                  setFile(null);
                  setPreview(null);
                }}
                className="text-red-600 hover:text-red-800"
              >
                Remove
              </button>
            </div>
            
            {preview && (
              <div className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">Preview:</h4>
                <img
                  src={preview}
                  alt="Preview"
                  className="max-w-full h-auto max-h-64 mx-auto border border-gray-200 rounded"
                />
              </div>
            )}
          </div>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-4 justify-end">
        <button
          onClick={onCancel}
          className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          disabled={uploading}
        >
          Cancel
        </button>
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {uploading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            'Upload & Analyze'
          )}
        </button>
      </div>
    </div>
  );
};

export default HandwritingUpload;