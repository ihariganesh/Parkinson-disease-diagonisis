#!/usr/bin/env python3
"""
Test script to verify frontend endpoint fixes
"""

import requests
import os

def test_mri_demo_endpoint():
    """Test that the demo endpoint is working"""
    print("Testing MRI demo endpoint...")
    
    # Test endpoint availability
    url = "http://localhost:8000/api/v1/analysis/mri/demo"
    
    # Use a test image if available
    test_image_path = "/home/hari/Downloads/parkinson/MRI/Healthy"
    if os.path.exists(test_image_path):
        # Find first image file
        for file in os.listdir(test_image_path):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(test_image_path, file)
                print(f"Using test image: {image_path}")
                
                try:
                    with open(image_path, 'rb') as f:
                        files = {'file': f}
                        response = requests.post(url, files=files, timeout=10)
                    
                    print(f"Status Code: {response.status_code}")
                    print(f"Response: {response.json()}")
                    
                    if response.status_code == 200:
                        print("✅ Demo endpoint is working correctly!")
                        return True
                    else:
                        print("❌ Demo endpoint returned error")
                        return False
                        
                except Exception as e:
                    print(f"❌ Error testing endpoint: {e}")
                    return False
                break
    else:
        print("❌ No test images found")
        return False

def test_health_endpoint():
    """Test that the server is running"""
    print("Testing server health...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print("❌ Server health check failed")
            return False
    except Exception as e:
        print(f"❌ Server is not responding: {e}")
        return False

if __name__ == "__main__":
    print("=== Frontend Endpoint Fix Verification ===\n")
    
    # Test server health first
    if test_health_endpoint():
        print()
        # Test the demo endpoint
        test_mri_demo_endpoint()
    else:
        print("Please ensure the backend server is running with: cd parkinson-app && ./start_app.sh")
    
    print("\n=== Test Complete ===")