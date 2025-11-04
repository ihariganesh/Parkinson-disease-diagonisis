"""
Test authentication flow by making direct HTTP requests
"""
import json
import time
import webbrowser

def test_with_curl():
    """Test using curl commands"""
    import subprocess
    
    print("🧪 Testing Parkinson's Detection App Authentication...")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        result = subprocess.run([
            'curl', '-s', 'http://127.0.0.1:8000/health'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Health check passed")
            print("Response:", result.stdout)
        else:
            print("❌ Health check failed")
            print("Error:", result.stderr)
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Registration
    print("\n2. Testing user registration...")
    reg_data = {
        "email": "patient@example.com",
        "password": "securepassword123",
        "first_name": "Jane",
        "last_name": "Doe",
        "role": "PATIENT"
    }
    
    try:
        result = subprocess.run([
            'curl', '-s', '-X', 'POST',
            'http://127.0.0.1:8000/api/v1/auth/register',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps(reg_data)
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Registration request sent")
            print("Response:", result.stdout)
        else:
            print("❌ Registration failed")
            print("Error:", result.stderr)
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    # Test 3: Login
    print("\n3. Testing user login...")
    try:
        result = subprocess.run([
            'curl', '-s', '-X', 'POST',
            'http://127.0.0.1:8000/api/v1/auth/login',
            '-H', 'Content-Type: application/x-www-form-urlencoded',
            '-d', 'username=patient@example.com&password=securepassword123'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Login request sent")
            print("Response:", result.stdout)
            
            # Try to parse the response to get the token
            try:
                response_data = json.loads(result.stdout)
                if 'access_token' in response_data:
                    token = response_data['access_token']
                    print(f"🔑 Access token received: {token[:20]}...")
                    
                    # Test 4: Protected endpoint
                    print("\n4. Testing protected endpoint...")
                    result = subprocess.run([
                        'curl', '-s', '-X', 'GET',
                        'http://127.0.0.1:8000/api/v1/auth/me',
                        '-H', f'Authorization: Bearer {token}'
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        print("✅ Protected endpoint accessed")
                        print("User info:", result.stdout)
                    else:
                        print("❌ Protected endpoint failed")
                        print("Error:", result.stderr)
                        
            except json.JSONDecodeError:
                print("⚠️ Could not parse login response as JSON")
                
        else:
            print("❌ Login failed")
            print("Error:", result.stderr)
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Authentication testing completed!")
    print("\n📋 Next steps:")
    print("1. Backend API is running at: http://127.0.0.1:8000")
    print("2. Frontend app is running at: http://localhost:5173")
    print("3. API documentation: http://127.0.0.1:8000/docs")
    print("4. Test the complete flow in the browser!")

if __name__ == "__main__":
    test_with_curl()