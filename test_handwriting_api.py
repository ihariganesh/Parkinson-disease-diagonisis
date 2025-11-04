#!/usr/bin/env python3
"""
Test script for handwriting analysis API
"""
import requests
import os
import sys

def test_handwriting_api():
    """Test the handwriting analysis API endpoint"""
    # API endpoint
    url = "http://localhost:8000/api/v1/handwriting/upload"
    
    # Test image path
    test_image_path = "archive/spiral/testing/healthy/V01HE01.png"
    
    if not os.path.exists(test_image_path):
        # Find any available test image
        test_dir = "archive/spiral/testing/healthy"
        if os.path.exists(test_dir):
            files = [f for f in os.listdir(test_dir) if f.endswith('.png')]
            if files:
                test_image_path = os.path.join(test_dir, files[0])
                print(f"Using test image: {test_image_path}")
            else:
                print("No test images found!")
                return
        else:
            print("Test directory not found!")
            return
    
    try:
        # Test the API
        with open(test_image_path, 'rb') as f:
            files = {'file': f}
            data = {'drawing_type': 'spiral'}
            
            print("Sending request to handwriting analysis API...")
            response = requests.post(url, files=files, data=data)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API Test Successful!")
                print(f"Analysis ID: {result.get('analysis_id', 'N/A')}")
                print(f"Prediction: {result.get('prediction', 'N/A')}")
                print(f"Confidence: {result.get('confidence_score', 'N/A')}")
            else:
                print("❌ API Test Failed!")
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_models_exist():
    """Check if trained models exist"""
    model_files = [
        "models/spiral_cnn_model.h5",
        "models/spiral_svm_model_svm.pkl",
        "models/spiral_svm_model_scaler.pkl",
        "models/wave_cnn_model.h5",
        "models/wave_svm_model_svm.pkl",
        "models/wave_svm_model_scaler.pkl"
    ]
    
    print("Checking trained models:")
    all_exist = True
    for model_file in model_files:
        exists = os.path.exists(model_file)
        status = "✅" if exists else "❌"
        print(f"{status} {model_file}")
        if not exists:
            all_exist = False
    
    if all_exist:
        print("✅ All models are present!")
    else:
        print("❌ Some models are missing!")
    
    return all_exist

def test_dataset_exists():
    """Check if dataset exists"""
    dataset_paths = [
        "archive/spiral/training/healthy",
        "archive/spiral/training/parkinson",
        "archive/spiral/testing/healthy",
        "archive/spiral/testing/parkinson",
        "archive/wave/training/healthy",
        "archive/wave/training/parkinson",
        "archive/wave/testing/healthy",
        "archive/wave/testing/parkinson"
    ]
    
    print("Checking dataset:")
    all_exist = True
    for path in dataset_paths:
        exists = os.path.exists(path)
        status = "✅" if exists else "❌"
        count = len([f for f in os.listdir(path) if f.endswith('.png')]) if exists else 0
        print(f"{status} {path} ({count} images)")
        if not exists:
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    print("🧠 Parkinson's Handwriting Analysis System Test")
    print("=" * 50)
    
    # Test 1: Check dataset
    print("\n1. Dataset Check:")
    dataset_ok = test_dataset_exists()
    
    # Test 2: Check models
    print("\n2. Model Check:")
    models_ok = test_models_exist()
    
    # Test 3: API Test
    print("\n3. API Test:")
    if dataset_ok and models_ok:
        test_handwriting_api()
    else:
        print("❌ Skipping API test due to missing dataset or models")
    
    print("\n" + "=" * 50)
    print("Test completed!")