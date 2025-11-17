# 🚀 Complete Model Training Guide

## Quick Summary

**Dataset Ready**: 80 subjects (56 PD + 24 Non-PD) from NTUA  
**GPU Available**: ✅ NVIDIA RTX 3050 6GB  
**Status**: Ready to train!

---

## 🎯 Step-by-Step Training Instructions

### Step 1: Preprocess DaT Scan Data (10-15 minutes)

```bash
cd /home/hari/Downloads/parkinson/parkinson-app/ml_models

# Activate virtual environment
source ../backend/ml_env/bin/activate

# Run preprocessing (converts images to numpy arrays)
python dat_preprocessing.py \
  --input_dir /home/hari/Downloads/parkinson/ntua-parkinson-dataset \
  --output_dir ./dat_preprocessed_ntua \
  --image_size 128 \
  --max_slices 16

# Expected output:
# - Processed 80 subjects
# - Created train/val/test splits (70/15/15)
# - Saved as .npy files in dat_preprocessed_ntua/
```

**What it does**:
- Loads DaT scans from "PD Patients" and "Non PD Patients" folders
- Resizes to 128x128 pixels
- Normalizes pixel values to [0, 1]
- Pads/trims to exactly 16 slices per subject
- Splits into train (56), validation (12), test (12)
- Saves as numpy arrays for fast loading

---

### Step 2: Train DaT Scan Model (60-90 minutes with GPU)

```bash
# Still in ml_models directory with virtual environment activated
python train_dat_model.py \
  --data_dir ./dat_preprocessed_ntua \
  --output_dir ../models/dat_scan \
  --epochs 100 \
  --batch_size 8 \
  --patience 15

# Monitor training:
# - Watch for "Epoch X/100" progress
# - Check validation AUC each epoch
# - Training stops early if no improvement after 15 epochs
# - Best model saved automatically
```

**Expected Results**:
```
Epoch 1/100: loss: 0.65, acc: 0.65, val_loss: 0.60, val_acc: 0.70, val_auc: 0.72
Epoch 2/100: loss: 0.58, acc: 0.72, val_loss: 0.55, val_acc: 0.75, val_auc: 0.76
...
Epoch 45/100: loss: 0.35, acc: 0.85, val_loss: 0.42, val_acc: 0.80, val_auc: 0.78
Early stopping at epoch 45
Best model: val_auc = 0.78

Test Results:
- Accuracy: 78.5%
- AUC: 0.77
- Sensitivity: 80.0%
- Specificity: 75.0%

Model saved to: models/dat_scan/dat_model_final_20251108_HHMMSS.keras
```

**What it does**:
- Trains CNN+LSTM model (1.8M parameters)
- Uses data augmentation (rotation, shift, zoom)
- Early stopping prevents overfitting
- Generates confusion matrix, ROC curve, PR curve
- Saves best model + evaluation metrics

---

### Step 3: Train Voice Model (10-20 minutes)

```bash
# Still in ml_models directory
python train_speech_model.py

# Expected output:
# - Extracted MFCC features: 144 per audio
# - Trained Random Forest classifier
# - Cross-validation scores
# - Model saved to models/speech/
```

**Note**: Voice model training depends on having audio files in the NTUA dataset. If audio files are not available, the system will continue using baseline estimates (50% probability).

---

### Step 4: Validate Multi-Modal System (5-10 minutes)

```bash
cd /home/hari/Downloads/parkinson/parkinson-app

# Create validation script
python -c "
from backend.app.services.multimodal_service import MultiModalAnalysisService
from pathlib import Path
import numpy as np

print('Testing Multi-Modal Analysis Service...')
service = MultiModalAnalysisService()

print('✅ DaT Service Available:', service.dat_service.is_available())
print('✅ Handwriting Service Available:', service.handwriting_service.spiral_model is not None)
print('✅ Voice Service Available:', service.speech_service.is_available())

print('\nMulti-Modal System Ready! 🎉')
"
```

---

## 📊 Expected Final Performance

### Individual Modalities

| Modality | Status | Accuracy | AUC | Notes |
|----------|--------|----------|-----|-------|
| **DaT Scan** | After Training | 75-80% | 0.75-0.80 | CNN+LSTM on 80 subjects |
| **Handwriting** | ✅ Trained | ~75% | ~0.75 | ResNet50 models already loaded |
| **Voice** | Baseline | 50% | 0.50 | Needs training or uses fallback |

### Multi-Modal Ensemble

| Metric | Expected Value | Calculation |
|--------|----------------|-------------|
| **Accuracy** | **77-82%** | Weighted fusion (50%+25%+25%) |
| **AUC** | **0.78-0.82** | Better than individual |
| **Sensitivity** | **78-85%** | Good at detecting PD |
| **Specificity** | **75-80%** | Good at identifying healthy |

