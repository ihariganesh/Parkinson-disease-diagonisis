#!/bin/bash

# Advanced Parkinson's Detection Setup Script
# This script sets up the transfer learning environment and trains models

echo "🧠 Advanced Parkinson's Detection - Transfer Learning Setup"
echo "=========================================================="

# Check if we're in the right directory
if [ ! -d "ml-models" ]; then
    echo "❌ Please run this script from the parkinson-app root directory"
    exit 1
fi

cd ml-models

echo "📦 Installing required packages..."

# Install Python packages with error handling
install_package() {
    package=$1
    echo "Installing $package..."
    if pip install --user "$package"; then
        echo "✅ $package installed successfully"
    else
        echo "❌ Failed to install $package"
        return 1
    fi
}

# Core ML packages
install_package "torch torchvision" || true
install_package "tensorflow>=2.10.0" || true
install_package "opencv-python" || true
install_package "scikit-learn" || true
install_package "matplotlib" || true
install_package "seaborn" || true
install_package "pillow" || true
install_package "numpy" || true
install_package "joblib" || true
install_package "pandas" || true

echo ""
echo "🔍 Checking dataset availability..."

DATASET_PATH="../archive/drawings"
if [ -d "$DATASET_PATH" ]; then
    echo "✅ Dataset found at $DATASET_PATH"
    
    # Count images
    spiral_healthy=$(find "$DATASET_PATH/spiral/training/healthy" -name "*.png" 2>/dev/null | wc -l)
    spiral_parkinson=$(find "$DATASET_PATH/spiral/training/parkinson" -name "*.png" 2>/dev/null | wc -l)
    wave_healthy=$(find "$DATASET_PATH/wave/training/healthy" -name "*.png" 2>/dev/null | wc -l)
    wave_parkinson=$(find "$DATASET_PATH/wave/training/parkinson" -name "*.png" 2>/dev/null | wc -l)
    
    echo "📊 Dataset Summary:"
    echo "   Spiral - Healthy: $spiral_healthy images"
    echo "   Spiral - Parkinson: $spiral_parkinson images"
    echo "   Wave - Healthy: $wave_healthy images"
    echo "   Wave - Parkinson: $wave_parkinson images"
    echo "   Total: $((spiral_healthy + spiral_parkinson + wave_healthy + wave_parkinson)) images"
else
    echo "❌ Dataset not found at $DATASET_PATH"
    echo "Please ensure the dataset is available before training"
    exit 1
fi

echo ""
echo "🏋️  Starting Model Training..."
echo "This may take 30-60 minutes depending on your hardware"
echo ""

# Run the training script
if python3 train_advanced_models.py; then
    echo ""
    echo "🎉 Training completed successfully!"
    echo ""
    echo "📁 Check the 'trained_models' directory for:"
    echo "   - Trained model files (.h5)"
    echo "   - Training history plots"
    echo "   - Confusion matrices"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Start the backend server to test the models"
    echo "   2. Use the web interface to upload handwriting samples"
    echo "   3. The system will automatically use the best available models"
    echo ""
else
    echo "❌ Training failed. Please check the error messages above."
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Ensure all required packages are installed"
    echo "   2. Check that the dataset is properly formatted"
    echo "   3. Verify you have sufficient disk space and memory"
    echo "   4. For GPU training, ensure CUDA is properly configured"
    exit 1
fi

echo "✅ Setup completed successfully!"