import requests
import json

# Test if the user already exists
url = "http://127.0.0.1:8000/api/v1/auth/register"

# Try registering the same user from the screenshot
data = {
    "email": "ravi.mohan@example.com",  # Same as in screenshot
    "password": "password123",
    "first_name": "Ravi",
    "last_name": "Mohan",
    "role": "PATIENT"
}

print("Testing registration with user from screenshot...")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 400:
        print("⚠️  User already exists - this is expected!")
    elif response.status_code == 200:
        print("✅ Registration successful!")
    else:
        print("❌ Unexpected error!")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50)

# Try with a new unique email
import time
unique_email = f"test{int(time.time())}@example.com"

data2 = {
    "email": unique_email,
    "password": "password123",
    "first_name": "Test",
    "last_name": "User",
    "role": "PATIENT"
}

print(f"Testing registration with new email: {unique_email}")
try:
    response = requests.post(url, json=data2)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Registration successful with new email!")
    else:
        print("❌ Registration failed!")
        
except Exception as e:
    print(f"Error: {e}")