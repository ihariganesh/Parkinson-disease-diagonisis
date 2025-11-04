#!/usr/bin/env python3
"""
Quick Test Script for DaT Scan Module
Verifies all components are working correctly
"""

import sys
import os
from pathlib import Path

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def check_dataset():
    """Check if DAT dataset exists"""
    print_section("1. CHECKING DATASET")
    
    data_dir = Path("/home/hari/Downloads/parkinson/DAT")
    if not data_dir.exists():
        print("❌ DAT dataset not found!")
        print(f"   Expected location: {data_dir}")
        return False
    
    healthy_dir = data_dir / "Healthy"
    pd_dir = data_dir / "PD"
    
    healthy_count = len(list(healthy_dir.iterdir())) if healthy_dir.exists() else 0
    pd_count = len(list(pd_dir.iterdir())) if pd_dir.exists() else 0
    
    print(f"✅ Dataset found: {data_dir}")
    print(f"   Healthy subjects: {healthy_count}")
    print(f"   PD subjects: {pd_count}")
    print(f"   Total: {healthy_count + pd_count}")
    
    return True

def check_preprocessing():
    """Check if data is preprocessed"""
    print_section("2. CHECKING PREPROCESSED DATA")
    
    preprocess_dir = Path("/home/hari/Downloads/parkinson/parkinson-app/ml_models/dat_preprocessed")
    
    if not preprocess_dir.exists():
        print("⚠️  Data not preprocessed yet")
        print("   Run: python ml_models/dat_preprocessing.py")
        return False
    
    required_files = [
        "train_X.npy", "train_y.npy",
        "val_X.npy", "val_y.npy",
        "test_X.npy", "test_y.npy",
        "metadata.json"
    ]
    
    missing = []
    for file in required_files:
        if not (preprocess_dir / file).exists():
            missing.append(file)
    
    if missing:
        print(f"⚠️  Missing files: {missing}")
        return False
    
    print(f"✅ Preprocessed data found: {preprocess_dir}")
    
    # Load and print stats
    import numpy as np
    train_X = np.load(preprocess_dir / "train_X.npy")
    train_y = np.load(preprocess_dir / "train_y.npy")
    val_X = np.load(preprocess_dir / "val_X.npy")
    test_X = np.load(preprocess_dir / "test_X.npy")
    
    print(f"   Train: {train_X.shape}, Labels: {train_y.shape}")
    print(f"   Val:   {val_X.shape}")
    print(f"   Test:  {test_X.shape}")
    
    return True

def check_model():
    """Check if model is trained"""
    print_section("3. CHECKING TRAINED MODEL")
    
    model_dir = Path("/home/hari/Downloads/parkinson/parkinson-app/models/dat_scan")
    
    if not model_dir.exists():
        print("⚠️  Model directory not found")
        print("   Models will be saved here after training")
        return False
    
    model_files = list(model_dir.glob("dat_model_*.keras"))
    
    if not model_files:
        print("⚠️  No trained models found")
        print("   Run: python ml_models/train_dat_model.py")
        return False
    
    latest_model = sorted(model_files)[-1]
    print(f"✅ Trained model found: {latest_model.name}")
    print(f"   Size: {latest_model.stat().st_size / (1024*1024):.1f} MB")
    
    # Check for evaluation results
    eval_files = list(model_dir.glob("evaluation_results_*.json"))
    if eval_files:
        import json
        with open(eval_files[-1]) as f:
            results = json.load(f)
        
        print("\n   Model Performance:")
        if 'roc_auc' in results:
            print(f"   - AUC: {results['roc_auc']:.4f}")
        if 'classification_report' in results:
            report = results['classification_report']
            print(f"   - Accuracy: {report['accuracy']:.4f}")
    
    return True

def check_backend():
    """Check if backend service is configured"""
    print_section("4. CHECKING BACKEND INTEGRATION")
    
    service_file = Path("/home/hari/Downloads/parkinson/parkinson-app/backend/app/services/dat_analysis_service.py")
    endpoint_file = Path("/home/hari/Downloads/parkinson/parkinson-app/backend/app/api/v1/endpoints/analysis.py")
    
    if not service_file.exists():
        print("❌ Backend service not found!")
        return False
    
    if not endpoint_file.exists():
        print("❌ API endpoints not found!")
        return False
    
    print(f"✅ Backend service: {service_file.name}")
    print(f"✅ API endpoints: {endpoint_file.name}")
    
    # Check if endpoint is registered
    with open(endpoint_file) as f:
        content = f.read()
        if '/dat/analyze' in content:
            print("✅ DaT scan endpoints registered:")
            print("   - POST /api/v1/analysis/dat/analyze")
            print("   - GET /api/v1/analysis/dat/status")
        else:
            print("⚠️  DaT scan endpoints not found in API")
            return False
    
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print_section("5. CHECKING DEPENDENCIES")
    
    required_packages = {
        'tensorflow': 'tensorflow',
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'sklearn': 'scikit-learn',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn'
    }
    
    missing = []
    installed = []
    
    for module, package in required_packages.items():
        try:
            __import__(module)
            installed.append(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        print(f"\n   Install with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    print(f"✅ All required packages installed:")
    for pkg in installed:
        print(f"   - {pkg}")
    
    return True

def print_next_steps(results):
    """Print next steps based on check results"""
    print_section("NEXT STEPS")
    
    dataset_ok, preprocess_ok, model_ok, backend_ok, deps_ok = results
    
    if not deps_ok:
        print("1. Install missing dependencies:")
        print("   pip install tensorflow opencv-python numpy scikit-learn matplotlib seaborn")
        return
    
    if not dataset_ok:
        print("1. Ensure DAT dataset is in: /home/hari/Downloads/parkinson/DAT/")
        print("   Structure: DAT/Healthy/001/, DAT/PD/001/, etc.")
        return
    
    if not preprocess_ok:
        print("1. Preprocess the dataset:")
        print("   cd ml_models")
        print("   python dat_preprocessing.py")
        return
    
    if not model_ok:
        print("1. Train the model:")
        print("   ./train_dat_model.sh")
        print("   (or manually: python ml_models/train_dat_model.py)")
        return
    
    if not backend_ok:
        print("1. Backend integration issue - check files")
        return
    
    # All checks passed
    print("✅ ALL SYSTEMS READY!")
    print("\nYou can now:")
    print("  1. Start the backend:")
    print("     cd backend")
    print("     uvicorn app.main:app --reload")
    print()
    print("  2. Test the API:")
    print("     curl http://localhost:8000/api/v1/analysis/dat/status")
    print()
    print("  3. Make predictions:")
    print("     curl -X POST http://localhost:8000/api/v1/analysis/dat/analyze \\")
    print("       -H 'Authorization: Bearer TOKEN' \\")
    print("       -F 'files=@scan1.png' -F 'files=@scan2.png' ...")

def main():
    print("="*80)
    print("  DaT SCAN MODULE - SYSTEM CHECK")
    print("="*80)
    
    results = [
        check_dataset(),
        check_preprocessing(),
        check_model(),
        check_backend(),
        check_dependencies()
    ]
    
    print_next_steps(results)
    
    print("\n" + "="*80)
    
    # Summary
    total = len(results)
    passed = sum(results)
    
    print(f"\nSummary: {passed}/{total} checks passed")
    
    if passed == total:
        print("Status: 🟢 READY FOR PRODUCTION")
        sys.exit(0)
    elif passed >= 3:
        print("Status: 🟡 NEEDS SETUP")
        sys.exit(0)
    else:
        print("Status: 🔴 SETUP REQUIRED")
        sys.exit(1)

if __name__ == "__main__":
    main()
