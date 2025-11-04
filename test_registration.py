import requests
import json

# Test registration
url = "http://127.0.0.1:8000/api/v1/auth/register"
data = {
    "email": "ravi.mohan@example.com",
    "password": "securepassword123",
    "first_name": "Ravi",
    "last_name": "Mohan",
    "role": "PATIENT"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Registration successful!")
    else:
        print("❌ Registration failed!")
        
except Exception as e:
    print(f"Error: {e}")