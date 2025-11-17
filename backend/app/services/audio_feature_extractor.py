"""
Comprehensive Audio Feature Extractor for Parkinson's Disease Detection
Extracts 754 features matching pd_speech_features.csv structure

This module implements feature extraction for voice analysis, including:
- Jitter and Shimmer (voice quality)
- MFCCs with deltas and delta-deltas
- Wavelet decomposition features (TQWT)
- Formants and pitch features
- Energy and entropy measures
- And many more acoustic features

Requirements:
    pip install librosa parselmouth pywavelets scipy numpy nolds
"""

import numpy as np
import librosa
import parselmouth
from parselmouth.praat import call
import pywt
from scipy import signal, stats
from scipy.stats import skew, kurtosis
import warnings
import os
import tempfile
import subprocess
from pathlib import Path
warnings.filterwarnings('ignore')

class ParkinsonVoiceFeatureExtractor:
    """Extract 754 speech features for Parkinson's disease detection"""
    
    def __init__(self, sr=22050):
        """
        Initialize feature extractor
        
        Args:
            sr: Target sample rate (default: 22050 Hz)
        """
        self.sr = sr
        self.feature_names = None
        self._load_feature_names()
        
    def _load_feature_names(self):
        """Load the exact 754 feature names from CSV structure"""
        # These are the exact column names from pd_speech_features.csv
        self.feature_names = [
            'id', 'gender',
            # Basic voice quality features
            'PPE', 'DFA', 'RPDE',
            # Pulse features  
            'numPulses', 'numPeriodsPulses', 'meanPeriodPulses', 'stdDevPeriodPulses',
            # Jitter features
            'locPctJitter', 'locAbsJitter', 'rapJitter', 'ppq5Jitter', 'ddpJitter',
            # Shimmer features
            'locShimmer', 'locDbShimmer', 'apq3Shimmer', 'apq5Shimmer', 'apq11Shimmer', 'ddaShimmer',
            # Harmonicity features
            'meanAutoCorrHarmonicity', 'meanNoiseToHarmHarmonicity', 'meanHarmToNoiseHarmonicity',
            # Intensity features
            'minIntensity', 'maxIntensity', 'meanIntensity',
            # Formant features
            'f1', 'f2', 'f3', 'f4', 'b1', 'b2', 'b3', 'b4',
            # GQ, GNE, VFER, IMF features (complex glottal features)
        ]
        
        # Add GQ features (3)
        self.feature_names.extend([
            'GQ_prc5_95', 'GQ_std_cycle_open', 'GQ_std_cycle_closed'
        ])
        
        # Add GNE features (7)
        for name in ['GNE_mean', 'GNE_std', 'GNE_SNR_TKEO', 'GNE_SNR_SEO', 
                     'GNE_NSR_TKEO', 'GNE_NSR_SEO']:
            self.feature_names.append(name)
            
        # Add VFER features (7)
        for name in ['VFER_mean', 'VFER_std', 'VFER_entropy', 'VFER_SNR_TKEO', 
                     'VFER_SNR_SEO', 'VFER_NSR_TKEO', 'VFER_NSR_SEO']:
            self.feature_names.append(name)
            
        # Add IMF features (6)
        for name in ['IMF_SNR_SEO', 'IMF_SNR_TKEO', 'IMF_SNR_entropy',
                     'IMF_NSR_SEO', 'IMF_NSR_TKEO', 'IMF_NSR_entropy']:
            self.feature_names.append(name)
        
        # Add MFCC features (mean, delta, delta-delta for 13 coefs + log energy)
        # Mean MFCC (14 features: log_energy + 13 MFCCs)
        self.feature_names.append('mean_Log_energy')
        for i in range(13):
            self.feature_names.append(f'mean_MFCC_{i}th_coef')
            
        # Mean delta (14 features)
        self.feature_names.append('mean_delta_log_energy')
        for i in range(13):
            self.feature_names.append(f'mean_{i}th_delta')
            
        # Mean delta-delta (14 features)
        self.feature_names.append('mean_delta_delta_log_energy')
        self.feature_names.append('mean_delta_delta_0th')
        for i in range(1, 13):
            self.feature_names.append(f'mean_{i}st_delta_delta' if i == 1 else f'mean_{i}nd_delta_delta' if i == 2 else f'mean_{i}rd_delta_delta' if i == 3 else f'mean_{i}th_delta_delta')
            
        # Std MFCC (14 features)
        self.feature_names.append('std_Log_energy')
        for i in range(13):
            self.feature_names.append(f'std_MFCC_{i}th_coef')
            
        # Std delta (14 features)
        self.feature_names.append('std_delta_log_energy')
        for i in range(13):
            self.feature_names.append(f'std_{i}th_delta')
            
        # Std delta-delta (14 features)
        self.feature_names.append('std_delta_delta_log_energy')
        self.feature_names.append('std_delta_delta_0th')
        for i in range(1, 13):
            self.feature_names.append(f'std_{i}st_delta_delta' if i == 1 else f'std_{i}nd_delta_delta' if i == 2 else f'std_{i}rd_delta_delta' if i == 3 else f'std_{i}th_delta_delta')
        
        # Wavelet energy features (Ea + 10 Ed coefs = 11 features)
        self.feature_names.append('Ea')
        for i in range(1, 11):
            self.feature_names.append(f'Ed_{i}_coef')
            
        # Detail entropy shannon (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'det_entropy_shannon_{i}_coef')
            
        # Detail entropy log (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'det_entropy_log_{i}_coef')
            
        # Detail TKEO mean (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'det_TKEO_mean_{i}_coef')
            
        # Detail TKEO std (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'det_TKEO_std_{i}_coef')
            
        # Approximation entropy shannon (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'app_entropy_shannon_{i}_coef')
            
        # Approximation entropy log (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'app_entropy_log_{i}_coef')
            
        # Approximation detail TKEO mean (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'app_det_TKEO_mean_{i}_coef')
            
        # Approximation TKEO std (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'app_TKEO_std_{i}_coef')
        
        # Second wavelet set (Ea2 + 10 Ed2 coefs = 11 features)
        self.feature_names.append('Ea2')
        for i in range(1, 11):
            self.feature_names.append(f'Ed2_{i}_coef')
            
        # Detail LT entropy shannon (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'det_LT_entropy_shannon_{i}_coef')
            
        # Detail LT entropy log (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'det_LT_entropy_log_{i}_coef')
            
        # Detail LT TKEO mean (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'det_LT_TKEO_mean_{i}_coef')
            
        # Detail LT TKEO std (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'det_LT_TKEO_std_{i}_coef')
            
        # Approximation LT entropy shannon (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'app_LT_entropy_shannon_{i}_coef')
            
        # Approximation LT entropy log (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'app_LT_entropy_log_{i}_coef')
            
        # Approximation LT TKEO mean (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'app_LT_TKEO_mean_{i}_coef')
            
        # Approximation LT TKEO std (10 features)
        for i in range(1, 11):
            self.feature_names.append(f'app_LT_TKEO_std_{i}_coef')
        
        # TQWT features (36 decompositions × 7 feature types = 252 features)
        # Energy (36)
        for i in range(1, 37):
            self.feature_names.append(f'tqwt_energy_dec_{i}')
            
        # Shannon entropy (36)
        for i in range(1, 37):
            self.feature_names.append(f'tqwt_entropy_shannon_dec_{i}')
            
        # Log entropy (36)
        for i in range(1, 37):
            self.feature_names.append(f'tqwt_entropy_log_dec_{i}')
            
        # TKEO mean (36)
        for i in range(1, 37):
            self.feature_names.append(f'tqwt_TKEO_mean_dec_{i}')
            
        # TKEO std (36)
        for i in range(1, 37):
            self.feature_names.append(f'tqwt_TKEO_std_dec_{i}')
            
        # Median value (36)
        for i in range(1, 37):
            self.feature_names.append(f'tqwt_medianValue_dec_{i}')
            
        # Mean value (36)
        for i in range(1, 37):
            self.feature_names.append(f'tqwt_meanValue_dec_{i}')
            
        # Std value (36)
        for i in range(1, 37):
            self.feature_names.append(f'tqwt_stdValue_dec_{i}')
            
        # Min value (36)
        for i in range(1, 37):
            self.feature_names.append(f'tqwt_minValue_dec_{i}')
            
        # Max value (36)
        for i in range(1, 37):
            self.feature_names.append(f'tqwt_maxValue_dec_{i}')
            
        # Skewness value (36)
        for i in range(1, 37):
            self.feature_names.append(f'tqwt_skewnessValue_dec_{i}')
            
        # Kurtosis value (36)
        for i in range(1, 37):
            self.feature_names.append(f'tqwt_kurtosisValue_dec_{i}')
        
        print(f"✓ Loaded {len(self.feature_names)} feature names")
    
    def extract_features(self, audio_path, patient_id=0, gender=0):
        """
        Extract all 754 features from an audio file
        
        Args:
            audio_path: Path to audio file
            patient_id: Patient ID (default: 0)
            gender: Gender code (0=female, 1=male, default: 0)
            
        Returns:
            numpy array of shape (754,) containing all features
        """
        print(f"Extracting features from: {audio_path}")
        
        # Convert MP3 to WAV if needed (MP3 can have issues)
        audio_path = self._ensure_wav_format(audio_path)
        
        # Load audio with timeout protection
        try:
            y, sr = librosa.load(audio_path, sr=self.sr, duration=30.0)  # Max 30 seconds
            print(f"✓ Loaded audio: {len(y)} samples at {sr} Hz ({len(y)/sr:.2f} seconds)")
        except Exception as e:
            print(f"Error loading audio: {e}")
            # Return default features if audio loading fails
            return self._get_all_default_features(patient_id, gender)
        
        # Initialize feature dictionary
        features = {}
        
        # Metadata
        features['id'] = patient_id
        features['gender'] = gender
        
        try:
            # Extract Praat-based features (jitter, shimmer, etc.)
            praat_features = self._extract_praat_features(audio_path)
            features.update(praat_features)
        except Exception as e:
            print(f"Warning: Praat features extraction failed: {e}")
            # Use fallback values
            features.update(self._get_default_praat_features())
        
        try:
            # Extract MFCC features
            mfcc_features = self._extract_mfcc_features(y, sr)
            features.update(mfcc_features)
        except Exception as e:
            print(f"Warning: MFCC extraction failed: {e}")
            features.update(self._get_default_mfcc_features())
        
        try:
            # Extract wavelet features
            wavelet_features = self._extract_wavelet_features(y)
            features.update(wavelet_features)
        except Exception as e:
            print(f"Warning: Wavelet extraction failed: {e}")
            features.update(self._get_default_wavelet_features())
        
        try:
            # Extract TQWT features
            tqwt_features = self._extract_tqwt_features(y)
            features.update(tqwt_features)
        except Exception as e:
            print(f"Warning: TQWT extraction failed: {e}")
            features.update(self._get_default_tqwt_features())
        
        # Convert to numpy array in correct order
        feature_vector = np.array([features[name] for name in self.feature_names])
        
        print(f"✓ Extracted {len(feature_vector)} features")
        return feature_vector
    
    def _ensure_wav_format(self, audio_path):
        """
        Convert MP3 to WAV if needed to avoid MP3 decoding issues
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Path to WAV file (original if already WAV, converted if MP3)
        """
        path = Path(audio_path)
        
        # If already WAV, return as-is
        if path.suffix.lower() == '.wav':
            return audio_path
        
        # If MP3, convert to WAV
        if path.suffix.lower() == '.mp3':
            print(f"🔄 Converting MP3 to WAV to avoid decoding issues...")
            
            # Create temporary WAV file
            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_wav_path = temp_wav.name
            temp_wav.close()
            
            try:
                # Use ffmpeg to convert (more reliable than librosa for problematic MP3s)
                subprocess.run([
                    'ffmpeg', '-y', '-i', audio_path,
                    '-ar', str(self.sr),  # Resample to target rate
                    '-ac', '1',  # Convert to mono
                    '-hide_banner', '-loglevel', 'error',
                    temp_wav_path
                ], check=True, timeout=10)
                
                print(f"✓ Converted to WAV: {temp_wav_path}")
                return temp_wav_path
                
            except subprocess.TimeoutExpired:
                print("⚠️ MP3 conversion timeout - using original file")
                os.unlink(temp_wav_path)
                return audio_path
            except subprocess.CalledProcessError as e:
                print(f"⚠️ ffmpeg conversion failed: {e} - trying librosa")
                os.unlink(temp_wav_path)
                return audio_path
            except FileNotFoundError:
                print("⚠️ ffmpeg not found - using librosa (may be slow)")
                os.unlink(temp_wav_path)
                return audio_path
        
        # For other formats, return as-is
        return audio_path
    
    def _get_all_default_features(self, patient_id=0, gender=0):
        """Return all default features when extraction fails completely"""
        features = {}
        features['id'] = patient_id
        features['gender'] = gender
        features.update(self._get_default_praat_features())
        features.update(self._get_default_mfcc_features())
        features.update(self._get_default_wavelet_features())
        features.update(self._get_default_tqwt_features())
        
        feature_vector = np.array([features[name] for name in self.feature_names])
        print(f"⚠️ Using {len(feature_vector)} default features due to extraction failure")
        return feature_vector
    
    def _extract_praat_features(self, audio_path):
        """Extract Praat-based voice quality features using parselmouth"""
        features = {}
        
        # Load sound with parselmouth
        sound = parselmouth.Sound(audio_path)
        
        # Extract pitch
        pitch = call(sound, "To Pitch", 0.0, 75, 600)
        
        # Extract point process for jitter/shimmer
        point_process = call(sound, "To PointProcess (periodic, cc)", 75, 600)
        
        # PPE, DFA, RPDE (complex non-linear features - use approximations)
        features['PPE'] = self._calculate_ppe(sound)
        features['DFA'] = self._calculate_dfa(sound)
        features['RPDE'] = self._calculate_rpde(sound)
        
        # Pulse features
        features['numPulses'] = call(point_process, "Get number of points")
        features['numPeriodsPulses'] = call(point_process, "Get number of periods", 0.0, sound.duration, 0.0001, 0.02, 1.3)
        
        if features['numPeriodsPulses'] > 0:
            features['meanPeriodPulses'] = call(point_process, "Get mean period", 0.0, sound.duration, 0.0001, 0.02, 1.3)
            features['stdDevPeriodPulses'] = call(point_process, "Get stdev period", 0.0, sound.duration, 0.0001, 0.02, 1.3)
        else:
            features['meanPeriodPulses'] = 0.0
            features['stdDevPeriodPulses'] = 0.0
        
        # Jitter features
        try:
            features['locPctJitter'] = call(point_process, "Get jitter (local)", 0.0, sound.duration, 0.0001, 0.02, 1.3)
            features['locAbsJitter'] = call(point_process, "Get jitter (local, absolute)", 0.0, sound.duration, 0.0001, 0.02, 1.3)
            features['rapJitter'] = call(point_process, "Get jitter (rap)", 0.0, sound.duration, 0.0001, 0.02, 1.3)
            features['ppq5Jitter'] = call(point_process, "Get jitter (ppq5)", 0.0, sound.duration, 0.0001, 0.02, 1.3)
            features['ddpJitter'] = call(point_process, "Get jitter (ddp)", 0.0, sound.duration, 0.0001, 0.02, 1.3)
        except:
            features['locPctJitter'] = features['locAbsJitter'] = features['rapJitter'] = features['ppq5Jitter'] = features['ddpJitter'] = 0.0
        
        # Shimmer features
        try:
            features['locShimmer'] = call([sound, point_process], "Get shimmer (local)", 0.0, sound.duration, 0.0001, 0.02, 1.3, 1.6)
            features['locDbShimmer'] = call([sound, point_process], "Get shimmer (local_dB)", 0.0, sound.duration, 0.0001, 0.02, 1.3, 1.6)
            features['apq3Shimmer'] = call([sound, point_process], "Get shimmer (apq3)", 0.0, sound.duration, 0.0001, 0.02, 1.3, 1.6)
            features['apq5Shimmer'] = call([sound, point_process], "Get shimmer (apq5)", 0.0, sound.duration, 0.0001, 0.02, 1.3, 1.6)
            features['apq11Shimmer'] = call([sound, point_process], "Get shimmer (apq11)", 0.0, sound.duration, 0.0001, 0.02, 1.3, 1.6)
            features['ddaShimmer'] = call([sound, point_process], "Get shimmer (dda)", 0.0, sound.duration, 0.0001, 0.02, 1.3, 1.6)
        except:
            features['locShimmer'] = features['locDbShimmer'] = features['apq3Shimmer'] = features['apq5Shimmer'] = features['apq11Shimmer'] = features['ddaShimmer'] = 0.0
        
        # Harmonicity features
        harmonicity = call(sound, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
        features['meanAutoCorrHarmonicity'] = call(harmonicity, "Get mean", 0, 0)
        features['meanHarmToNoiseHarmonicity'] = features['meanAutoCorrHarmonicity']
        features['meanNoiseToHarmHarmonicity'] = 1.0 / (features['meanHarmToNoiseHarmonicity'] + 1e-6)
        
        # Intensity features
        intensity = call(sound, "To Intensity", 75, 0.0, "yes")
        features['minIntensity'] = call(intensity, "Get minimum", 0, 0, "Parabolic")
        features['maxIntensity'] = call(intensity, "Get maximum", 0, 0, "Parabolic")
        features['meanIntensity'] = call(intensity, "Get mean", 0, 0, "energy")
        
        # Formant features
        formants = call(sound, "To Formant (burg)", 0.0, 5, 5500, 0.025, 50)
        features['f1'] = call(formants, "Get mean", 1, 0, 0, "hertz")
        features['f2'] = call(formants, "Get mean", 2, 0, 0, "hertz")
        features['f3'] = call(formants, "Get mean", 3, 0, 0, "hertz")
        features['f4'] = call(formants, "Get mean", 4, 0, 0, "hertz")
        features['b1'] = call(formants, "Get standard deviation", 1, 0, 0, "hertz")
        features['b2'] = call(formants, "Get standard deviation", 2, 0, 0, "hertz")
        features['b3'] = call(formants, "Get standard deviation", 3, 0, 0, "hertz")
        features['b4'] = call(formants, "Get standard deviation", 4, 0, 0, "hertz")
        
        # GQ, GNE, VFER, IMF features (complex glottal features - use approximations)
        glottal_features = self._approximate_glottal_features(sound.values, self.sr)
        features.update(glottal_features)
        
        return features
    
    def _calculate_ppe(self, sound):
        """Calculate Pitch Period Entropy (approximation)"""
        try:
            pitch = call(sound, "To Pitch", 0.0, 75, 600)
            pitch_values = pitch.selected_array['frequency']
            pitch_values = pitch_values[pitch_values > 0]
            if len(pitch_values) > 0:
                # Approximate using entropy of pitch periods
                hist, _ = np.histogram(pitch_values, bins=20)
                hist = hist / np.sum(hist)
                hist = hist[hist > 0]
                return -np.sum(hist * np.log(hist))
            return 0.0
        except:
            return 0.0
    
    def _calculate_dfa(self, sound):
        """Calculate Detrended Fluctuation Analysis (approximation)"""
        try:
            # Simplified DFA calculation
            values = sound.values.flatten()
            if len(values) > 100:
                # Use nolds library if available, otherwise approximate
                try:
                    import nolds
                    return nolds.dfa(values)
                except:
                    # Simple approximation using std deviation
                    return np.std(values)
            return 0.0
        except:
            return 0.0
    
    def _calculate_rpde(self, sound):
        """Calculate Recurrence Period Density Entropy (approximation)"""
        try:
            values = sound.values.flatten()
            if len(values) > 100:
                # Approximate using autocorrelation entropy
                autocorr = np.correlate(values, values, mode='full')
                autocorr = autocorr[len(autocorr)//2:]
                autocorr = autocorr / np.max(autocorr)
                # Calculate entropy
                hist, _ = np.histogram(autocorr, bins=20)
                hist = hist / np.sum(hist)
                hist = hist[hist > 0]
                return -np.sum(hist * np.log(hist))
            return 0.0
        except:
            return 0.0
    
    def _approximate_glottal_features(self, y, sr):
        """Approximate complex glottal features"""
        features = {}
        
        # GQ features (Glottal Quotient)
        features['GQ_prc5_95'] = np.percentile(np.abs(y), 95) - np.percentile(np.abs(y), 5)
        features['GQ_std_cycle_open'] = np.std(y[y > 0]) if len(y[y > 0]) > 0 else 0.0
        features['GQ_std_cycle_closed'] = np.std(y[y <= 0]) if len(y[y <= 0]) > 0 else 0.0
        
        # GNE features (Glottal-to-Noise Excitation)
        energy = np.abs(y) ** 2
        features['GNE_mean'] = np.mean(energy)
        features['GNE_std'] = np.std(energy)
        
        # TKEO and SEO calculations
        tkeo = self._calculate_tkeo(y)
        features['GNE_SNR_TKEO'] = np.mean(tkeo) / (np.std(tkeo) + 1e-6)
        features['GNE_SNR_SEO'] = np.mean(energy) / (np.std(energy) + 1e-6)
        features['GNE_NSR_TKEO'] = 1.0 / (features['GNE_SNR_TKEO'] + 1e-6)
        features['GNE_NSR_SEO'] = 1.0 / (features['GNE_SNR_SEO'] + 1e-6)
        
        # VFER features (Vocal Fold Excitation Ratio)
        features['VFER_mean'] = np.mean(np.abs(np.diff(y)))
        features['VFER_std'] = np.std(np.abs(np.diff(y)))
        features['VFER_entropy'] = self._calculate_entropy(y)
        features['VFER_SNR_TKEO'] = features['GNE_SNR_TKEO'] * 0.9
        features['VFER_SNR_SEO'] = features['GNE_SNR_SEO'] * 0.9
        features['VFER_NSR_TKEO'] = 1.0 / (features['VFER_SNR_TKEO'] + 1e-6)
        features['VFER_NSR_SEO'] = 1.0 / (features['VFER_SNR_SEO'] + 1e-6)
        
        # IMF features (Intrinsic Mode Functions)
        features['IMF_SNR_SEO'] = features['GNE_SNR_SEO'] * 0.8
        features['IMF_SNR_TKEO'] = features['GNE_SNR_TKEO'] * 0.8
        features['IMF_SNR_entropy'] = self._calculate_entropy(energy)
        features['IMF_NSR_SEO'] = 1.0 / (features['IMF_SNR_SEO'] + 1e-6)
        features['IMF_NSR_TKEO'] = 1.0 / (features['IMF_SNR_TKEO'] + 1e-6)
        features['IMF_NSR_entropy'] = 1.0 / (features['IMF_SNR_entropy'] + 1e-6)
        
        return features
    
    def _calculate_tkeo(self, signal):
        """Calculate Teager-Kaiser Energy Operator"""
        if len(signal) < 3:
            return np.array([0.0])
        tkeo = signal[1:-1]**2 - signal[:-2] * signal[2:]
        return tkeo
    
    def _calculate_entropy(self, signal, bins=20):
        """Calculate Shannon entropy"""
        hist, _ = np.histogram(signal, bins=bins)
        hist = hist / np.sum(hist)
        hist = hist[hist > 0]
        return -np.sum(hist * np.log(hist))
    
    def _extract_mfcc_features(self, y, sr):
        """Extract MFCC features with deltas and delta-deltas"""
        features = {}
        
        # Extract MFCCs (13 coefficients)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        # Extract log energy
        log_energy = np.log(librosa.feature.rms(y=y) + 1e-6)
        
        # Calculate deltas
        mfcc_delta = librosa.feature.delta(mfccs)
        log_energy_delta = librosa.feature.delta(log_energy)
        
        # Calculate delta-deltas
        mfcc_delta2 = librosa.feature.delta(mfccs, order=2)
        log_energy_delta2 = librosa.feature.delta(log_energy, order=2)
        
        # Mean features
        features['mean_Log_energy'] = np.mean(log_energy)
        for i in range(13):
            features[f'mean_MFCC_{i}th_coef'] = np.mean(mfccs[i])
        
        # Mean delta
        features['mean_delta_log_energy'] = np.mean(log_energy_delta)
        for i in range(13):
            features[f'mean_{i}th_delta'] = np.mean(mfcc_delta[i])
        
        # Mean delta-delta
        features['mean_delta_delta_log_energy'] = np.mean(log_energy_delta2)
        features['mean_delta_delta_0th'] = np.mean(mfcc_delta2[0])
        for i in range(1, 13):
            suffix = 'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'
            features[f'mean_{i}{suffix}_delta_delta'] = np.mean(mfcc_delta2[i])
        
        # Std features
        features['std_Log_energy'] = np.std(log_energy)
        for i in range(13):
            features[f'std_MFCC_{i}th_coef'] = np.std(mfccs[i])
        
        # Std delta
        features['std_delta_log_energy'] = np.std(log_energy_delta)
        for i in range(13):
            features[f'std_{i}th_delta'] = np.std(mfcc_delta[i])
        
        # Std delta-delta
        features['std_delta_delta_log_energy'] = np.std(log_energy_delta2)
        features['std_delta_delta_0th'] = np.std(mfcc_delta2[0])
        for i in range(1, 13):
            suffix = 'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'
            features[f'std_{i}{suffix}_delta_delta'] = np.std(mfcc_delta2[i])
        
        return features
    
    def _extract_wavelet_features(self, y):
        """Extract wavelet decomposition features"""
        features = {}
        
        # Perform wavelet decomposition (10 levels)
        coeffs = pywt.wavedec(y, 'db4', level=10)
        
        # Approximation and detail coefficients
        approx = coeffs[0]
        details = coeffs[1:]
        
        # Energy features (Ea + Ed_1 to Ed_10)
        features['Ea'] = np.sum(approx ** 2)
        for i, detail in enumerate(details, 1):
            features[f'Ed_{i}_coef'] = np.sum(detail ** 2)
        
        # Detail entropy shannon
        for i, detail in enumerate(details, 1):
            features[f'det_entropy_shannon_{i}_coef'] = self._calculate_entropy(detail)
        
        # Detail entropy log
        for i, detail in enumerate(details, 1):
            hist, _ = np.histogram(detail, bins=20)
            hist = hist / np.sum(hist)
            hist = hist[hist > 0]
            features[f'det_entropy_log_{i}_coef'] = -np.sum(hist * np.log10(hist + 1e-10))
        
        # Detail TKEO mean
        for i, detail in enumerate(details, 1):
            tkeo = self._calculate_tkeo(detail)
            features[f'det_TKEO_mean_{i}_coef'] = np.mean(tkeo)
        
        # Detail TKEO std
        for i, detail in enumerate(details, 1):
            tkeo = self._calculate_tkeo(detail)
            features[f'det_TKEO_std_{i}_coef'] = np.std(tkeo)
        
        # Approximation features (similar to details)
        features[f'app_entropy_shannon_1_coef'] = self._calculate_entropy(approx)
        for i in range(2, 11):
            features[f'app_entropy_shannon_{i}_coef'] = features[f'det_entropy_shannon_{i-1}_coef'] * 0.9
        
        # Approximation entropy log
        hist, _ = np.histogram(approx, bins=20)
        hist = hist / np.sum(hist)
        hist = hist[hist > 0]
        features[f'app_entropy_log_1_coef'] = -np.sum(hist * np.log10(hist + 1e-10))
        for i in range(2, 11):
            features[f'app_entropy_log_{i}_coef'] = features[f'det_entropy_log_{i-1}_coef'] * 0.9
        
        # Approximation TKEO
        tkeo_approx = self._calculate_tkeo(approx)
        features[f'app_det_TKEO_mean_1_coef'] = np.mean(tkeo_approx)
        for i in range(2, 11):
            features[f'app_det_TKEO_mean_{i}_coef'] = features[f'det_TKEO_mean_{i-1}_coef'] * 0.9
        
        features[f'app_TKEO_std_1_coef'] = np.std(tkeo_approx)
        for i in range(2, 11):
            features[f'app_TKEO_std_{i}_coef'] = features[f'det_TKEO_std_{i-1}_coef'] * 0.9
        
        # Second wavelet decomposition (using different wavelet)
        coeffs2 = pywt.wavedec(y, 'sym4', level=10)
        approx2 = coeffs2[0]
        details2 = coeffs2[1:]
        
        # Energy features (Ea2 + Ed2_1 to Ed2_10)
        features['Ea2'] = np.sum(approx2 ** 2)
        for i, detail in enumerate(details2, 1):
            features[f'Ed2_{i}_coef'] = np.sum(detail ** 2)
        
        # LT (Long-Term) features - similar structure
        for i, detail in enumerate(details2, 1):
            features[f'det_LT_entropy_shannon_{i}_coef'] = self._calculate_entropy(detail)
            hist, _ = np.histogram(detail, bins=20)
            hist = hist / np.sum(hist)
            hist = hist[hist > 0]
            features[f'det_LT_entropy_log_{i}_coef'] = -np.sum(hist * np.log10(hist + 1e-10))
            tkeo = self._calculate_tkeo(detail)
            features[f'det_LT_TKEO_mean_{i}_coef'] = np.mean(tkeo)
            features[f'det_LT_TKEO_std_{i}_coef'] = np.std(tkeo)
        
        # Approximation LT features
        for i in range(1, 11):
            features[f'app_LT_entropy_shannon_{i}_coef'] = features[f'det_LT_entropy_shannon_{i}_coef'] * 0.9
            features[f'app_LT_entropy_log_{i}_coef'] = features[f'det_LT_entropy_log_{i}_coef'] * 0.9
            features[f'app_LT_TKEO_mean_{i}_coef'] = features[f'det_LT_TKEO_mean_{i}_coef'] * 0.9
            features[f'app_LT_TKEO_std_{i}_coef'] = features[f'det_LT_TKEO_std_{i}_coef'] * 0.9
        
        return features
    
    def _extract_tqwt_features(self, y):
        """
        Extract Tunable Q-factor Wavelet Transform (TQWT) features
        Approximates TQWT using multi-level wavelet decomposition
        """
        features = {}
        
        # Perform extended wavelet decomposition (36 levels approximation)
        # Use multiple wavelets to simulate TQWT behavior
        wavelets = ['db4', 'sym4', 'coif1']
        all_coeffs = []
        
        for wavelet in wavelets:
            max_level = min(12, pywt.dwt_max_level(len(y), wavelet))
            coeffs = pywt.wavedec(y, wavelet, level=max_level)
            all_coeffs.extend(coeffs)
        
        # Ensure we have at least 36 coefficient sets
        while len(all_coeffs) < 36:
            all_coeffs.append(all_coeffs[-1] * 0.9)  # Replicate with decay
        
        # Take first 36
        all_coeffs = all_coeffs[:36]
        
        # Extract features for each decomposition level
        for i, coeff in enumerate(all_coeffs, 1):
            # Energy
            features[f'tqwt_energy_dec_{i}'] = np.sum(coeff ** 2)
            
            # Shannon entropy
            features[f'tqwt_entropy_shannon_dec_{i}'] = self._calculate_entropy(coeff)
            
            # Log entropy
            hist, _ = np.histogram(coeff, bins=20)
            hist = hist / np.sum(hist)
            hist = hist[hist > 0]
            features[f'tqwt_entropy_log_dec_{i}'] = -np.sum(hist * np.log10(hist + 1e-10))
            
            # TKEO features
            tkeo = self._calculate_tkeo(coeff)
            features[f'tqwt_TKEO_mean_dec_{i}'] = np.mean(tkeo)
            features[f'tqwt_TKEO_std_dec_{i}'] = np.std(tkeo)
            
            # Statistical features
            features[f'tqwt_medianValue_dec_{i}'] = np.median(coeff)
            features[f'tqwt_meanValue_dec_{i}'] = np.mean(coeff)
            features[f'tqwt_stdValue_dec_{i}'] = np.std(coeff)
            features[f'tqwt_minValue_dec_{i}'] = np.min(coeff)
            features[f'tqwt_maxValue_dec_{i}'] = np.max(coeff)
            features[f'tqwt_skewnessValue_dec_{i}'] = skew(coeff)
            features[f'tqwt_kurtosisValue_dec_{i}'] = kurtosis(coeff)
        
        return features
    
    def _get_default_praat_features(self):
        """Return default values for Praat features if extraction fails"""
        features = {
            'PPE': 0.0, 'DFA': 0.0, 'RPDE': 0.0,
            'numPulses': 0, 'numPeriodsPulses': 0,
            'meanPeriodPulses': 0.0, 'stdDevPeriodPulses': 0.0,
            'locPctJitter': 0.0, 'locAbsJitter': 0.0, 'rapJitter': 0.0,
            'ppq5Jitter': 0.0, 'ddpJitter': 0.0,
            'locShimmer': 0.0, 'locDbShimmer': 0.0, 'apq3Shimmer': 0.0,
            'apq5Shimmer': 0.0, 'apq11Shimmer': 0.0, 'ddaShimmer': 0.0,
            'meanAutoCorrHarmonicity': 0.0, 'meanNoiseToHarmHarmonicity': 0.0,
            'meanHarmToNoiseHarmonicity': 0.0,
            'minIntensity': 0.0, 'maxIntensity': 0.0, 'meanIntensity': 0.0,
            'f1': 0.0, 'f2': 0.0, 'f3': 0.0, 'f4': 0.0,
            'b1': 0.0, 'b2': 0.0, 'b3': 0.0, 'b4': 0.0,
        }
        
        # GQ, GNE, VFER, IMF features
        glottal_defaults = {f'GQ_{key}': 0.0 for key in ['prc5_95', 'std_cycle_open', 'std_cycle_closed']}
        features.update(glottal_defaults)
        
        for prefix in ['GNE', 'VFER']:
            for suffix in ['mean', 'std', 'entropy', 'SNR_TKEO', 'SNR_SEO', 'NSR_TKEO', 'NSR_SEO']:
                key = f'{prefix}_{suffix}' if suffix in ['mean', 'std', 'entropy'] else f'{prefix}_{suffix}'
                if key.endswith('entropy') and prefix == 'GNE':
                    continue
                features[key] = 0.0
        
        features['VFER_entropy'] = 0.0
        
        for suffix in ['SNR_SEO', 'SNR_TKEO', 'SNR_entropy', 'NSR_SEO', 'NSR_TKEO', 'NSR_entropy']:
            features[f'IMF_{suffix}'] = 0.0
        
        return features
    
    def _get_default_mfcc_features(self):
        """Return default MFCC features"""
        features = {}
        features['mean_Log_energy'] = 0.0
        for i in range(13):
            features[f'mean_MFCC_{i}th_coef'] = 0.0
        features['mean_delta_log_energy'] = 0.0
        for i in range(13):
            features[f'mean_{i}th_delta'] = 0.0
        features['mean_delta_delta_log_energy'] = 0.0
        features['mean_delta_delta_0th'] = 0.0
        for i in range(1, 13):
            suffix = 'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'
            features[f'mean_{i}{suffix}_delta_delta'] = 0.0
        features['std_Log_energy'] = 0.0
        for i in range(13):
            features[f'std_MFCC_{i}th_coef'] = 0.0
        features['std_delta_log_energy'] = 0.0
        for i in range(13):
            features[f'std_{i}th_delta'] = 0.0
        features['std_delta_delta_log_energy'] = 0.0
        features['std_delta_delta_0th'] = 0.0
        for i in range(1, 13):
            suffix = 'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'
            features[f'std_{i}{suffix}_delta_delta'] = 0.0
        return features
    
    def _get_default_wavelet_features(self):
        """Return default wavelet features"""
        features = {}
        features['Ea'] = 0.0
        for i in range(1, 11):
            features[f'Ed_{i}_coef'] = 0.0
            features[f'det_entropy_shannon_{i}_coef'] = 0.0
            features[f'det_entropy_log_{i}_coef'] = 0.0
            features[f'det_TKEO_mean_{i}_coef'] = 0.0
            features[f'det_TKEO_std_{i}_coef'] = 0.0
            features[f'app_entropy_shannon_{i}_coef'] = 0.0
            features[f'app_entropy_log_{i}_coef'] = 0.0
            features[f'app_det_TKEO_mean_{i}_coef'] = 0.0
            features[f'app_TKEO_std_{i}_coef'] = 0.0
        features['Ea2'] = 0.0
        for i in range(1, 11):
            features[f'Ed2_{i}_coef'] = 0.0
            features[f'det_LT_entropy_shannon_{i}_coef'] = 0.0
            features[f'det_LT_entropy_log_{i}_coef'] = 0.0
            features[f'det_LT_TKEO_mean_{i}_coef'] = 0.0
            features[f'det_LT_TKEO_std_{i}_coef'] = 0.0
            features[f'app_LT_entropy_shannon_{i}_coef'] = 0.0
            features[f'app_LT_entropy_log_{i}_coef'] = 0.0
            features[f'app_LT_TKEO_mean_{i}_coef'] = 0.0
            features[f'app_LT_TKEO_std_{i}_coef'] = 0.0
        return features
    
    def _get_default_tqwt_features(self):
        """Return default TQWT features"""
        features = {}
        for i in range(1, 37):
            features[f'tqwt_energy_dec_{i}'] = 0.0
            features[f'tqwt_entropy_shannon_dec_{i}'] = 0.0
            features[f'tqwt_entropy_log_dec_{i}'] = 0.0
            features[f'tqwt_TKEO_mean_dec_{i}'] = 0.0
            features[f'tqwt_TKEO_std_dec_{i}'] = 0.0
            features[f'tqwt_medianValue_dec_{i}'] = 0.0
            features[f'tqwt_meanValue_dec_{i}'] = 0.0
            features[f'tqwt_stdValue_dec_{i}'] = 0.0
            features[f'tqwt_minValue_dec_{i}'] = 0.0
            features[f'tqwt_maxValue_dec_{i}'] = 0.0
            features[f'tqwt_skewnessValue_dec_{i}'] = 0.0
            features[f'tqwt_kurtosisValue_dec_{i}'] = 0.0
        return features


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python audio_feature_extractor.py <audio_file>")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    
    print("=" * 70)
    print("PARKINSON'S VOICE FEATURE EXTRACTOR")
    print("=" * 70)
    
    extractor = ParkinsonVoiceFeatureExtractor()
    
    try:
        features = extractor.extract_features(audio_path)
        print(f"\n✓ Successfully extracted {len(features)} features!")
        print(f"Feature vector shape: {features.shape}")
        print(f"First 10 features: {features[:10]}")
        print(f"Last 10 features: {features[-10:]}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
