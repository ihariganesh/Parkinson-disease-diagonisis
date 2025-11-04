"""
Test script to verify the database and API setup
"""
import requests
import json

def test_api_health():
    """Test the health endpoint"""
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        if response.status_code == 200:
            print("✅ Health check passed:", response.json())
            return True
        else:
            print("❌ Health check failed:", response.status_code)
            return False
    except Exception as e:
        print("❌ Health check error:", str(e))
        return False

def test_api_v1_health():
    """Test the API v1 health endpoint"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/health")
        if response.status_code == 200:
            print("✅ API v1 health check passed:", response.json())
            return True
        else:
            print("❌ API v1 health check failed:", response.status_code)
            return False
    except Exception as e:
        print("❌ API v1 health check error:", str(e))
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Parkinson's Detection API...")
    print("=" * 50)
    
    health_ok = test_api_health()
    api_health_ok = test_api_v1_health()
    
    print("=" * 50)
    if health_ok and api_health_ok:
        print("🎉 All tests passed! The API is ready.")
        print("\n📋 Available endpoints:")
        print("- API Documentation: http://127.0.0.1:8000/docs")
        print("- Health Check: http://127.0.0.1:8000/health")
        print("- API v1 Health: http://127.0.0.1:8000/api/v1/health")
        print("- Authentication: http://127.0.0.1:8000/api/v1/auth/*")
        print("- Patients: http://127.0.0.1:8000/api/v1/patients/*")
        print("- Medical Data: http://127.0.0.1:8000/api/v1/medical-data/*")
        print("- Analysis: http://127.0.0.1:8000/api/v1/analysis/*")
    else:
        print("❌ Some tests failed. Check the server status.")

if __name__ == "__main__":
    main()