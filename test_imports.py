
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
    
    # MRI analysis removed - focusing on speech and handwriting analysis
    print("ℹ️ MRI Analysis: Removed to clean up space")
    
    # Test FastAPI components
    import fastapi
    import uvicorn
    import sqlalchemy
    print("✅ Web framework packages: OK")
    
    print("🎉 All critical imports working!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
