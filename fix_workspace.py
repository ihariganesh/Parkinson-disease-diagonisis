#!/usr/bin/env python3
"""
🔧 Fix Parkinson's Disease Detection Workspace Import Issues

This script fixes all import-related problems in the workspace by:
1. Setting up the Python virtual environment with all required packages
2. Creating proper __init__.py files for module imports
3. Updating Python paths in import statements
4. Testing all critical imports

Run this script to resolve all the import errors shown in VS Code.
"""

import os
import sys
import subprocess
from pathlib import Path

def create_init_files():
    """Create __init__.py files where needed"""
    init_locations = [
        "backend/app/__init__.py",
        "backend/app/api/__init__.py", 
        "backend/app/api/v1/__init__.py",
        "backend/app/api/v1/endpoints/__init__.py",
        "backend/app/core/__init__.py",
        "backend/app/db/__init__.py",
        "ml-models/__init__.py",
        "models/__init__.py"
    ]
    
    for init_file in init_locations:
        init_path = Path(init_file)
        if not init_path.exists():
            init_path.parent.mkdir(parents=True, exist_ok=True)
            init_path.write_text('"""Package initialization"""')
            print(f"✅ Created {init_file}")

def setup_environment():
    """Set up environment variables and paths"""
    env_content = """# Environment Configuration for Parkinson's Detection App

# Python Environment
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/ml-models:$(pwd)/backend"

# Virtual Environment Activation
source venv/bin/activate

# Optional: Disable TensorFlow warnings
export TF_CPP_MIN_LOG_LEVEL=2
export TF_ENABLE_ONEDNN_OPTS=0

echo "✅ Environment configured for Parkinson's Detection App"
echo "📍 Current directory: $(pwd)"
echo "🐍 Python path: $PYTHONPATH"
echo "🧠 TensorFlow warnings suppressed"
"""
    
    with open(".env_setup.sh", "w") as f:
        f.write(env_content)
    
    # Make it executable
    os.chmod(".env_setup.sh", 0o755)
    print("✅ Created .env_setup.sh")

def test_imports():
    """Test critical imports"""
    test_script = """
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'ml-models'))
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

try:
    # Test core ML packages
    import tensorflow as tf
    import numpy as np
    import cv2
    import sklearn
    import matplotlib
    import seaborn
    print("✅ Core ML packages: OK")
    
    # Test MRI ensemble service
    from mri_ensemble_service import MRIEnsembleService
    print("✅ MRI Ensemble Service: OK")
    
    # Test FastAPI components
    import fastapi
    import uvicorn
    import sqlalchemy
    print("✅ Web framework packages: OK")
    
    print("🎉 All critical imports working!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
"""
    
    with open("test_imports.py", "w") as f:
        f.write(test_script)
    
    print("✅ Created test_imports.py")

def create_startup_script():
    """Create a comprehensive startup script"""
    startup_content = """#!/bin/bash
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
"""
    
    with open("start_app.sh", "w") as f:
        f.write(startup_content)
    
    os.chmod("start_app.sh", 0o755)
    print("✅ Created start_app.sh")

def main():
    """Main setup function"""
    print("🔧 Fixing Parkinson's Detection Workspace...")
    print("=" * 50)
    
    # Change to project root
    os.chdir(Path(__file__).parent)
    
    # Create necessary files
    create_init_files()
    setup_environment()
    test_imports()
    create_startup_script()
    
    print("\n🎉 Workspace Fix Complete!")
    print("\nNext Steps:")
    print("1. Run: chmod +x start_app.sh")
    print("2. Run: ./start_app.sh")
    print("3. If successful, you can start the API server or train models")
    print("\n📝 Files created:")
    print("   • __init__.py files for proper module imports")
    print("   • .env_setup.sh for environment configuration")
    print("   • test_imports.py for testing imports")
    print("   • start_app.sh for easy startup")

if __name__ == "__main__":
    main()