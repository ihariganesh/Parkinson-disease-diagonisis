import { useState, useRef } from 'react';
import { Mic, Upload, Play, Pause, Square, Trash2, Download, AlertCircle, CheckCircle } from 'lucide-react';
import { Alert, Loading } from '../common';
import { useAuth } from '../../contexts/AuthContext';

interface SpeechAnalysisResult {
  prediction_probability: number;
  predicted_class: number;
  class_label: string;
  confidence: number;
  risk_level: string;
  interpretation: string;
  analysis_timestamp: string;
}

interface SpeechAnalysisProps {
  onAnalysisComplete?: (result: SpeechAnalysisResult) => void;
}

export const SpeechAnalysis: React.FC<SpeechAnalysisProps> = ({ onAnalysisComplete }) => {
  const { state } = useAuth();
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<SpeechAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const intervalRef = useRef<number | null>(null);

  const startRecording = async () => {
    try {
      setError(null);
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      });
      
      streamRef.current = stream;
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      
      const chunks: BlobPart[] = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm;codecs=opus' });
        setRecordedBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        
        // Clean up stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start timer
      intervalRef.current = window.setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (err) {
      setError('Could not access microphone. Please check permissions.');
      console.error('Error accessing microphone:', err);
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }
  };

  const resumeRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      intervalRef.current = window.setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      
      if (intervalRef.current) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }
  };

  const clearRecording = () => {
    setRecordedBlob(null);
    setAudioUrl(null);
    setRecordingTime(0);
    setAnalysisResult(null);
    setError(null);
    setIsPlaying(false);
    
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
  };

  const downloadRecording = () => {
    if (recordedBlob) {
      const url = URL.createObjectURL(recordedBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `speech-recording-${new Date().toISOString().slice(0, 19)}.webm`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('audio/')) {
        setError('Please select an audio file');
        return;
      }

      // Validate file size (50MB limit)
      if (file.size > 50 * 1024 * 1024) {
        setError('File size too large. Please select a file smaller than 50MB');
        return;
      }

      setRecordedBlob(file);
      setAudioUrl(URL.createObjectURL(file));
      setError(null);
      setAnalysisResult(null);
    }
  };

  const playAudio = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const analyzeAudio = async () => {
    if (!recordedBlob) {
      setError('No audio recording to analyze');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      
      // Determine the filename based on whether it's a File (uploaded) or Blob (recorded)
      let filename: string;
      if (recordedBlob instanceof File) {
        // Uploaded file - use original filename
        filename = recordedBlob.name;
      } else {
        // Recorded blob - use default recording name
        filename = 'speech-recording.webm';
      }
      
      formData.append('file', recordedBlob, filename);

      // Use demo endpoint if not authenticated
      const endpoint = state.isAuthenticated 
        ? '/api/v1/analysis/speech/analyze'
        : '/api/v1/analysis/speech/demo-analyze';

      const headers: HeadersInit = {};
      if (state.isAuthenticated && localStorage.getItem('auth_token')) {
        headers['Authorization'] = `Bearer ${localStorage.getItem('auth_token')}`;
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers,
        body: formData
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`;
        try {
          // First, get the response text
          const responseText = await response.text();
          console.log('Error response text:', responseText);
          
          // Try to parse as JSON
          try {
            const errorData = JSON.parse(responseText);
            errorMessage = errorData.detail || errorMessage;
          } catch (jsonError) {
            // If JSON parsing fails, use the raw text
            errorMessage = responseText || errorMessage;
          }
        } catch (e) {
          console.log('Error reading response:', e);
        }
        throw new Error(errorMessage);
      }

      const responseText = await response.text();
      console.log('Response text:', responseText);

      let data;
      try {
        data = JSON.parse(responseText);
      } catch (e) {
        console.error('JSON parsing error:', e);
        console.error('Response that failed to parse:', responseText);
        throw new Error('Invalid response format from server');
      }
      
      if (data.success && data.analysis_result) {
        setAnalysisResult(data.analysis_result);
        onAnalysisComplete?.(data.analysis_result);
      } else {
        throw new Error('Analysis failed');
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case 'low': return 'text-green-600';
      case 'moderate': return 'text-yellow-600';
      case 'high': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Speech Analysis</h2>
        
        {error && (
          <Alert type="error" message={error} className="mb-4" />
        )}

        {/* Recording Controls */}
        <div className="space-y-6">
          {/* Record New Audio */}
          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Record New Audio</h3>
            
            <div className="flex items-center gap-4 mb-4">
              {!isRecording ? (
                <button
                  onClick={startRecording}
                  className="flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
                  disabled={isAnalyzing}
                >
                  <Mic className="w-5 h-5" />
                  Start Recording
                </button>
              ) : (
                <div className="flex items-center gap-2">
                  {!isPaused ? (
                    <button
                      onClick={pauseRecording}
                      className="flex items-center gap-2 bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded-lg transition-colors"
                    >
                      <Pause className="w-5 h-5" />
                      Pause
                    </button>
                  ) : (
                    <button
                      onClick={resumeRecording}
                      className="flex items-center gap-2 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors"
                    >
                      <Play className="w-5 h-5" />
                      Resume
                    </button>
                  )}
                  
                  <button
                    onClick={stopRecording}
                    className="flex items-center gap-2 bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    <Square className="w-5 h-5" />
                    Stop
                  </button>
                </div>
              )}
              
              {(isRecording || isPaused) && (
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${isRecording && !isPaused ? 'bg-red-500 animate-pulse' : 'bg-gray-400'}`} />
                  <span className="text-lg font-mono">{formatTime(recordingTime)}</span>
                </div>
              )}
            </div>

            <p className="text-sm text-gray-600">
              Speak clearly for at least 10-15 seconds. You can say vowels (ah, eh, oh), read a passage, or speak naturally.
            </p>
          </div>

          {/* Upload Audio File */}
          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Upload Audio File</h3>
            
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg cursor-pointer transition-colors">
                <Upload className="w-5 h-5" />
                Choose File
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={isAnalyzing}
                />
              </label>
              
              <span className="text-sm text-gray-600">
                Supported formats: WAV, MP3, M4A, FLAC, OGG (max 50MB)
              </span>
            </div>
          </div>

          {/* Audio Preview and Analysis */}
          {recordedBlob && (
            <div className="border rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">Audio Preview</h3>
              
              <div className="flex items-center gap-4 mb-4">
                <button
                  onClick={playAudio}
                  className="flex items-center gap-2 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors"
                  disabled={isAnalyzing}
                >
                  {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                  {isPlaying ? 'Pause' : 'Play'}
                </button>
                
                <button
                  onClick={downloadRecording}
                  className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
                  disabled={isAnalyzing}
                >
                  <Download className="w-5 h-5" />
                  Download
                </button>
                
                <button
                  onClick={clearRecording}
                  className="flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
                  disabled={isAnalyzing}
                >
                  <Trash2 className="w-5 h-5" />
                  Clear
                </button>
              </div>

              <audio
                ref={audioRef}
                src={audioUrl || undefined}
                onEnded={() => setIsPlaying(false)}
                className="w-full mb-4"
                controls
              />

              <button
                onClick={analyzeAudio}
                disabled={isAnalyzing}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white py-3 px-6 rounded-lg font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isAnalyzing ? <Loading className="inline mr-2" /> : null}
                {isAnalyzing ? 'Analyzing Speech...' : 'Analyze Speech'}
              </button>
            </div>
          )}

          {/* Analysis Results */}
          {analysisResult && (
            <div className="border rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                Analysis Results
              </h3>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-gray-800 mb-2">Prediction</h4>
                    <p className="text-lg">
                      <span className="font-bold">{analysisResult.class_label}</span>
                    </p>
                    <p className="text-sm text-gray-600">
                      Probability: {(analysisResult.prediction_probability * 100).toFixed(1)}%
                    </p>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-gray-800 mb-2">Risk Level</h4>
                    <p className={`text-lg font-bold ${getRiskColor(analysisResult.risk_level)}`}>
                      {analysisResult.risk_level}
                    </p>
                    <p className="text-sm text-gray-600">
                      Confidence: {(analysisResult.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
                
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    Interpretation
                  </h4>
                  <p className="text-sm text-gray-700 leading-relaxed">
                    {analysisResult.interpretation}
                  </p>
                </div>
              </div>
              
              <div className="mt-4 text-xs text-gray-500">
                Analysis completed on: {new Date(analysisResult.analysis_timestamp).toLocaleString()}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SpeechAnalysis;