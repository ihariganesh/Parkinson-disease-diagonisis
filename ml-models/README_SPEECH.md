# Speech Analysis for Parkinson's Disease Detection

This module implements an advanced speech analysis system for detecting Parkinson's disease using machine learning. The system extracts comprehensive speech features and uses a CNN+LSTM neural network for classification.

## Overview

The speech analysis system consists of:

1. **Feature Extraction Pipeline**: Extracts 754+ features from audio recordings
2. **CNN+LSTM Model**: Deep learning model for classification
3. **API Integration**: REST endpoints for real-time analysis
4. **Frontend Interface**: User-friendly speech recording and analysis interface

## Features Extracted

### Praat-based Features (Voice Quality)
- **Jitter**: Period-to-period variation in vocal fold vibration
  - Absolute jitter, relative jitter, PPQ5, DDP
- **Shimmer**: Amplitude variation between vocal periods
  - Absolute shimmer, relative shimmer, APQ3, APQ5, APQ11, DDA
- **Fundamental Frequency (F0)**: Voice pitch characteristics
  - Mean, std, min, max, median, range
- **Harmonics-to-Noise Ratio (HNR)**: Voice quality measure

### Librosa-based Features (Spectral Analysis)
- **MFCC (0-12)**: Mel-frequency cepstral coefficients with statistics
- **Spectral Features**: Centroid, bandwidth, rolloff
- **Chroma Features**: Harmonic content representation
- **Energy Features**: RMS energy, total energy
- **Zero Crossing Rate**: Speech/silence detection
- **Tempo**: Rhythmic characteristics

### Statistical Features
- **Amplitude Statistics**: Mean, std, min, max, median, skewness, kurtosis
- **Spectral Entropy**: Measure of signal complexity

## Model Architecture

```
Input: 754+ speech features
    ↓
Reshape → (features, 1)
    ↓
CNN Block 1: Conv1D(64) → Conv1D(64) → MaxPool → Dropout(0.25)
    ↓
CNN Block 2: Conv1D(128) → Conv1D(128) → MaxPool → Dropout(0.25)
    ↓
CNN Block 3: Conv1D(256) → Conv1D(256) → MaxPool → Dropout(0.25)
    ↓
LSTM Layer 1: LSTM(128, return_sequences=True) → Dropout(0.3)
    ↓
LSTM Layer 2: LSTM(64) → Dropout(0.3)
    ↓
Dense Layers: Dense(128) → Dense(64) → Dense(32) → Dense(1)
    ↓
Output: Sigmoid activation (Parkinson's probability)
```

## Dataset

