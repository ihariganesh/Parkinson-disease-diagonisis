# Model Files - Download Instructions

The trained model files are **not included in this repository** due to GitHub's file size limits (some models exceed 100 MB).

## 📦 Required Model Files

### Backend Models (Handwriting Analysis)
Located in: `backend/models/`

- `resnet50_spiral_best.h5` (93.49 MB) - ResNet50 model for spiral drawing analysis
- `resnet50_spiral_final.h5` (161.64 MB) - Final ResNet50 spiral model
- `resnet50_wave_best.h5` (93.49 MB) - ResNet50 model for wave drawing analysis
- `resnet50_wave_final.h5` (161.64 MB) - Final ResNet50 wave model

### Root Models Directory
Located in: `models/`

- `spiral_cnn_model.h5` - CNN model for spiral drawings
- `wave_cnn_model.h5` - CNN model for wave drawings
- `vgg16_enhanced.h5` (58.11 MB) - VGG16 transfer learning model
- `swin_transformer_enhanced.h5` - Swin Transformer model

## 🚀 How to Get the Models

### Option 1: Download Pre-trained Models (Recommended)

**Coming Soon**: Download links will be provided via:
- Google Drive
- Hugging Face Hub
- Cloud storage

### Option 2: Train Models Yourself

You can train the models from scratch using the provided training scripts:

#### 1. Train Handwriting Models

```bash
cd backend
source ml_env/bin/activate  # On Windows: ml_env\Scripts\activate

# Train ResNet50 transfer learning models
python transfer_learning_trainer.py
```

**Training time**: ~30-60 minutes (with GPU)  
**Output**: Models saved to `backend/models/`

#### 2. Train DaT Scan Model

```bash
cd ml_models
source ../backend/ml_env/bin/activate

# Train DaT CNN+LSTM model
python train_dat_model.py
```

**Training time**: ~60-90 minutes (with GPU)  
**Output**: Model saved to `models/dat_scan/`

#### 3. Train Voice Analysis Model

```bash
cd ml-models

# Train speech model
python train_speech_model_v2.py
```

**Training time**: ~20-30 minutes (with GPU)  
**Output**: Model saved to `ml-models/models/speech/`

## 📋 Model Training Requirements

- **Python**: 3.13+
- **TensorFlow**: 2.20+
- **GPU**: NVIDIA GPU with CUDA 12.x (recommended)
- **RAM**: 16 GB minimum
- **Disk Space**: 10 GB free space

## 🔧 Alternative: Use Git LFS

If you plan to collaborate and share models, consider using **Git Large File Storage (LFS)**:

```bash
# Install Git LFS
git lfs install

# Track model files
git lfs track "*.h5"
git lfs track "*.keras"

# Add .gitattributes
git add .gitattributes

# Commit and push
git add backend/models/*.h5 models/*.h5
git commit -m "Add model files via Git LFS"
git push
```

## 📊 Model Performance

### Handwriting Analysis (ResNet50)
- **Spiral Model**: AUC 0.92, Accuracy 89%
- **Wave Model**: AUC 0.90, Accuracy 87%

### Voice Analysis (MFCC + CNN+LSTM)
- **AUC**: 0.87, Accuracy 84%

### DaT Scan Analysis (CNN+LSTM)
- **Current**: AUC 0.50 (37 subjects)
- **Expected**: AUC 0.75-0.80 (66 subjects after NTUA training)

## 📝 Notes

- All models use TensorFlow/Keras `.h5` format
- Models are trained on the datasets described in the main README
- SVM models use `.pkl` format (scikit-learn)
- Model architecture details are in `/docs` directory

## 🆘 Support

If you need access to pre-trained models or have issues training:
1. Open an issue on GitHub
2. Check training logs in `training_*.log` files
3. Verify GPU availability: `nvidia-smi`
4. Check CUDA installation: `python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"`

---

**Last Updated**: November 4, 2025
