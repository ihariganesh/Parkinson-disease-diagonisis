"""
Test authentication endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_register():
    """Test user registration"""
    print("🧪 Testing user registration...")
    
    user_data = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "role": "PATIENT"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            return True
        else:
            print(f"❌ Registration failed: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def test_login():
    """Test user login"""
    print("\n🧪 Testing user login...")
    
    # Use form data for OAuth2PasswordRequestForm
    login_data = {
        "username": "testuser@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login", 
            data=login_data,  # Use data instead of json for form data
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            return data.get("access_token")
        else:
            print(f"❌ Login failed: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_me_endpoint(token):
    """Test current user endpoint"""
    print("\n🧪 Testing /me endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Me endpoint successful!")
            return True
        else:
            print(f"❌ Me endpoint failed: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Me endpoint error: {e}")
        return False

def test_health_check():
    """Test API health"""
    print("\n🧪 Testing API health...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ API health check passed!")
            return True
        else:
            print(f"❌ API health check failed")
            return False
            
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

def main():
    """Run all authentication tests"""
    print("🚀 Testing Parkinson's Detection API Authentication")
    print("=" * 60)
    
    # Test API health first
    health_ok = test_health_check()
    if not health_ok:
        print("❌ API is not healthy, stopping tests")
        return
    
    # Test registration
    register_ok = test_register()
    
    # Test login
    token = test_login()
    
    # Test protected endpoint
    if token:
        me_ok = test_me_endpoint(token)
    else:
        me_ok = False
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"Health Check: {'✅' if health_ok else '❌'}")
    print(f"Registration: {'✅' if register_ok else '❌'}")
    print(f"Login: {'✅' if token else '❌'}")
    print(f"Me Endpoint: {'✅' if token and me_ok else '❌'}")
    
    if health_ok and register_ok and token and me_ok:
        print("\n🎉 All authentication tests passed!")
        print("\n✨ Frontend can now connect to:")
        print("- Register: POST /api/v1/auth/register")
        print("- Login: POST /api/v1/auth/login (form data)")
        print("- Profile: GET /api/v1/auth/me (with Bearer token)")
    else:
        print("\n❌ Some tests failed. Check the issues above.")

if __name__ == "__main__":
    main()