- **File**: `pd_speech_features.csv`
- **Samples**: 757 recordings
- **Features**: 754+ comprehensive speech biomarkers
- **Target**: Binary classification (0=Healthy, 1=Parkinson's)
- **Source**: Pre-extracted features from speech recordings

## Installation and Setup

### Quick Setup (Recommended)

```bash
cd ml-models
./setup_speech_analysis.sh
```

### Manual Setup

1. **Install Dependencies**:
```bash
pip install -r requirements_speech.txt
```

2. **Ensure Dataset is Present**:
```bash
# The pd_speech_features.csv file should be in ml-models directory
ls pd_speech_features.csv
```

3. **Train the Model**:
```bash
python train_speech_model.py --csv-path pd_speech_features.csv --epochs 50
```

## Usage

### Training the Model

```python
from speech_model_trainer import SpeechPDModel

# Initialize trainer
model = SpeechPDModel(model_save_dir="models/speech")

# Load and preprocess data
X, y = model.load_data("pd_speech_features.csv")
X_train, X_test, y_train, y_test = model.preprocess_data(X, y)

# Train model
history = model.train_model(X_train, y_train, X_test, y_test, epochs=50)

# Evaluate and save
accuracy, predictions = model.evaluate_model(X_test, y_test)
model.save_model_components()
```

### Feature Extraction from Audio

```python
from speech_feature_extractor import SpeechFeatureExtractor

# Initialize extractor
extractor = SpeechFeatureExtractor()

# Extract features from audio file
features = extractor.extract_all_features("audio_file.wav")

# Convert to DataFrame for model input
features_df = extractor.extract_features_to_dataframe("audio_file.wav")
```

### Making Predictions

```python
from speech_analysis_service import SpeechAnalysisService

# Initialize service
service = SpeechAnalysisService()

# Analyze audio file
result = service.predict("path/to/audio.wav")

# Analyze from bytes (for uploads)
with open("audio.wav", "rb") as f:
    audio_bytes = f.read()
result = service.analyze_audio_from_bytes(audio_bytes, "audio.wav")
```

## API Endpoints

### Analyze Speech Recording
```http
POST /api/v1/analysis/speech/analyze
Content-Type: multipart/form-data

file: <audio_file>
```

**Response**:
```json
{
  "success": true,
  "message": "Speech analysis completed successfully",
  "analysis_result": {
    "prediction_probability": 0.75,
    "predicted_class": 1,
    "class_label": "Parkinson's",
    "confidence": 0.50,
    "risk_level": "High",
    "interpretation": "The speech analysis suggests a high likelihood...",
    "analysis_timestamp": "2025-01-01T12:00:00Z"
  }
}
```

### Check Service Health
```http
GET /api/v1/analysis/speech/health
```

### Batch Analysis
```http
POST /api/v1/analysis/speech/batch-analyze
Content-Type: multipart/form-data

files: <multiple_audio_files>
```

## Frontend Integration

The speech analysis is integrated into the frontend with:

1. **Recording Interface**: Built-in microphone recording with real-time controls
2. **File Upload**: Support for multiple audio formats (WAV, MP3, M4A, FLAC, OGG)
3. **Audio Preview**: Playback controls for recorded/uploaded audio
4. **Analysis Results**: Comprehensive display of prediction results
5. **Navigation**: Integrated into patient dashboard and analysis hub

### Access Points

- **Individual Analysis**: `/speech` - Dedicated speech analysis page
- **Patient Dashboard**: Quick demo access for authenticated users
- **Analysis Hub**: Demo access for non-authenticated users
- **Multimodal Upload**: Integrated into comprehensive analysis flow

## Model Performance

Expected performance metrics:
- **Accuracy**: 85-95% (depends on data quality and model training)
- **Sensitivity**: High detection of Parkinson's cases
- **Specificity**: Low false positive rate for healthy individuals

## Audio Requirements

### Supported Formats
- WAV (recommended)
- MP3
- M4A
- FLAC
- OGG

### Recording Guidelines
- **Duration**: Minimum 10-15 seconds
- **Quality**: Clear audio, minimal background noise
- **Content**: Sustained vowels, reading passages, or natural speech
- **Environment**: Quiet recording environment
- **Microphone**: Good quality microphone recommended

## Technical Details

### Dependencies
- **TensorFlow**: Deep learning framework
- **Librosa**: Audio processing and feature extraction
- **Parselmouth**: Praat wrapper for voice analysis
- **NumPy/Pandas**: Data manipulation
- **Scikit-learn**: Preprocessing and metrics
- **SoundFile**: Audio file I/O

### Model Files
After training, the following files are created:
- `speech_cnn_lstm_model_<timestamp>.h5`: Trained model
- `speech_scaler_<timestamp>.pkl`: Feature scaler
- `speech_label_encoder_<timestamp>.pkl`: Label encoder
- `speech_feature_names_<timestamp>.pkl`: Feature names list

### Performance Considerations
- **Memory**: Requires ~4GB RAM for training
- **Training Time**: 15-30 minutes on modern hardware
- **Inference**: <1 second per audio file
- **File Size**: Models are ~10-50MB

## Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   pip install tensorflow librosa parselmouth soundfile
   ```

2. **Audio Loading Errors**:
   - Ensure audio file is not corrupted
   - Try converting to WAV format
   - Check file permissions

3. **Model Training Fails**:
   - Verify CSV file integrity
   - Ensure sufficient memory (4GB+)
   - Check Python/TensorFlow compatibility

4. **Low Accuracy**:
   - Increase training epochs
   - Verify data quality
   - Check feature extraction pipeline

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Future Enhancements

- [ ] Real-time streaming analysis
- [ ] Additional voice biomarkers
- [ ] Model interpretability (LIME/SHAP)
- [ ] Multi-language support
- [ ] Advanced noise reduction
- [ ] Longitudinal tracking

## References

- Parkinson's Voice Analysis Research
- MFCC Feature Extraction Techniques
- CNN+LSTM Architectures for Sequential Data
- Praat Voice Analysis Software

## License

This speech analysis module is part of the Parkinson's Disease Detection System.