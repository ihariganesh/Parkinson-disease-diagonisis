# 🚀 DaT Scan Module - Quick Start Guide

## 📋 Current Status

✅ **Dataset:** 37 subjects found (15 Healthy, 22 PD)  
✅ **Backend Integration:** API endpoints configured  
⚠️ **Dependencies:** Need to install ML packages  
⚠️ **Preprocessing:** Not done yet  
⚠️ **Model:** Not trained yet  

---

## ⚡ Quick Installation & Training

### Step 1: Install Dependencies (5 minutes)

```bash
cd /home/hari/Downloads/parkinson/parkinson-app
source ml_env/bin/activate

# Install all required packages
pip install tensorflow opencv-python numpy scikit-learn matplotlib seaborn tqdm
```

### Step 2: Train the Model (Automated - 1-3 hours)

```bash
# One command does everything!
./train_dat_model.sh
```

**This script will:**
1. ✅ Preprocess the DAT dataset
2. ✅ Train the CNN+LSTM model
3. ✅ Evaluate on test set
4. ✅ Generate performance plots
5. ✅ Test inference service

**Expected Output:**
```
==========================================
DaT SCAN MODEL TRAINING PIPELINE
==========================================

→ Activating virtual environment...
✓ Data directory found

==========================================
STEP 1: DATA PREPROCESSING
==========================================
Loading Healthy subjects: 100%
Loading PD subjects: 100%
Dataset loaded successfully!
Total subjects: 37
✓ Preprocessing completed successfully!

==========================================
STEP 2: MODEL TRAINING
==========================================
→ Training CNN+LSTM model...
Epoch 1/25: loss=0.6543, acc=0.7200, val_loss=0.5432, val_acc=0.7500
...
Epoch 25/25: loss=0.1234, acc=0.9500, val_loss=0.1567, val_acc=0.9000
✓ Model training completed successfully!

==========================================
STEP 3: MODEL VALIDATION
==========================================
✓ Found trained model
→ Testing inference service...
Prediction: Healthy
Confidence: 0.9234
✓ Inference service working correctly!

==========================================
TRAINING PIPELINE COMPLETE!
==========================================
```

---

## 🧪 Manual Training (Optional)

If you prefer step-by-step control:

```bash
cd /home/hari/Downloads/parkinson/parkinson-app
source ml_env/bin/activate

# Step 1: Preprocess (5-10 minutes)
cd ml_models
python dat_preprocessing.py

# Step 2: Train (1-3 hours)
python train_dat_model.py

# Step 3: Test inference
python dat_inference_service.py \
    ../models/dat_scan/dat_model_best_*.keras \
    /home/hari/Downloads/parkinson/DAT/Healthy/001
```

---

## 🔍 Verify Installation

Check system status anytime:

```bash
python check_dat_module.py
```

**Expected output after setup:**
```
Summary: 5/5 checks passed
Status: 🟢 READY FOR PRODUCTION
```

---

## 🌐 Using the API

### Start Backend

```bash
cd /home/hari/Downloads/parkinson/parkinson-app/backend
source ../ml_env/bin/activate
uvicorn app.main:app --reload
```

### Test Service Status

```bash
curl http://localhost:8000/api/v1/analysis/dat/status
```

**Response:**
```json
{
  "service_name": "DaT Scan Analysis",
  "version": "1.0.0",
  "available": true,
  "model_loaded": true,
  "model_path": "/path/to/dat_model_best_20251020.keras"
}
```

### Analyze DaT Scan

```bash
# Get authentication token first
TOKEN="your_jwt_token_here"

# Upload scan slices
curl -X POST "http://localhost:8000/api/v1/analysis/dat/analyze" \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@/path/to/scan/001.png" \
  -F "files=@/path/to/scan/002.png" \
  -F "files=@/path/to/scan/003.png" \
  -F "files=@/path/to/scan/004.png" \
  -F "files=@/path/to/scan/005.png" \
  -F "files=@/path/to/scan/006.png" \
  -F "files=@/path/to/scan/007.png" \
  -F "files=@/path/to/scan/008.png" \
  -F "files=@/path/to/scan/009.png" \
  -F "files=@/path/to/scan/010.png" \
  -F "files=@/path/to/scan/011.png" \
  -F "files=@/path/to/scan/012.png" \
  -F "files=@/path/to/scan/013.png" \
  -F "files=@/path/to/scan/014.png" \
  -F "files=@/path/to/scan/015.png" \
  -F "files=@/path/to/scan/016.png"
```

**Response:**
```json
{
  "success": true,
  "prediction": "Parkinson",
  "confidence": 0.8765,
  "probability_healthy": 0.1235,
  "probability_parkinson": 0.8765,
  "risk_level": "High",
  "interpretation": "Scan shows significant dopamine transporter deficit with high confidence. Strong indication of Parkinson's disease.",
  "recommendations": [
    "⚠️ Consult a neurologist for comprehensive clinical evaluation",
    "📋 Complete neurological examination recommended",
    "🔬 Consider additional diagnostic tests (UPDRS, MDS-UPDRS)",
    "💊 Discuss treatment options with movement disorder specialist",
    "🏥 Early intervention may improve long-term outcomes"
  ]
}
```

