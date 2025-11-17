# 🎤 Speech Model Training & Analysis - Complete Explanation

**Question**: Does the speech model use `pd_speech_features.csv` for training and analyze voices by extracting features?

**Short Answer**: 
- ✅ **YES** - Used for training
- ❌ **NO** - Not currently used for analyzing new voices (using mock features instead)

---

## 📊 The CSV File: `pd_speech_features.csv`

### File Details
```
Location: /home/hari/Downloads/parkinson/pd_speech_features.csv
Size: 5.1 MB
Rows: 757 (756 data + 1 header)
Columns: 755 (754 features + 1 label)
Created: October 24, 2019
```

### What's Inside
This CSV contains **pre-extracted speech features** from real patient voice recordings:

```
id, gender, PPE, DFA, RPDE, numPulses, numPeriodsPulses, 
meanPeriodPulses, stdDevPeriodPulses, locPctJitter, locAbsJitter,
rapJitter, ppq5Jitter, ddpJitter, locShimmer, locDbShimmer,
apq3Shimmer, apq5Shimmer, apq11Shimmer, ddaShimmer, ...
[... 754 features total ...], class
```

**Last Column**: `class` (0 = Healthy, 1 = Parkinson's)

---

## 🔄 Two Different Processes

### 1️⃣ **TRAINING** (What Already Happened - Nov 8, 2025)

**Used**: ✅ `pd_speech_features.csv`

```python
# Training Script: ml-models/train_speech_model.py
# Trainer: ml-models/speech_model_trainer.py

STEP 1: Load CSV File
├── Read: pd_speech_features.csv (756 samples, 754 features)
├── Separate: X (features), y (labels)
├── Class distribution:
│   ├── Parkinson's: 564 samples (74.6%)
│   └── Healthy: 192 samples (25.4%)
└── Store feature names for later

STEP 2: Preprocess Data
├── Handle missing values (NaN → 0.0)
├── Encode labels (Healthy=0, Parkinson's=1)
├── Split: 80% training (604), 20% testing (152)
├── Scale features using StandardScaler
└── Ready for training!

STEP 3: Create Model
├── Architecture: CNN (3 blocks) + Bidirectional LSTM
├── Input: (754,) features
├── Output: Probability [0.0-1.0]
└── Total params: ~1.2M

STEP 4: Train Model
├── Epochs: 100 (with early stopping)
├── Batch size: 32
├── Optimizer: Adam
├── Loss: Binary crossentropy
└── Time: ~2 minutes (GPU)

STEP 5: Evaluate & Save
├── Test Accuracy: 74.3%
├── Save model: speech_cnn_lstm_model_20251108_230051.h5 (7.5 MB)
├── Save scaler: speech_scaler_20251108_230051.pkl (18 KB)
├── Save encoder: speech_label_encoder_20251108_230051.pkl (258 B)
└── Save features: speech_feature_names_20251108_230051.pkl (17 KB)

RESULT: ✅ Trained model ready to use!
```

---

### 2️⃣ **ANALYSIS** (What Should Happen vs. What Actually Happens)

#### 🎯 **What SHOULD Happen** (Ideal Flow)

**Should Use**: The SAME 754 features extraction process

```python
# IDEAL PROCESS (Not yet implemented)

USER UPLOADS: voice_recording.wav
    ↓
STEP 1: Load Audio File
├── Load with librosa: y, sr = librosa.load(audio_path)
├── Duration: 5-10 seconds
├── Sample rate: 22050 Hz
└── Raw audio waveform

STEP 2: Extract 754 Features (Match CSV exactly!)
├── id, gender (metadata)
├── PPE, DFA, RPDE (voice quality measures)
├── numPulses, numPeriodsPulses (pitch analysis)
├── Jitter features (10+ variants)
│   └── locPctJitter, locAbsJitter, rapJitter, ppq5Jitter, etc.
├── Shimmer features (10+ variants)
│   └── locShimmer, locDbShimmer, apq3Shimmer, apq5Shimmer, etc.
├── Pitch & Formants (F0, F1-F4)
├── MFCCs (100+ coefficients with mean/std/delta)
├── Harmonic features (HNR, NHR)
├── Wavelet features (TQWT)
├── Energy & Entropy metrics
└── ... all 754 features

STEP 3: Create Feature Vector
├── Arrange in exact same order as training CSV
├── Result: numpy array [f1, f2, f3, ..., f754]
└── Shape: (754,)

STEP 4: Normalize & Predict
├── Apply StandardScaler (from training)
├── Feed to CNN+LSTM model
├── Get prediction probability
└── Return: "Parkinson's" or "Healthy"

RESULT: ✅ Accurate prediction based on voice features!
```

---

#### ⚠️ **What ACTUALLY Happens** (Current Implementation)

**Actually Uses**: ❌ Mock random features (NOT from CSV!)

```python
# CURRENT PROCESS (speech_service.py)

USER UPLOADS: voice_recording.wav
    ↓
STEP 1: Receive Audio File
├── Backend receives the file
├── Stores temporarily
└── Ready to analyze

STEP 2: Generate FAKE Features 🎲
├── Hash filename: hash("voice_recording.wav") = 123456789
├── Use as random seed: np.random.seed(123456789)
├── Generate random features: np.random.randn(754) * 0.5
├── Result: [0.23, -0.51, 0.82, ..., 0.15]  ← RANDOM NUMBERS!
└── Shape: (754,) ✅ Correct, but meaningless!

STEP 3: Normalize & Predict
├── Apply StandardScaler (from training) ✅
├── Feed to CNN+LSTM model ✅
├── Get prediction probability ✅
└── Return: "Parkinson's" or "Healthy" ✅

RESULT: ⚠️ Prediction is FAKE (based on random numbers, not audio!)
```

---

## 🤔 Why The Gap?

### Problem: Feature Extraction is Complex!

The CSV file contains **pre-extracted features** that were processed offline by researchers using specialized tools. To replicate this for new audio files, we would need to:

**Complex Feature Extraction Pipeline:**
```python
# This is what we NEED but don't have yet:

def extract_754_features(audio_path: str) -> np.ndarray:
    """
    Extract all 754 features from audio file
    Must match pd_speech_features.csv exactly!
    """
    
    # Load audio
    y, sr = librosa.load(audio_path, sr=22050)
    
    # 1. Basic vocal quality (10+ features)
    features['PPE'] = calculate_pitch_period_entropy(y, sr)
    features['DFA'] = calculate_detrended_fluctuation(y, sr)
    features['RPDE'] = calculate_recurrence_period_density(y, sr)
    
    # 2. Jitter analysis (12+ features)
    features['locPctJitter'] = calculate_local_jitter_pct(y, sr)
    features['locAbsJitter'] = calculate_local_jitter_abs(y, sr)
    features['rapJitter'] = calculate_rap_jitter(y, sr)
    # ... 9 more jitter variants
    
    # 3. Shimmer analysis (12+ features)
    features['locShimmer'] = calculate_local_shimmer(y, sr)
    features['locDbShimmer'] = calculate_db_shimmer(y, sr)
    # ... 10 more shimmer variants
    
    # 4. MFCCs (100+ features)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    for i in range(13):
        features[f'mfcc_{i}_mean'] = np.mean(mfccs[i])
        features[f'mfcc_{i}_std'] = np.std(mfccs[i])
        features[f'mfcc_{i}_delta'] = calculate_delta(mfccs[i])
        # etc.
    
    # 5. Pitch & Formants (20+ features)
    pitch = librosa.yin(y, fmin=80, fmax=400, sr=sr)
    formants = calculate_formants(y, sr)  # F1, F2, F3, F4
    
    # 6. Harmonic analysis (10+ features)
    hnr = calculate_harmonics_to_noise_ratio(y, sr)
    
    # 7. Wavelet features (50+ features)
    wavelet_coeffs = calculate_tqwt_features(y)
    
    # 8. Energy & Entropy (20+ features)
    energy = calculate_energy_features(y)
    entropy = calculate_spectral_entropy(y, sr)
    
    # ... and many more!
    
    # Combine all features in exact order
    feature_vector = np.array([
        features['id'],
        features['gender'],
        features['PPE'],
        features['DFA'],
        # ... all 754 features in CSV column order
    ])
    
    return feature_vector  # Shape: (754,)
```

**Challenges:**
1. **754 features** - That's a LOT of features to extract!
2. **Exact order** - Must match CSV column order exactly
3. **Complex algorithms** - Some features require specialized tools:
   - `parselmouth` (Praat) for voice analysis
   - `librosa` for audio processing
   - Custom algorithms for RPDE, DFA, etc.
4. **System hanging** - Some features (like librosa.util.smooth) cause freezing
5. **Performance** - Must extract in < 2 seconds for good UX

---

## 📋 Feature Breakdown

### What's in the 754 Features?

Based on the CSV column names, here's what the model expects:

| Category | Count | Examples |
|----------|-------|----------|
| **Metadata** | ~10 | id, gender |
| **Pitch Period Features** | ~50 | numPulses, numPeriodsPulses, meanPeriodPulses |
| **Jitter Features** | ~12 | locPctJitter, rapJitter, ppq5Jitter, ddpJitter |
| **Shimmer Features** | ~12 | locShimmer, apq3Shimmer, apq5Shimmer, ddaShimmer |
| **Voice Quality** | ~20 | PPE, DFA, RPDE, HNR, NHR |
| **MFCCs** | ~100 | mfcc_0_mean, mfcc_1_std, mfcc_2_delta, etc. |
| **Formants** | ~20 | F1, F2, F3, F4 (with variants) |
| **Wavelet Features** | ~50 | TQWT decomposition coefficients |
| **Energy & Entropy** | ~20 | RMS energy, spectral entropy |
| **Other** | ~460 | Various acoustic and prosodic features |
| **TOTAL** | **754** | |

---

## 🎯 Current Status Summary

### Training ✅ COMPLETE
```
✅ Used: pd_speech_features.csv (754 features, 756 samples)
✅ Model: CNN+LSTM trained successfully
✅ Accuracy: 74.3%
✅ Saved: All model files (7.5 MB)
✅ Status: Ready to make predictions!
```

### Analysis ⚠️ PARTIAL
```
❌ Not Using: pd_speech_features.csv
❌ Not Extracting: Real audio features
⚠️ Using: Random mock features (754 fake numbers)
✅ Model Works: Trained model runs correctly
⚠️ Predictions: Fake (based on random input)
```

---

## 🔮 What Needs to Happen

### Option 1: Implement Feature Extraction (Ideal) 🎯

**Task**: Create a feature extractor that produces the exact 754 features

```python
# Create: backend/app/services/audio_feature_extractor.py

class AudioFeatureExtractor:
    """Extract 754 speech features matching pd_speech_features.csv"""
    
    def extract_features(self, audio_path: str) -> np.ndarray:
        """
        Extract all 754 features from audio file
        
        Returns:
            numpy array of shape (754,) with features in exact order
        """
        # Load audio
        # Extract each feature category
        # Combine in correct order
        # Return feature vector
        pass
```

**Pros**:
- ✅ Accurate predictions based on real audio
- ✅ Matches training data exactly
- ✅ Clinically useful

**Cons**:
- ❌ Complex to implement (100+ hours)
- ❌ Requires specialized libraries
- ❌ May have performance issues

---

### Option 2: Simplified Feature Set (Pragmatic) 🎯

**Task**: Extract a subset of most important features

```python
# Extract only the most discriminative features (maybe 50-100)
# Re-train model on reduced feature set
# Much easier to implement
```

**Pros**:
- ✅ Faster to implement (10-20 hours)
- ✅ Simpler code
- ✅ May still give good accuracy

**Cons**:
- ⚠️ Need to re-train model
- ⚠️ Lower accuracy (maybe 65-70%)
- ⚠️ Need to identify which features are most important

---

### Option 3: Pre-compute Features Offline (Workaround) 🎯

**Task**: Extract features offline, store in database

```python
# For each patient:
# 1. Record voice → save as WAV
# 2. Extract features offline (using Python script)
# 3. Store features in database
# 4. At prediction time, load pre-computed features
```

**Pros**:
- ✅ Easy to implement (2-5 hours)
- ✅ No real-time extraction needed
- ✅ Can use existing tools

**Cons**:
- ❌ Not real-time
- ❌ Requires offline processing step
- ❌ Less convenient for users

---

## 💡 Bottom Line

### Current Situation:

```
Training: ✅ Used pd_speech_features.csv correctly
          ✅ Model learned from 754 real features
          ✅ 74.3% accuracy achieved

Analysis: ⚠️ NOT using pd_speech_features.csv
          ❌ NOT extracting real features from audio
          🎲 Using random mock features (754 fake numbers)
          ⚠️ Predictions are meaningless for diagnosis
```

### The Model is Like:

```
🎓 TRAINED DOCTOR (Model):
   - Studied 756 patient cases
   - Learned patterns from 754 features
   - 74.3% diagnostic accuracy
   - Ready to diagnose!

👂 LISTENING (Feature Extraction):
   - Should analyze voice recording
   - Should extract 754 features
   - ❌ Currently just guessing random numbers!
   - Result: Doctor gets random data, not real symptoms!
```

### What You Need:

To make the system work properly, you need to implement feature extraction that:
1. Takes an audio file (WAV/MP3)
2. Extracts the **same 754 features** as in `pd_speech_features.csv`
3. In the **exact same order** as the CSV columns
4. Feeds these **real features** to the trained model
5. Gets an **accurate prediction**

**Right now**: The model is perfect, but we're feeding it random noise instead of real data! 🎲❌

---

**Created**: November 12, 2025  
**Status**: Training ✅ | Analysis ⚠️  
**Next Step**: Implement real feature extraction

🎤🔬✨
