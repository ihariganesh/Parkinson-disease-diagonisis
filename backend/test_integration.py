"""
Frontend-Backend Integration Test for Parkinson's Detection App
This script tests the complete authentication flow
"""
import requests
import json
import time

def test_backend_auth():
    """Test backend authentication"""
    print("🔧 Testing Backend Authentication...")
    
    # Test with a new user
    import uuid
    test_email = f"test{str(uuid.uuid4())[:8]}@example.com"
    
    # Register new user
    register_data = {
        "email": test_email,
        "password": "testpass123",
        "first_name": "Integration",
        "last_name": "Test",
        "role": "PATIENT"
    }
    
    try:
        response = requests.post("http://127.0.0.1:8000/api/v1/auth/register", json=register_data)
        if response.status_code != 200:
            print(f"❌ Registration failed: {response.json()}")
            return False
        print(f"✅ User registered: {test_email}")
        
        # Test login
        login_data = {"username": test_email, "password": "testpass123"}
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.json()}")
            return False
            
        token_data = response.json()
        token = token_data["access_token"]
        user = token_data["user"]
        
        print(f"✅ Login successful for: {user['first_name']} {user['last_name']}")
        print(f"   Role: {user['role']}")
        print(f"   Token: {token[:20]}...")
        
        # Test protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://127.0.0.1:8000/api/v1/auth/me", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ /me endpoint failed: {response.json()}")
            return False
            
        me_data = response.json()
        print(f"✅ Profile retrieved: {me_data['email']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def check_frontend_server():
    """Check if frontend server is running"""
    try:
        response = requests.get("http://localhost:5173/", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Run complete integration test"""
    print("🚀 Parkinson's Detection App - Integration Test")
    print("=" * 60)
    
    # Check backend
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not running!")
            return
        print("✅ Backend is running")
    except:
        print("❌ Backend is not accessible!")
        return
    
    # Test authentication
    auth_ok = test_backend_auth()
    
    # Check frontend
    frontend_running = check_frontend_server()
    if frontend_running:
        print("✅ Frontend is running")
    else:
        print("❌ Frontend is not running")
    
    print("\n" + "=" * 60)
    print("📊 Integration Test Results:")
    print(f"Backend Health: ✅")
    print(f"Authentication: {'✅' if auth_ok else '❌'}")
    print(f"Frontend Server: {'✅' if frontend_running else '❌'}")
    
    if auth_ok:
        print("\n🎉 Backend authentication is working perfectly!")
        print("\n📋 What works:")
        print("✅ User registration (POST /api/v1/auth/register)")
        print("✅ User login (POST /api/v1/auth/login)")
        print("✅ JWT token generation")
        print("✅ Protected endpoints (GET /api/v1/auth/me)")
        print("✅ SQLite database integration")
        
        if frontend_running:
            print("\n🌐 Both servers are running:")
            print("• Frontend: http://localhost:5173")
            print("• Backend: http://127.0.0.1:8000")
            print("• API Docs: http://127.0.0.1:8000/docs")
            
            print("\n🧪 Test the full flow:")
            print("1. Open: http://localhost:5173/register")
            print("2. Register a new account")
            print("3. Login with your credentials")
            print("4. Check the network tab for API calls")
        else:
            print("\n⚠️ Frontend server is not running")
            print("Start it with: npm run dev (in frontend directory)")
    else:
        print("\n❌ Authentication issues detected. Check the logs above.")

if __name__ == "__main__":
    main()