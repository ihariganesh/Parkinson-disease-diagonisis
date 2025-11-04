#!/bin/bash
#
# DaT Scan Model Training Pipeline
# Complete workflow: Preprocessing → Training → Evaluation
#

set -e  # Exit on error

echo "=========================================="
echo "DaT SCAN MODEL TRAINING PIPELINE"
echo "=========================================="
echo ""

# Configuration
PROJECT_ROOT="/home/hari/Downloads/parkinson/parkinson-app"
ML_MODELS_DIR="$PROJECT_ROOT/ml_models"
DATA_DIR="/home/hari/Downloads/parkinson/DAT"
OUTPUT_DIR="$PROJECT_ROOT/ml_models/dat_preprocessed"
MODEL_OUTPUT_DIR="$PROJECT_ROOT/models/dat_scan"

# Activate virtual environment
echo "→ Activating virtual environment..."
source "$PROJECT_ROOT/ml_env/bin/activate"

# Check if data directory exists
if [ ! -d "$DATA_DIR" ]; then
    echo "Error: DaT scan data directory not found: $DATA_DIR"
    echo "Please ensure the DAT folder is in /home/hari/Downloads/parkinson/"
    exit 1
fi

echo "✓ Data directory found: $DATA_DIR"
echo ""

# Step 1: Preprocessing
echo "=========================================="
echo "STEP 1: DATA PREPROCESSING"
echo "=========================================="
cd "$ML_MODELS_DIR"

if [ ! -d "$OUTPUT_DIR" ]; then
    echo "→ Preprocessing DaT scan dataset..."
    python dat_preprocessing.py
    
    if [ $? -eq 0 ]; then
        echo "✓ Preprocessing completed successfully!"
    else
        echo "✗ Preprocessing failed!"
        exit 1
    fi
else
    echo "⚠ Preprocessed data already exists at: $OUTPUT_DIR"
    read -p "Do you want to reprocess? (y/n): " answer
    if [ "$answer" == "y" ]; then
        rm -rf "$OUTPUT_DIR"
        python dat_preprocessing.py
    else
        echo "→ Skipping preprocessing, using existing data"
    fi
fi

echo ""

# Step 2: Model Training
echo "=========================================="
echo "STEP 2: MODEL TRAINING"
echo "=========================================="

echo "→ Training CNN+LSTM model..."
echo "   This may take 1-3 hours depending on your GPU..."
echo ""

python train_dat_model.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Model training completed successfully!"
else
    echo ""
    echo "✗ Model training failed!"
    exit 1
fi

echo ""

# Step 3: Model Validation
echo "=========================================="
echo "STEP 3: MODEL VALIDATION"
echo "=========================================="

# Find the latest trained model
LATEST_MODEL=$(ls -t "$MODEL_OUTPUT_DIR"/dat_model_best_*.keras 2>/dev/null | head -n 1)

if [ -z "$LATEST_MODEL" ]; then
    LATEST_MODEL=$(ls -t "$MODEL_OUTPUT_DIR"/dat_model_*.keras 2>/dev/null | head -n 1)
fi

if [ -n "$LATEST_MODEL" ]; then
    echo "✓ Found trained model: $LATEST_MODEL"
    echo ""
    echo "→ Testing inference service..."
    
    # Test with a sample scan
    SAMPLE_SCAN="$DATA_DIR/Healthy/001"
    if [ -d "$SAMPLE_SCAN" ]; then
        python dat_inference_service.py "$LATEST_MODEL" "$SAMPLE_SCAN"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✓ Inference service working correctly!"
        else
            echo ""
            echo "⚠ Inference service test failed"
        fi
    else
        echo "⚠ Sample scan not found, skipping inference test"
    fi
else
    echo "⚠ No trained model found in $MODEL_OUTPUT_DIR"
fi

echo ""

# Summary
echo "=========================================="
echo "TRAINING PIPELINE COMPLETE!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  Data Directory:    $DATA_DIR"
echo "  Preprocessed Data: $OUTPUT_DIR"
echo "  Model Directory:   $MODEL_OUTPUT_DIR"
echo ""

if [ -n "$LATEST_MODEL" ]; then
    echo "  Latest Model:      $(basename $LATEST_MODEL)"
    echo ""
    echo "Next steps:"
    echo "  1. Review training plots in: $MODEL_OUTPUT_DIR"
    echo "  2. Check evaluation results: $MODEL_OUTPUT_DIR/evaluation_results_*.json"
    echo "  3. Start the backend server to use the model"
    echo "  4. Test via API: POST /api/v1/analysis/dat/analyze"
else
    echo "  ⚠ No model found - training may have failed"
fi

echo ""
echo "=========================================="

# Deactivate virtual environment
deactivate
