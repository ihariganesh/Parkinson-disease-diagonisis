#!/bin/bash

# Complete Model Training Script
# Trains all models for the Multi-Modal Parkinson's Diagnosis System

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Parkinson's Disease Multi-Modal Model Training       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Change to project root
cd "$(dirname "$0")"
PROJECT_ROOT="$(pwd)"

# Activate virtual environment
echo -e "${YELLOW}→ Activating virtual environment...${NC}"
source backend/ml_env/bin/activate

# Change to ml_models directory
cd ml_models

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN} Step 1/3: Preprocessing NTUA Dataset${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Dataset: 80 subjects (56 PD + 24 Non-PD)"
echo "Processing DaT scans to 128x128x16 numpy arrays..."
echo ""

python dat_preprocessing.py \
  --input_dir "/home/hari/Downloads/parkinson/ntua-parkinson-dataset" \
  --output_dir "${PROJECT_ROOT}/ml_models/dat_preprocessed_ntua" \
  --target_size 128 128 \
  --max_slices 16

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Preprocessing complete!${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠️  Preprocessing failed or already done${NC}"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN} Step 2/3: Training DaT Scan Model${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Model: CNN+LSTM with 1.8M parameters"
echo "Expected time: 60-90 minutes with GPU"
echo "Target AUC: 0.75-0.80"
echo ""
echo "Starting training..."
echo ""

python train_dat_model.py \
  --data_dir "${PROJECT_ROOT}/ml_models/dat_preprocessed_ntua" \
  --output_dir "${PROJECT_ROOT}/models/dat_scan" \
  --epochs 100 \
  --batch_size 8 \
  --patience 15

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ DaT model training complete!${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠️  DaT model training failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN} Step 3/3: Training Voice Model (Optional)${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""

if [ -f "train_speech_model.py" ]; then
    echo "Training speech/voice analysis model..."
    echo ""
    
    python train_speech_model.py || echo -e "${YELLOW}⚠️  Voice model training skipped${NC}"
else
    echo -e "${YELLOW}⚠️  Voice training script not found, skipping...${NC}"
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Training Complete! 🎉                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Models trained and saved to:${NC}"
echo "  • DaT Scan: models/dat_scan/dat_model_final_*.keras"
echo "  • Handwriting: backend/models/resnet50_*.h5 (already trained)"
echo "  • Voice: models/speech/ (if training succeeded)"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Restart backend server to load new models"
echo "  2. Test at: http://localhost:5173/demo/comprehensive"
echo "  3. Update README.md with performance metrics"
echo ""
echo -e "${YELLOW}To restart backend:${NC}"
echo "  cd backend && ./ml_env/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
