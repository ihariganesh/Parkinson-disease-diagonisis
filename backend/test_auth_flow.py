import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1/auth"

# Test registration
register_payload = {
    "email": "testuser@example.com",
    "password": "testpassword",
    "first_name": "Test",
    "last_name": "User",
    "role": "PATIENT"
}

with httpx.Client() as client:
    reg_resp = client.post(f"{BASE_URL}/register", json=register_payload)
    print("Register status:", reg_resp.status_code)
    print("Register response:", reg_resp.json())

    # Test login
    login_payload = {
        "username": "testuser@example.com",
        "password": "testpassword"
    }
    login_resp = client.post(f"{BASE_URL}/login", data=login_payload)
    print("Login status:", login_resp.status_code)
    print("Login response:", login_resp.json())
