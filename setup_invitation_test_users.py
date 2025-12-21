"""
Setup test doctor and patient accounts for invitation system testing
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def create_doctor():
    """Create test doctor account"""
    print("Creating test doctor account...")
    
    doctor_data = {
        "email": "test_doctor@example.com",
        "password": "Doctor123!",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "role": "doctor",
        "specialization": "Neurology - Parkinson's Specialist",
        "license_number": "MD12345",
        "hospital_affiliation": "Parkinson Research Hospital"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=doctor_data)
        if response.status_code == 200:
            print("✓ Doctor account created successfully")
            print(f"  Email: {doctor_data['email']}")
            print(f"  Password: {doctor_data['password']}")
            return True
        elif response.status_code == 400 and "already registered" in response.text.lower():
            print("ℹ Doctor account already exists")
            print(f"  Email: {doctor_data['email']}")
            print(f"  Password: {doctor_data['password']}")
            return True
        else:
            print(f"✗ Failed to create doctor: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def create_patient():
    """Create test patient account"""
    print("\nCreating test patient account...")
    
    patient_data = {
        "email": "test_patient@example.com",
        "password": "Patient123!",
        "first_name": "John",
        "last_name": "Doe",
        "role": "patient",
        "age": 65,
        "gender": "male"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=patient_data)
        if response.status_code == 200:
            print("✓ Patient account created successfully")
            print(f"  Email: {patient_data['email']}")
            print(f"  Password: {patient_data['password']}")
            return True
        elif response.status_code == 400 and "already registered" in response.text.lower():
            print("ℹ Patient account already exists")
            print(f"  Email: {patient_data['email']}")
            print(f"  Password: {patient_data['password']}")
            return True
        else:
            print(f"✗ Failed to create patient: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def verify_login(email, password, user_type):
    """Verify account can login"""
    print(f"\nVerifying {user_type} login...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": email, "password": password}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✓ {user_type.capitalize()} login successful")
            print(f"  Token type: {token_data.get('token_type', 'N/A')}")
            return True
        else:
            print(f"✗ Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Login error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("INVITATION SYSTEM - TEST ACCOUNT SETUP")
    print("="*60)
    
    doctor_created = create_doctor()
    patient_created = create_patient()
    
    if doctor_created and patient_created:
        print("\n" + "="*60)
        print("VERIFYING ACCOUNTS")
        print("="*60)
        
        doctor_verified = verify_login("test_doctor@example.com", "Doctor123!", "doctor")
        patient_verified = verify_login("test_patient@example.com", "Patient123!", "patient")
        
        if doctor_verified and patient_verified:
            print("\n" + "="*60)
            print("✓ ALL ACCOUNTS READY!")
            print("="*60)
            print("\nYou can now run: python test_invitation_system.py")
            print("\nTest Credentials:")
            print("  Doctor: test_doctor@example.com / Doctor123!")
            print("  Patient: test_patient@example.com / Patient123!")
        else:
            print("\n✗ Account verification failed")
    else:
        print("\n✗ Failed to create test accounts")
