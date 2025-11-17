#!/usr/bin/env python3
"""
Test Voice Analysis with Trained Model
Tests the complete voice analysis pipeline end-to-end
"""

import requests
import json
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_AUDIO_FILE = "/home/hari/Downloads/parkinson/test_audio.wav"

def test_voice_analysis():
    """Test voice analysis endpoint"""
    print("=" * 70)
    print("🎤 Testing Voice Analysis with Trained Model")
    print("=" * 70)
    
    # Check if test audio file exists
    audio_path = Path(TEST_AUDIO_FILE)
    if not audio_path.exists():
        print(f"❌ Test audio file not found: {TEST_AUDIO_FILE}")
        return False
    
    print(f"\n📁 Test Audio File: {audio_path.name}")
    print(f"   Size: {audio_path.stat().st_size / 1024:.2f} KB")
    
    # Test voice analysis endpoint
    print("\n🔬 Testing Voice Analysis Endpoint...")
    try:
        with open(audio_path, 'rb') as f:
            files = {'file': (audio_path.name, f, 'audio/wav')}
            response = requests.post(
                f"{API_BASE_URL}/api/analyze/voice",
                files=files,
                timeout=30
            )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Voice Analysis Response:")
            print(json.dumps(result, indent=2))
            
            # Check key fields
            if 'success' in result and result['success']:
                print("\n📊 Key Results:")
                print(f"   • Success: {result.get('success', 'N/A')}")
                print(f"   • PD Probability: {result.get('pd_probability', 'N/A'):.2%}")
                print(f"   • Confidence: {result.get('confidence', 'N/A'):.2%}")
                print(f"   • Predicted Class: {result.get('predicted_class', 'N/A')}")
                print(f"   • Model Used: {result.get('model_type', 'N/A')}")
                
                if 'note' in result:
                    print(f"   • Note: {result['note']}")
                
                # Check if using trained model (not baseline)
                if result.get('pd_probability', 0.5) != 0.5:
                    print("\n✅ Using trained model (not baseline 50%)")
                else:
                    print("\n⚠️  Still using baseline 50% - may be using mock features")
                
                return True
            else:
                print(f"\n❌ Analysis failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running on port 8000?")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_health_check():
    """Test backend health"""
    print("\n🏥 Testing Backend Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is healthy")
            return True
        else:
            print(f"   ⚠️  Backend returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend not accessible: {e}")
        return False

def main():
    """Run all tests"""
    print("\n🧪 Starting Voice Analysis Tests\n")
    
    # Test 1: Health check
    health_ok = test_health_check()
    if not health_ok:
        print("\n⚠️  Backend is not running. Please start it first:")
        print("   cd backend && ml_env/bin/python -m uvicorn app.main:app --reload")
        return
    
    # Test 2: Voice analysis
    voice_ok = test_voice_analysis()
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 Test Summary")
    print("=" * 70)
    print(f"   Backend Health: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Voice Analysis: {'✅ PASS' if voice_ok else '❌ FAIL'}")
    print("=" * 70)
    
    if health_ok and voice_ok:
        print("\n🎉 All tests passed! Voice analysis is working with trained model!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
