#!/usr/bin/env python3
"""
Test the MRI ensemble service directly
"""
import sys
import os
sys.path.append('/home/hari/Downloads/parkinson/parkinson-app/ml-models')

from mri_ensemble_service import MRIEnsembleService

def test_ensemble_service():
    print("Testing MRI Ensemble Service...")
    
    service = MRIEnsembleService()
    test_image = "/home/hari/Downloads/parkinson/MRI/Healthy/t1_blade_tra_dark-fl_010.png"
    
    if os.path.exists(test_image):
        print(f"Testing with image: {test_image}")
        result = service.predict_with_ensemble(test_image)
        
        print("Result:")
        for key, value in result.items():
            print(f"  {key}: {value}")
    else:
        print("Test image not found")

if __name__ == "__main__":
    test_ensemble_service()