---

## 📊 Model Performance

After training, check results in:

```bash
cd models/dat_scan/

# View training plots
open training_history_*.png
open confusion_matrix_*.png
open roc_curve_*.png

# Read evaluation metrics
cat evaluation_results_*.json
```

**Expected Metrics:**
- **Accuracy:** 85-95%
- **Precision:** 80-90%
- **Recall:** 80-90%
- **AUC:** 0.90-0.95

---

## 🗂️ File Structure

```
parkinson-app/
├── ml_models/
│   ├── dat_preprocessing.py          # ← Data preprocessing
│   ├── dat_cnn_lstm_model.py         # ← Model architecture
│   ├── train_dat_model.py            # ← Training script
│   ├── dat_inference_service.py      # ← Inference service
│   └── dat_preprocessed/             # ← Generated after preprocessing
│       ├── train_X.npy (70% data)
│       ├── val_X.npy (20% data)
│       ├── test_X.npy (10% data)
│       └── metadata.json
├── models/
│   └── dat_scan/                     # ← Generated after training
│       ├── dat_model_best_*.keras    # ← Best model (use this)
│       ├── dat_model_final_*.keras   # ← Final model
│       ├── training_history_*.png    # ← Training plots
│       ├── confusion_matrix_*.png    # ← Performance visualization
│       ├── roc_curve_*.png          # ← ROC curve
│       └── evaluation_results_*.json # ← Metrics
├── backend/
│   └── app/
│       ├── api/v1/endpoints/
│       │   └── analysis.py           # ← API endpoints
│       └── services/
│           └── dat_analysis_service.py # ← Backend service
├── train_dat_model.sh                # ← Automated training pipeline
├── check_dat_module.py               # ← System check script
├── DAT_SCAN_README.md                # ← Full documentation
└── DAT_IMPLEMENTATION_SUMMARY.md     # ← Implementation details
```

---

## 🔧 Troubleshooting

### Out of Memory Error
```bash
# Edit ml_models/train_dat_model.py
# Line ~305, change:
BATCH_SIZE = 4  # or even 2 for 4GB GPU
```

### Model Not Training Well
```bash
# Increase epochs
EPOCHS = 50

# Or adjust learning rate
LEARNING_RATE = 0.0005
```

### Service Not Loading Model
```bash
# Check model exists
ls -lh models/dat_scan/

# Manually specify model path in backend
# Edit backend/app/services/dat_analysis_service.py
# Line ~27, add:
self.model_path = "/full/path/to/dat_model_best_20251020.keras"
```

---

## 📚 Documentation

- **Full Documentation:** `DAT_SCAN_README.md`
- **Implementation Details:** `DAT_IMPLEMENTATION_SUMMARY.md`
- **API Reference:** See DAT_SCAN_README.md → API Usage section

---

## ✅ Checklist

- [ ] Dependencies installed (`pip install ...`)
- [ ] Data preprocessed (`python dat_preprocessing.py`)
- [ ] Model trained (`python train_dat_model.py`)
- [ ] Inference tested (`python dat_inference_service.py ...`)
- [ ] Backend started (`uvicorn app.main:app --reload`)
- [ ] API tested (`curl .../dat/status`)

---

## 🎯 Next Steps After Training

1. **Review Performance:**
   - Check training plots
   - Review confusion matrix
   - Analyze ROC curve
   - Read evaluation metrics

2. **Test Inference:**
   ```bash
   python check_dat_module.py
   ```

3. **Start Backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

4. **Test API:**
   ```bash
   curl http://localhost:8000/api/v1/analysis/dat/status
   ```

5. **Frontend Integration** (Future):
   - Create DaTAnalysis.tsx component
   - Add multi-file upload UI
   - Display predictions and recommendations

---

## 💡 Tips

- **Training Time:** ~1-3 hours on RTX 3050 GPU
- **GPU Usage:** Monitor with `nvidia-smi` during training
- **Checkpoints:** Best model saved automatically during training
- **TensorBoard:** View training in real-time:
  ```bash
  tensorboard --logdir=models/dat_scan/logs_*
  ```

---

## 🚀 Ready to Start?

```bash
# Install dependencies
pip install tensorflow opencv-python numpy scikit-learn matplotlib seaborn tqdm

# Run automated training
./train_dat_model.sh

# Check status
python check_dat_module.py

# Start backend
cd backend && uvicorn app.main:app --reload
```

**That's it! Your DaT scan analysis module will be ready to use!** 🎉

---

**Last Updated:** October 20, 2025  
**Status:** Ready for Training  
**Estimated Time:** 3-4 hours total
