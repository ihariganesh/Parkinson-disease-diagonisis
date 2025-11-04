"""
Speech Feature Extraction Pipeline for Parkinson's Disease Detection
Uses librosa and parselmouth to extract comprehensive speech features from audio files
"""

import numpy as np
import pandas as pd
import librosa
import os
import scipy.stats
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')

# Try to import parselmouth, but make it optional
try:
    import parselmouth
    from parselmouth.praat import call
    PARSELMOUTH_AVAILABLE = True
    print("✓ Parselmouth available - using high-quality Praat features")
except ImportError:
    PARSELMOUTH_AVAILABLE = False
    print("⚠️  Warning: parselmouth not available. Install with: pip install praat-parselmouth")
    print("   Some speech features will be estimated using alternative methods.")

class SpeechFeatureExtractor:
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
        self.features = {}
        
    def load_audio(self, audio_path):
        """Load audio file using librosa"""
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Remove silence from the beginning and end
            y_trimmed, _ = librosa.effects.trim(y, top_db=20)
            
            return y_trimmed, sr
        except Exception as e:
            print(f"Error loading audio: {e}")
            return None, None
            
    def extract_praat_features(self, audio_path):
        """Extract Praat-based features using parselmouth or alternative methods"""
        if not PARSELMOUTH_AVAILABLE:
            return self._extract_alternative_features(audio_path)
            
        try:
            # Load audio using parselmouth
            sound = parselmouth.Sound(audio_path)
            
            # Create pitch object
            pitch = call(sound, "To Pitch", 0.0, 75, 600)  # f0 range: 75-600 Hz
            
            # Extract fundamental frequency (F0)
            f0_values = pitch.selected_array['frequency']
            f0_values = f0_values[f0_values != 0]  # Remove unvoiced frames
            
            features = {}
            
            if len(f0_values) > 0:
                # Basic F0 statistics
                features['mean_f0'] = np.mean(f0_values)
                features['std_f0'] = np.std(f0_values)
                features['min_f0'] = np.min(f0_values)
                features['max_f0'] = np.max(f0_values)
                features['median_f0'] = np.median(f0_values)
                features['range_f0'] = features['max_f0'] - features['min_f0']
                
                # Calculate jitter (period-to-period variation)
                periods = 1.0 / f0_values
                if len(periods) > 1:
                    period_diffs = np.abs(np.diff(periods))
                    features['jitter_abs'] = np.mean(period_diffs)
                    features['jitter_rel'] = features['jitter_abs'] / np.mean(periods)
                    features['jitter_ppq5'] = self._calculate_ppq(periods, 5)
                    features['jitter_ddp'] = np.mean(np.abs(np.diff(period_diffs)))
                else:
                    features['jitter_abs'] = 0
                    features['jitter_rel'] = 0
                    features['jitter_ppq5'] = 0
                    features['jitter_ddp'] = 0
                    
            else:
                # Default values when no F0 is found
                for key in ['mean_f0', 'std_f0', 'min_f0', 'max_f0', 'median_f0', 
                           'range_f0', 'jitter_abs', 'jitter_rel', 'jitter_ppq5', 'jitter_ddp']:
                    features[key] = 0
                    
            # Extract amplitude-based features (shimmer)
            try:
                pointprocess = call(sound, "To PointProcess (periodic, cc)", 75, 600)
                amplitudes = []
                
                # Get amplitude at each glottal pulse
                for i in range(call(pointprocess, "Get number of points")):
                    time = call(pointprocess, "Get time from index", i + 1)
                    amplitude = call(sound, "Get value at time", time, "Cubic")
                    amplitudes.append(abs(amplitude))
                
                amplitudes = np.array(amplitudes)
                
                if len(amplitudes) > 1:
                    # Calculate shimmer (amplitude variation)
                    amp_diffs = np.abs(np.diff(amplitudes))
                    features['shimmer_abs'] = np.mean(amp_diffs)
                    features['shimmer_rel'] = features['shimmer_abs'] / np.mean(amplitudes)
                    features['shimmer_apq3'] = self._calculate_apq(amplitudes, 3)
                    features['shimmer_apq5'] = self._calculate_apq(amplitudes, 5)
                    features['shimmer_apq11'] = self._calculate_apq(amplitudes, 11)
                    features['shimmer_dda'] = np.mean(np.abs(np.diff(amp_diffs)))
                else:
                    for key in ['shimmer_abs', 'shimmer_rel', 'shimmer_apq3', 
                               'shimmer_apq5', 'shimmer_apq11', 'shimmer_dda']:
                        features[key] = 0
                        
            except:
                for key in ['shimmer_abs', 'shimmer_rel', 'shimmer_apq3', 
                           'shimmer_apq5', 'shimmer_apq11', 'shimmer_dda']:
                    features[key] = 0
                    
            # Harmonics-to-Noise Ratio
            try:
                harmonicity = call(sound, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
                hnr_values = harmonicity.values[harmonicity.values != -200]  # Remove undefined values
                
                if len(hnr_values) > 0:
                    features['hnr_mean'] = np.mean(hnr_values)
                    features['hnr_std'] = np.std(hnr_values)
                    features['hnr_min'] = np.min(hnr_values)
                    features['hnr_max'] = np.max(hnr_values)
                else:
                    features['hnr_mean'] = 0
                    features['hnr_std'] = 0
                    features['hnr_min'] = 0
                    features['hnr_max'] = 0
            except:
                features['hnr_mean'] = 0
                features['hnr_std'] = 0
                features['hnr_min'] = 0
                features['hnr_max'] = 0
                
            return features
            
        except Exception as e:
            print(f"Error in Praat feature extraction: {e}")
            return {}
    
    def _extract_alternative_features(self, audio_path):
        """Extract speech features using librosa when parselmouth is not available"""
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            y_trimmed, _ = librosa.effects.trim(y, top_db=20)
            
            # Extract fundamental frequency using librosa
            f0 = librosa.yin(y_trimmed, fmin=75, fmax=600, sr=sr)
            f0_values = f0[f0 > 0]  # Remove unvoiced frames
            
            features = {}
            
            if len(f0_values) > 0:
                # Basic F0 statistics (approximate parselmouth features)
                features['mean_f0'] = np.mean(f0_values)
                features['std_f0'] = np.std(f0_values)
                features['min_f0'] = np.min(f0_values)
                features['max_f0'] = np.max(f0_values)
                
                # Approximate jitter and shimmer calculations
                f0_diff = np.abs(np.diff(f0_values))
                features['jitter_percent'] = np.mean(f0_diff) / np.mean(f0_values) * 100 if len(f0_diff) > 0 else 0
                features['jitter_abs'] = np.mean(f0_diff) if len(f0_diff) > 0 else 0
                features['jitter_rap'] = np.mean(f0_diff) / np.mean(f0_values) if len(f0_diff) > 0 else 0
                features['jitter_ppq5'] = features['jitter_percent']  # Approximation
                features['jitter_ddp'] = features['jitter_rap'] * 3  # Approximation
                
                # Approximate shimmer using amplitude envelope
                amplitude = np.abs(y_trimmed)
                amplitude_smooth = librosa.util.smooth(amplitude, length=512)
                amp_diff = np.abs(np.diff(amplitude_smooth))
                features['shimmer_percent'] = np.mean(amp_diff) / np.mean(amplitude_smooth) * 100 if len(amp_diff) > 0 else 0
                features['shimmer_abs'] = np.mean(amp_diff) if len(amp_diff) > 0 else 0
                features['shimmer_apq3'] = features['shimmer_percent']  # Approximation
                features['shimmer_apq5'] = features['shimmer_percent']  # Approximation
                features['shimmer_apq11'] = features['shimmer_percent']  # Approximation
                features['shimmer_dda'] = features['shimmer_apq3'] * 3  # Approximation
                
                # Approximate Harmonics-to-Noise Ratio using spectral features
                spec_centroid = librosa.feature.spectral_centroid(y=y_trimmed, sr=sr)[0]
                spec_rolloff = librosa.feature.spectral_rolloff(y=y_trimmed, sr=sr)[0]
                features['hnr_mean'] = np.mean(spec_centroid / spec_rolloff) * 20  # Rough approximation
                features['hnr_std'] = np.std(spec_centroid / spec_rolloff) * 20
                features['hnr_min'] = np.min(spec_centroid / spec_rolloff) * 20
                features['hnr_max'] = np.max(spec_centroid / spec_rolloff) * 20
            else:
                # Default values when no F0 detected
                for feature in ['mean_f0', 'std_f0', 'min_f0', 'max_f0', 'jitter_percent', 'jitter_abs', 
                               'jitter_rap', 'jitter_ppq5', 'jitter_ddp', 'shimmer_percent', 'shimmer_abs',
                               'shimmer_apq3', 'shimmer_apq5', 'shimmer_apq11', 'shimmer_dda', 
                               'hnr_mean', 'hnr_std', 'hnr_min', 'hnr_max']:
                    features[feature] = 0
                    
            return features
            
        except Exception as e:
            print(f"Error in alternative feature extraction: {e}")
            return {}
            
    def _calculate_ppq(self, periods, n):
        """Calculate Period Perturbation Quotient"""
        if len(periods) < n:
            return 0
        
        ppq_values = []
        for i in range(n//2, len(periods) - n//2):
            window = periods[i-n//2:i+n//2+1]
            mean_period = np.mean(window)
            ppq_values.append(abs(periods[i] - mean_period) / mean_period)
        
        return np.mean(ppq_values) if ppq_values else 0
        
    def _calculate_apq(self, amplitudes, n):
        """Calculate Amplitude Perturbation Quotient"""
        if len(amplitudes) < n:
            return 0
            
        apq_values = []
        for i in range(n//2, len(amplitudes) - n//2):
            window = amplitudes[i-n//2:i+n//2+1]
            mean_amplitude = np.mean(window)
            apq_values.append(abs(amplitudes[i] - mean_amplitude) / mean_amplitude)
            
        return np.mean(apq_values) if apq_values else 0
        
    def extract_librosa_features(self, y, sr):
        """Extract features using librosa"""
        features = {}
        
        try:
            # MFCC features (0-12 coefficients)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for i in range(13):
                features[f'MFCC_{i}_mean'] = np.mean(mfccs[i])
                features[f'MFCC_{i}_std'] = np.std(mfccs[i])
                features[f'MFCC_{i}_min'] = np.min(mfccs[i])
                features[f'MFCC_{i}_max'] = np.max(mfccs[i])
                features[f'MFCC_{i}_median'] = np.median(mfccs[i])
                features[f'MFCC_{i}_skew'] = scipy.stats.skew(mfccs[i])
                features[f'MFCC_{i}_kurtosis'] = scipy.stats.kurtosis(mfccs[i])
                
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features['spectral_centroid_mean'] = np.mean(spectral_centroids)
            features['spectral_centroid_std'] = np.std(spectral_centroids)
            features['spectral_centroid_min'] = np.min(spectral_centroids)
            features['spectral_centroid_max'] = np.max(spectral_centroids)
            
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            features['spectral_bandwidth_mean'] = np.mean(spectral_bandwidth)
            features['spectral_bandwidth_std'] = np.std(spectral_bandwidth)
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            features['spectral_rolloff_mean'] = np.mean(spectral_rolloff)
            features['spectral_rolloff_std'] = np.std(spectral_rolloff)
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            features['zcr_mean'] = np.mean(zcr)
            features['zcr_std'] = np.std(zcr)
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            for i in range(12):
                features[f'chroma_{i}_mean'] = np.mean(chroma[i])
                features[f'chroma_{i}_std'] = np.std(chroma[i])
                
            # Mel-frequency features
            mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
            features['mel_mean'] = np.mean(mel_spectrogram)
            features['mel_std'] = np.std(mel_spectrogram)
            features['mel_min'] = np.min(mel_spectrogram)
            features['mel_max'] = np.max(mel_spectrogram)
            
            # Energy features
            energy = np.sum(y**2)
            features['energy'] = energy
            
            # RMS energy
            rms = librosa.feature.rms(y=y)[0]
            features['rms_mean'] = np.mean(rms)
            features['rms_std'] = np.std(rms)
            features['rms_min'] = np.min(rms)
            features['rms_max'] = np.max(rms)
            
            # Tempo
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = tempo
            
        except Exception as e:
            print(f"Error in librosa feature extraction: {e}")
            
        return features
        
    def extract_statistical_features(self, y):
        """Extract basic statistical features from the audio signal"""
        features = {}
        
        try:
            # Basic statistics
            features['mean_amplitude'] = np.mean(y)
            features['std_amplitude'] = np.std(y)
            features['min_amplitude'] = np.min(y)
            features['max_amplitude'] = np.max(y)
            features['median_amplitude'] = np.median(y)
            features['skewness'] = scipy.stats.skew(y)
            features['kurtosis'] = scipy.stats.kurtosis(y)
            features['range_amplitude'] = features['max_amplitude'] - features['min_amplitude']
            
            # Entropy
            # Calculate spectral entropy
            S = np.abs(librosa.stft(y))
            entropy = -np.sum((S / np.sum(S)) * np.log2(S / np.sum(S) + 1e-8))
            features['spectral_entropy'] = entropy
            
        except Exception as e:
            print(f"Error in statistical feature extraction: {e}")
            
        return features
        
    def extract_all_features(self, audio_path):
        """Extract all features from an audio file"""
        print(f"Extracting features from: {audio_path}")
        
        # Load audio
        y, sr = self.load_audio(audio_path)
        if y is None:
            return None
            
        # Extract features from different methods
        praat_features = self.extract_praat_features(audio_path)
        librosa_features = self.extract_librosa_features(y, sr)
        statistical_features = self.extract_statistical_features(y)
        
        # Combine all features
        all_features = {**praat_features, **librosa_features, **statistical_features}
        
        print(f"Extracted {len(all_features)} features")
        return all_features
        
    def extract_features_to_dataframe(self, audio_path):
        """Extract features and return as a pandas DataFrame"""
        features = self.extract_all_features(audio_path)
        
        if features is None:
            return None
            
        # Convert to DataFrame
        df = pd.DataFrame([features])
        
        return df
        
    def get_feature_statistics(self):
        """Get statistics about the features that can be extracted"""
        # Create a dummy signal to test feature extraction
        duration = 2  # seconds
        sr = self.sample_rate
        t = np.linspace(0, duration, sr * duration)
        
        # Create a synthetic voice-like signal
        fundamental_freq = 150  # Hz
        signal = (np.sin(2 * np.pi * fundamental_freq * t) + 
                  0.5 * np.sin(2 * np.pi * fundamental_freq * 2 * t) +
                  0.25 * np.sin(2 * np.pi * fundamental_freq * 3 * t))
        signal += 0.1 * np.random.randn(len(signal))
        
        # Save as temporary file
        import tempfile
        import soundfile as sf
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            sf.write(temp_file.name, signal, sr)
            features = self.extract_all_features(temp_file.name)
            os.unlink(temp_file.name)
            
        if features:
            feature_categories = {
                'praat_features': len([f for f in features.keys() if any(key in f.lower() for key in ['jitter', 'shimmer', 'hnr', 'f0'])]),
                'mfcc_features': len([f for f in features.keys() if 'mfcc' in f.lower()]),
                'spectral_features': len([f for f in features.keys() if 'spectral' in f.lower()]),
                'chroma_features': len([f for f in features.keys() if 'chroma' in f.lower()]),
                'energy_features': len([f for f in features.keys() if any(key in f.lower() for key in ['energy', 'rms'])]),
                'statistical_features': len([f for f in features.keys() if any(key in f.lower() for key in ['mean', 'std', 'min', 'max', 'median', 'skew', 'kurtosis'])]),
                'other_features': 0
            }
            
            # Count other features
            counted_features = sum(feature_categories.values())
            feature_categories['other_features'] = len(features) - counted_features
            
            return {
                'total_features': len(features),
                'parselmouth_available': PARSELMOUTH_AVAILABLE,
                'feature_categories': feature_categories,
                'feature_names': list(features.keys()),
                'dependencies': {
                    'librosa': True,  # Always available if we get here
                    'parselmouth': PARSELMOUTH_AVAILABLE,
                    'numpy': True,
                    'soundfile': True
                }
            }
        return None

def test_feature_extraction():
    """Test the feature extraction pipeline"""
    extractor = SpeechFeatureExtractor()
    
    # Get feature statistics
    stats = extractor.get_feature_statistics()
    if stats:
        print("=== Feature Extraction Statistics ===")
        print(f"✓ Total features extractable: {stats['total_features']}")
        print(f"✓ Parselmouth available: {stats['parselmouth_available']}")
        print("\nFeature breakdown:")
        for category, count in stats['feature_categories'].items():
            print(f"  - {category}: {count}")
        print(f"\nFirst 10 features: {stats['feature_names'][:10]}")
    else:
        print("❌ Feature extraction test failed")
        
    # Test with actual file if available
    test_files = ["test_audio.wav", "test_audio.mp3"]
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n=== Testing with {test_file} ===")
            features = extractor.extract_all_features(test_file)
            if features:
                print(f"✓ Extracted {len(features)} features from {test_file}")
            else:
                print(f"❌ Failed to extract features from {test_file}")
            break

def test_feature_extraction_legacy():
    """Legacy test function - kept for compatibility"""
    extractor = SpeechFeatureExtractor()
    
    # Create a dummy audio file for testing (you can replace with actual audio)
    print("Testing feature extraction...")
    
    # Generate a test signal
    duration = 5  # seconds
    sr = 22050
    t = np.linspace(0, duration, sr * duration)
    
    # Create a synthetic voice-like signal
    fundamental_freq = 150  # Hz
    signal = (np.sin(2 * np.pi * fundamental_freq * t) + 
              0.5 * np.sin(2 * np.pi * fundamental_freq * 2 * t) +
              0.25 * np.sin(2 * np.pi * fundamental_freq * 3 * t))
    
    # Add some noise
    signal += 0.1 * np.random.randn(len(signal))
    
    # Save as temporary file
    import soundfile as sf
    temp_path = "temp_test_audio.wav"
    sf.write(temp_path, signal, sr)
    
    try:
        # Extract features
        features_df = extractor.extract_features_to_dataframe(temp_path)
        
        if features_df is not None:
            print(f"Successfully extracted {len(features_df.columns)} features")
            print("\nFirst few features:")
            print(features_df.head())
        else:
            print("Feature extraction failed")
            
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    test_feature_extraction()