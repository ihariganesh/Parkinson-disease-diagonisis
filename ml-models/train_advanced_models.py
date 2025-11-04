#!/usr/bin/env python3
"""
Training Script for Advanced Parkinson's Detection Models
Trains ResNet, EfficientNet, MobileNetV2, Vision Transformer, and Ensemble models
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'tensorflow>=2.10.0',
        'opencv-python',
        'scikit-learn',
        'matplotlib',
        'seaborn',
        'pillow',
        'numpy',
        'joblib'
    ]
    
    print("Checking required packages...")
    missing_packages = []
    
    for package in required_packages:
        try:
            package_name = package.split('>=')[0].split('==')[0]
            if package_name == 'opencv-python':
                import cv2
            elif package_name == 'tensorflow':
                import tensorflow as tf
                print(f"✓ TensorFlow version: {tf.__version__}")
            elif package_name == 'scikit-learn':
                import sklearn
            elif package_name == 'matplotlib':
                import matplotlib
            elif package_name == 'seaborn':
                import seaborn
            elif package_name == 'pillow':
                from PIL import Image
            elif package_name == 'numpy':
                import numpy
            elif package_name == 'joblib':
                import joblib
            
            print(f"✓ {package_name}")
            
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package_name}")
    
    if missing_packages:
        print("\nMissing packages found. Please install them using:")
        print("pip install " + " ".join(missing_packages))
        return False
    
    print("✓ All required packages are installed!")
    return True

def setup_gpu():
    """Setup GPU configuration"""
    try:
        import tensorflow as tf
        
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                print(f"✓ GPU setup complete. {len(gpus)} GPU(s) available")
                return True
            except RuntimeError as e:
                print(f"GPU setup error: {e}")
                return False
        else:
            print("ℹ No GPU found. Training will use CPU")
            return False
    except ImportError:
        print("TensorFlow not available for GPU setup")
        return False

def train_models():
    """Train all transfer learning models"""
    print("\n" + "="*60)
    print("STARTING TRANSFER LEARNING MODEL TRAINING")
    print("="*60)
    
    # Check if data exists
    data_path = Path("/home/hari/Downloads/parkinson/parkinson-app/archive/drawings")
    if not data_path.exists():
        print(f"❌ Dataset not found at {data_path}")
        print("Please ensure the dataset is available at the correct location")
        return False
    
    print(f"✓ Dataset found at {data_path}")
    
    # Check GPU
    setup_gpu()
    
    # Import and run training
    try:
        from transfer_learning_models import ParkinsonsTransferLearningModels
        
        print("\nInitializing training system...")
        trainer = ParkinsonsTransferLearningModels(str(data_path))
        
        print("Starting comprehensive model training...")
        results = trainer.train_all_models()
        
        print("\n" + "="*60)
        print("TRAINING COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        print("\nFinal Results:")
        for model_name, accuracy in results.items():
            print(f"  {model_name:20}: {accuracy:.4f}")
        
        if results:
            best_model = max(results.items(), key=lambda x: x[1])
            print(f"\n🏆 Best Model: {best_model[0]} (Accuracy: {best_model[1]:.4f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_models():
    """Test the trained models"""
    print("\n" + "="*60)
    print("TESTING TRAINED MODELS")
    print("="*60)
    
    try:
        from advanced_detector import AdvancedParkinsonsDetector
        
        # Initialize detector
        detector = AdvancedParkinsonsDetector()
        
        if not detector.models:
            print("❌ No trained models found. Please train models first.")
            return False
        
        print(f"✓ Loaded {len(detector.models)} models: {list(detector.models.keys())}")
        
        # Test with sample images
        test_path = Path("/home/hari/Downloads/parkinson/parkinson-app/archive/drawings/spiral/testing")
        
        if test_path.exists():
            # Test healthy sample
            healthy_path = test_path / "healthy"
            if healthy_path.exists():
                test_files = list(healthy_path.glob("*.png"))
                if test_files:
                    print(f"\nTesting with healthy sample: {test_files[0].name}")
                    result = detector.analyze_handwriting(test_files[0], "spiral")
                    
                    if 'error' not in result:
                        summary = result['prediction_summary']
                        print(f"✓ Prediction: {summary['final_diagnosis']}")
                        print(f"✓ Confidence: {summary['confidence_score']}")
                        print(f"✓ Models used: {result['ensemble_prediction']['models_used']}")
                    else:
                        print(f"❌ Test failed: {result['error']}")
            
            # Test Parkinson sample
            parkinson_path = test_path / "parkinson"
            if parkinson_path.exists():
                test_files = list(parkinson_path.glob("*.png"))
                if test_files:
                    print(f"\nTesting with Parkinson sample: {test_files[0].name}")
                    result = detector.analyze_handwriting(test_files[0], "spiral")
                    
                    if 'error' not in result:
                        summary = result['prediction_summary']
                        print(f"✓ Prediction: {summary['final_diagnosis']}")
                        print(f"✓ Confidence: {summary['confidence_score']}")
                        print(f"✓ Models used: {result['ensemble_prediction']['models_used']}")
                    else:
                        print(f"❌ Test failed: {result['error']}")
        
        print("\n✓ Model testing completed!")
        return True
        
    except Exception as e:
        print(f"❌ Testing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main training and testing pipeline"""
    print("Advanced Parkinson's Detection - Transfer Learning Training Pipeline")
    print("="*70)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please install missing packages.")
        sys.exit(1)
    
    # Train models
    print("\nStarting training phase...")
    training_success = train_models()
    
    if training_success:
        print("\n✅ Training phase completed successfully!")
        
        # Test models
        print("\nStarting testing phase...")
        testing_success = test_models()
        
        if testing_success:
            print("\n🎉 All phases completed successfully!")
            print("\nNext steps:")
            print("1. Check the 'trained_models' directory for saved models")
            print("2. Review training plots and confusion matrices")
            print("3. Integrate the models with your web application")
            print("4. Test with your own handwriting samples")
            
        else:
            print("\n⚠️  Training successful but testing failed")
    else:
        print("\n❌ Training failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    
    total_time = end_time - start_time
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    seconds = int(total_time % 60)
    
    print(f"\nTotal execution time: {hours:02d}:{minutes:02d}:{seconds:02d}")