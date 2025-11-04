#!/bin/bash
# 🚀 Parkinson's Disease Detection App Startup Script

echo "🧠 Starting Parkinson's Disease Detection App..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements_minimal.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Set up environment
source .env_setup.sh

# Test imports
echo "🔍 Testing imports..."
python test_imports.py

if [ $? -eq 0 ]; then
    echo "🎉 All systems ready!"
    echo ""
    echo "Available commands:"
    echo "  🏃 Start API server:           uvicorn backend.app.main:app --reload"
    echo "  🧪 Train focused ensemble:     python train_focused_ensemble.py"
    echo "  🔍 Verify ensemble config:     python verify_focused_ensemble.py"
    echo "  🧪 Test models:               python test_models.py"
    echo ""
else
    echo "❌ Import tests failed. Please check the error messages above."
    exit 1
fi
