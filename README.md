# Parkinson's Disease Multi-Modal Diagnosis System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![CI](https://github.com/ihariganesh/Parkinson-disease-diagonisis/actions/workflows/ci.yml/badge.svg)](https://github.com/ihariganesh/Parkinson-disease-diagonisis/actions/workflows/ci.yml)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](#-contributing)

A comprehensive AI-powered clinical decision support system for Parkinson's disease diagnosis using multi-modal analysis combining DaT scans, handwriting patterns, and voice biomarkers.

![Multi-Modal Analysis](https://img.shields.io/badge/Modalities-3-orange) ![Accuracy Target](https://img.shields.io/badge/Target_Accuracy-85%25-success)

---

## 🌟 Features

### Multi-Modal Analysis
- **🧠 DaT Scan Analysis** (50% weight) - Deep learning analysis of dopamine transporter scans
- **✍️ Handwriting Analysis** (25% weight) - CNN-based detection of motor control abnormalities
- **🎤 Voice Analysis** (25% weight) - MFCC-based speech pattern recognition

### Key Capabilities
- ✅ **Weighted Ensemble Fusion** - Intelligent combination of multiple diagnostic modalities
- ✅ **Confidence-Aware Predictions** - High/Moderate/Low confidence levels based on agreement
- ✅ **Clinical Interpretation** - Auto-generated explanations for healthcare professionals
- ✅ **Context-Aware Recommendations** - Personalized next steps based on results
- ✅ **Professional Medical Interface** - Clinical-grade UI with proper disclaimers
- ✅ **Real-Time Analysis** - Fast inference with GPU acceleration support

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + TypeScript)             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Comprehensive Analysis Interface                      │ │
│  │  • DaT Scan Upload (12-16 images)                     │ │
│  │  • Handwriting Upload (spiral + wave)                 │ │
│  │  • Voice Recording Upload                             │ │
│  │  • Real-time Results Display                          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI + Python)                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Multi-Modal Fusion Service                           │ │
│  │  • DaT CNN+LSTM Model (50% weight)                    │ │
│  │  • Handwriting CNN Model (25% weight)                 │ │
│  │  • Voice MFCC+ML Model (25% weight)                   │ │
│  │  • Weighted Ensemble → Final Diagnosis                │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              ML MODELS (TensorFlow + scikit-learn)           │
│  • Custom CNN+LSTM for DaT scans                            │
│  • CNN for handwriting analysis                             │
│  • MFCC+SVM/RF for voice analysis                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Dataset Setup](#-dataset-setup)
- [Training Models](#-training-models)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Performance](#-performance)
- [Clinical Validation](#-clinical-validation)
- [Contributing](#-contributing)
- [License](#-license)
- [Disclaimers](#%EF%B8%8F-disclaimers)

---

## 🚀 Installation

### Prerequisites

- Python 3.13+
- Node.js 18+
- PostgreSQL 14+
- NVIDIA GPU (optional, for faster training)
- CUDA 11.8+ (if using GPU)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/parkinson-diagnosis.git
cd parkinson-diagnosis

# Create virtual environment
python3 -m venv ml_env
source ml_env/bin/activate  # On Windows: ml_env\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Set up database
cd backend
# Create PostgreSQL database named 'parkinson_db'
# Update .env file with database credentials

# Run migrations
python -c "from app.db.database import init_db; init_db()"
```

### Frontend Setup

```bash
# Install Node dependencies
cd frontend
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env
```

---

## 🎯 Quick Start

### 1. Start Backend Server

```bash
cd backend
source ../ml_env/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`  
API Documentation: `http://localhost:8000/docs`

### 2. Start Frontend Server

```bash
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### 3. Access the Application

- **Patient Dashboard**: `http://localhost:5173/patient/dashboard`
- **Comprehensive Analysis**: `http://localhost:5173/comprehensive`
- **Demo Mode**: `http://localhost:5173/demo/comprehensive` (no login required)

---

## 📊 Dataset Setup

### Option 1: Use NTUA Dataset (Recommended)

The system is designed to work with the [NTUA Parkinson Dataset](https://github.com/ails-lab/ntua-parkinson-dataset):

```bash
# Clone NTUA dataset
git clone https://github.com/ails-lab/ntua-parkinson-dataset.git

# Preprocess DaT scans
cd ml_models
python dat_preprocessing.py --input ../ntua-parkinson-dataset/DaT --output dat_preprocessed_ntua
```

**NTUA Dataset Contents:**
- 66 subjects (46 PD + 20 Healthy)
- DaT scans (12-16 slices per subject)
- Clinical metadata (UPDRS scores, medications, etc.)

### Option 2: Use Your Own Data

Organize your data in the following structure:

```
data/
├── DaT/
│   ├── Healthy/
│   │   ├── subject_001/
│   │   │   ├── scan_001.png
│   │   │   ├── scan_002.png
│   │   │   └── ...
│   │   └── ...
│   └── PD/
│       └── ...
├── Handwriting/
│   ├── Healthy/
│   └── PD/
└── Voice/
    ├── Healthy/
    └── PD/
```

---

## 🎓 Training Models

### 1. Train DaT Scan Model

```bash
cd ml_models

# Preprocess data (if not done)
python dat_preprocessing.py

# Train model
python train_dat_model.py

# Expected output:
# - Training time: 30-60 minutes (with GPU)
# - Target AUC: 0.75-0.80
# - Model saved to: models/dat_scan/dat_model_final_YYYYMMDD_HHMMSS.keras
```

**Model Architecture:**
- Custom CNN (4 blocks: 32→64→128→256 filters)
- Bidirectional LSTM (128→64 units)
- 1.8M trainable parameters
- Input: (16, 128, 128, 1) - 16 slices of 128×128 grayscale images

### 2. Train Handwriting Model

```bash
# Train handwriting analysis model
python train_handwriting_model.py
```

### 3. Train Voice Model

```bash
# Train voice analysis model
python train_speech_model.py
```

---

## 💻 Usage

### Web Interface

1. **Register/Login**: Create an account or use demo mode
2. **Navigate to Comprehensive Analysis**: Click "Comprehensive" in menu
3. **Upload Data**:
   - DaT Scans: 12-16 brain scan images (PNG/JPG)
   - Handwriting: Spiral and wave drawings
   - Voice: Audio recording (WAV/MP3)
4. **Analyze**: Click "Analyze All Modalities"
5. **View Results**: See diagnosis, confidence, and recommendations

### API Usage

```python
import requests

# Upload files for analysis
files = {
    'dat_scans': [
        ('dat_scans', open('scan1.png', 'rb')),
        ('dat_scans', open('scan2.png', 'rb')),
        # ... up to 16 scans
    ],
    'handwriting_spiral': open('spiral.png', 'rb'),
    'handwriting_wave': open('wave.png', 'rb'),
    'voice_recording': open('voice.wav', 'rb')
}

response = requests.post(
    'http://localhost:8000/api/v1/analysis/multimodal/comprehensive',
    files=files,
    headers={'Authorization': f'Bearer {token}'}
)

result = response.json()
print(f"Diagnosis: {result['fusion_results']['final_diagnosis']}")
print(f"Confidence: {result['fusion_results']['confidence']}")
```

---

## 📚 API Documentation

### Endpoints

#### Multi-Modal Analysis

**POST** `/api/v1/analysis/multimodal/comprehensive`

Comprehensive multi-modal analysis combining all three modalities.

**Request:**
- `dat_scans`: List[File] - DaT scan images (12-16 images)
- `handwriting_spiral`: File (optional) - Spiral drawing
- `handwriting_wave`: File (optional) - Wave drawing
- `voice_recording`: File (optional) - Voice audio file
- `patient_id`: string (optional) - Patient identifier

**Response:**
```json
{
  "diagnosis": "Parkinson's Disease" | "Healthy",
  "confidence": 0.87,
  "final_probability": 0.82,
  "confidence_level": "High",
  "agreement_score": 0.95,
  "modality_results": {
    "dat": {
      "probability": 0.85,
      "confidence": 0.90,
      "prediction": "Parkinson's"
    },
    "handwriting": {
      "probability": 0.78,
      "confidence": 0.85,
      "prediction": "Parkinson's"
    },
    "voice": {
      "probability": 0.83,
      "confidence": 0.82,
      "prediction": "Parkinson's"
    }
  },
  "clinical_interpretation": "...",
  "recommendations": ["...", "..."]
}
```

#### Individual Modality Endpoints

- **POST** `/api/v1/analysis/dat/analyze` - DaT scan only
- **POST** `/api/v1/analysis/handwriting/analyze` - Handwriting only
- **POST** `/api/v1/analysis/speech/analyze` - Voice only

---

## 🤝 Contributing

We welcome contributions from developers, researchers, and healthcare professionals.

- See `CONTRIBUTING.md` for setup, branching, and testing guidelines.
- Use the issue templates for bug reports and feature requests.
- Follow `CODE_OF_CONDUCT.md` and review `SECURITY.md` for reporting vulnerabilities.

## ⚙️ Configuration

### Environment Variables

Create `.env` files in backend and frontend directories:

**Backend (.env):**
```env
DATABASE_URL=postgresql://user:password@localhost/parkinson_db
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Frontend (.env):**
```env
VITE_API_URL=http://localhost:8000
```

### Model Weights

Configure modality weights in `backend/app/services/multimodal_service.py`:

```python
self.weights = {
    'dat': 0.50,          # 50% - Most reliable
    'handwriting': 0.25,  # 25% - Motor symptoms
    'voice': 0.25         # 25% - Speech characteristics
}
```

---

## 📈 Performance

### Current Performance (with NTUA Dataset)

| Metric | DaT Model | Handwriting | Voice | Multi-Modal |
|--------|-----------|-------------|-------|-------------|
| **Dataset Size** | 66 subjects | TBD | TBD | 66 subjects |
| **Accuracy** | TBD | TBD | TBD | **Target: 75-80%** |
| **AUC** | **Target: 0.75-0.80** | TBD | TBD | **Target: 0.80+** |
| **Sensitivity** | TBD | TBD | TBD | **Target: >75%** |
| **Specificity** | TBD | TBD | TBD | **Target: >75%** |

### Clinical-Grade Target (Future)

| Metric | Target |
|--------|--------|
| **Dataset Size** | 200-500+ subjects per modality |
| **Accuracy** | >85% |
| **Sensitivity** | >85% (correctly detect PD) |
| **Specificity** | >85% (correctly identify healthy) |
| **AUC** | >0.85 |

---

## 🏥 Clinical Validation

### Validation Status

⚠️ **Current Status**: Research prototype, not clinically validated

### Appropriate Use

✅ **DO USE FOR:**
- Research and educational purposes
- Supplementary screening tool
- Clinical decision support (with physician review)
- Risk assessment and early detection

❌ **DO NOT USE FOR:**
- Primary clinical diagnosis
- Treatment decisions without physician confirmation
- Patient care without neurologist evaluation
- Regulatory-approved medical device claims

### Validation Roadmap

1. ✅ Technical validation on training/test sets
2. ⏳ External validation on independent datasets
3. ⏳ Multi-center clinical validation study
4. ⏳ Comparison with expert neurologist diagnoses
5. ⏳ Regulatory approval process (FDA/CE marking)

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/parkinson-diagnosis.git

# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes and commit
git add .
git commit -m "Add your feature"

# Push and create pull request
git push origin feature/your-feature-name
```

### Areas for Contribution

- 🎯 Model improvements and optimization
- 📊 Additional datasets and preprocessing scripts
- 🎨 UI/UX enhancements
- 📝 Documentation improvements
- 🧪 Testing and validation
- 🌍 Internationalization

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimers

### Medical Disclaimer

**THIS SOFTWARE IS FOR RESEARCH AND EDUCATIONAL PURPOSES ONLY.**

- 🔴 **NOT A MEDICAL DEVICE**: This system is not FDA-approved or CE-marked as a medical diagnostic device
- 🔴 **NOT FOR CLINICAL DIAGNOSIS**: Do not use as the sole basis for diagnosis or treatment decisions
- 🔴 **REQUIRES PHYSICIAN REVIEW**: Always consult with a qualified neurologist for proper clinical diagnosis
- 🔴 **NO WARRANTY**: Provided "as is" without warranty of any kind

### Limitations

1. **Dataset Size**: Current models trained on limited datasets (66 subjects)
2. **Generalization**: May not generalize to all populations and demographics
3. **Scanner Variability**: Trained on specific scanner types and imaging protocols
4. **Clinical Context**: Does not replace comprehensive neurological examination

### Proper Use

This system should be used as:
- A **screening tool** to identify individuals who may benefit from further evaluation
- A **research tool** to study Parkinson's disease biomarkers
- A **clinical decision support aid** to complement physician expertise

**Always seek advice from a qualified healthcare professional for proper diagnosis and treatment.**

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/parkinson-diagnosis/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/parkinson-diagnosis/discussions)

---

## 🙏 Acknowledgments

- **NTUA Dataset**: [ails-lab/ntua-parkinson-dataset](https://github.com/ails-lab/ntua-parkinson-dataset)
- **TensorFlow/Keras**: Deep learning framework
- **FastAPI**: Modern web framework for Python
- **React**: Frontend framework
- **All Contributors**: Thank you for your contributions!

---

## 📚 Documentation

For detailed documentation, see:

- [MULTIMODAL_SYSTEM_DESIGN.md](MULTIMODAL_SYSTEM_DESIGN.md) - System architecture and design
- [DAT_CLASSIFICATION_EXPLAINED.md](DAT_CLASSIFICATION_EXPLAINED.md) - DaT scan analysis details
- [DAT_DATA_EXPLANATION.md](DAT_DATA_EXPLANATION.md) - Dataset structure and preprocessing
- [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md) - Current development status

---

## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ Multi-modal analysis system
- ✅ DaT scan CNN+LSTM model
- ✅ Handwriting CNN model
- ✅ Voice MFCC analysis
- ✅ Web interface
- ✅ REST API

### Version 2.0 (Planned)
- ⏳ Improved models with larger datasets
- ⏳ Temporal tracking (progression monitoring)
- ⏳ Risk stratification (early/moderate/late stage)
- ⏳ Treatment response prediction
- ⏳ Mobile app

### Version 3.0 (Future)
- ⏳ Clinical validation studies
- ⏳ Regulatory approval
- ⏳ EHR integration
- ⏳ Real-time monitoring
- ⏳ Personalized interventions

---

<p align="center">
  <strong>Built with ❤️ for advancing Parkinson's disease research and early detection</strong>
</p>

<p align="center">
  <sub>If this project helps your research, please consider citing our work and giving it a ⭐</sub>
</p>