**Confidence Levels**:
- **High (>80%)**: All three modalities agree
- **Moderate (60-80%)**: Two modalities agree
- **Low (<60%)**: Modalities disagree

---

## 🎯 Quick Training Commands (Copy-Paste Ready)

### Option 1: Train Everything from Scratch

```bash
# Open terminal and run:
cd /home/hari/Downloads/parkinson/parkinson-app/ml_models
source ../backend/ml_env/bin/activate

# Step 1: Preprocess (10-15 min)
python dat_preprocessing.py \
  --input_dir /home/hari/Downloads/parkinson/ntua-parkinson-dataset \
  --output_dir ./dat_preprocessed_ntua

# Step 2: Train DaT model (60-90 min)
python train_dat_model.py \
  --data_dir ./dat_preprocessed_ntua \
  --output_dir ../models/dat_scan \
  --epochs 100 \
  --batch_size 8

# Step 3: Train voice model (10-20 min) - if data available
python train_speech_model.py

echo "✅ Training Complete!"
```

**Total Time**: ~1.5-2 hours

### Option 2: Just Train DaT Model (Most Important)

```bash
cd /home/hari/Downloads/parkinson/parkinson-app/ml_models
source ../backend/ml_env/bin/activate

# Preprocess + Train
python dat_preprocessing.py --input_dir /home/hari/Downloads/parkinson/ntua-parkinson-dataset --output_dir ./dat_preprocessed_ntua
python train_dat_model.py --data_dir ./dat_preprocessed_ntua --output_dir ../models/dat_scan --epochs 100

echo "✅ DaT Model Trained!"
```

**Total Time**: ~1.5 hours

---

## 🔍 Monitoring Training Progress

### Watch Training in Real-Time

```bash
# Open another terminal and monitor GPU usage
watch -n 1 nvidia-smi

# Or check TensorBoard logs
tensorboard --logdir models/dat_scan/logs_*
```

### Check if Training is Working

**Good Signs**:
- ✅ GPU utilization 80-100%
- ✅ Loss decreasing each epoch
- ✅ Validation AUC increasing
- ✅ No "Out of Memory" errors

**Bad Signs**:
- ❌ Loss not changing (learning rate issue)
- ❌ Validation AUC worse than training (overfitting)
- ❌ OOM errors (reduce batch_size)

---

## 🐛 Troubleshooting

### GPU Out of Memory
```bash
# Reduce batch size
python train_dat_model.py --batch_size 4  # instead of 8
```

### Training Too Slow
```bash
# Verify GPU is being used
python -c "import tensorflow as tf; print('GPU:', tf.config.list_physical_devices('GPU'))"

# Should show: GPU: [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]
```

### Preprocessing Fails
```bash
# Check dataset path
ls -la /home/hari/Downloads/parkinson/ntua-parkinson-dataset/

# Should show: "PD Patients" and "Non PD Patients" folders
```

### Model Not Saving
```bash
# Check permissions
ls -la /home/hari/Downloads/parkinson/parkinson-app/models/dat_scan/

# Create directory if missing
mkdir -p /home/hari/Downloads/parkinson/parkinson-app/models/dat_scan
```

---

## ✅ After Training - Next Steps

### 1. Restart Backend Server
```bash
# Backend will automatically load the new trained model
# Just restart it:
pkill -f "uvicorn app.main"
cd /home/hari/Downloads/parkinson/parkinson-app/backend
./ml_env/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test the System
- Open: http://localhost:5173/demo/comprehensive
- Upload test data for all three modalities
- Click "Analyze All Modalities"
- Should now see improved DaT predictions!

### 3. Document Results
- Update README.md with actual performance metrics
- Save confusion matrices and ROC curves
- Note training time and parameters used

---

## 📝 Training Checklist

- [ ] Step 1: Preprocess NTUA data (10-15 min)
- [ ] Step 2: Train DaT model (60-90 min)
- [ ] Step 3: Train voice model (optional, 10-20 min)
- [ ] Step 4: Restart backend server
- [ ] Step 5: Test multi-modal analysis
- [ ] Step 6: Document results in README
- [ ] Step 7: Commit and push models (if < 100MB) or document where stored

---

## 🎓 Understanding the Model Architecture

### DaT Scan Model (CNN+LSTM)
```
Input: (16, 128, 128, 1) - 16 brain scan slices
    ↓
4x CNN Blocks (32→64→128→256 filters)
    ↓
Bidirectional LSTM (128→64 units)
    ↓
Dense Layer → Sigmoid
    ↓
Output: Probability of Parkinson's Disease
```

**Why it works**:
- CNN: Extracts spatial features from each slice
- LSTM: Captures temporal patterns across slices
- Bidirectional: Looks at slices both forward and backward

---

**Ready to begin training?** 🚀

Start with Step 1 (preprocessing) and the models will be ready in ~1.5-2 hours!
