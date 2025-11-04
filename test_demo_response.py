#!/usr/bin/env python3
"""
Quick test to verify the demo endpoint response format
"""

import requests
import json

def test_demo_endpoint():
    """Test the demo endpoint response format"""
    url = "http://localhost:8000/api/v1/analysis/mri/demo"
    
    # Create a simple test file (1x1 pixel PNG)
    import io
    from PIL import Image
    
    # Create a small test image
    img = Image.new('RGB', (1, 1), color='black')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    try:
        files = {'file': ('test.png', img_bytes, 'image/png')}
        response = requests.post(url, files=files, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Response format:")
            print(json.dumps(result, indent=2))
            
            # Check if it has the expected structure
            if 'analysis_result' in result and 'predicted_class' in result['analysis_result']:
                print("✅ Response format is correct for frontend!")
            else:
                print("❌ Response format still needs fixing")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")

if __name__ == "__main__":
    print("=== Testing Demo Endpoint Response Format ===")
    test_demo_endpoint()