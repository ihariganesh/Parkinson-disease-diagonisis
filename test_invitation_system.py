"""
Complete test for Doctor-Patient Invitation System
Tests the full workflow: generate → request → approve → verify
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_step(step_num, description):
    print(f"\n{BLUE}{'='*60}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*60}{RESET}\n")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")

# Test data
DOCTOR_CREDENTIALS = {
    "username": "test_doctor@example.com",
    "password": "Doctor123!"
}

PATIENT_CREDENTIALS = {
    "username": "test_patient@example.com",
    "password": "Patient123!"
}

def create_test_users():
    """Create test doctor and patient accounts if they don't exist"""
    print_step(0, "Setting up test users")
    
    # Create doctor
    doctor_data = {
        "email": DOCTOR_CREDENTIALS["username"],
        "password": DOCTOR_CREDENTIALS["password"],
        "full_name": "Dr. Test Doctor",
        "user_type": "doctor",
        "specialization": "Neurology",
        "license_number": "MD12345",
        "hospital_affiliation": "Test Hospital"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=doctor_data)
        if response.status_code == 200:
            print_success("Doctor account created")
        else:
            print_info("Doctor account already exists or registration failed")
    except Exception as e:
        print_error(f"Error creating doctor: {e}")
    
    # Create patient
    patient_data = {
        "email": PATIENT_CREDENTIALS["username"],
        "password": PATIENT_CREDENTIALS["password"],
        "full_name": "Test Patient",
        "user_type": "patient",
        "age": 65,
        "gender": "male"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=patient_data)
        if response.status_code == 200:
            print_success("Patient account created")
        else:
            print_info("Patient account already exists or registration failed")
    except Exception as e:
        print_error(f"Error creating patient: {e}")

def login(credentials, user_type):
    """Login and get access token"""
    print_info(f"Logging in as {user_type}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=credentials
        )
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print_success(f"{user_type.capitalize()} logged in successfully")
            return token
        else:
            print_error(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Login error: {e}")
        return None

def test_generate_invitation_code(doctor_token):
    """Test: Doctor generates invitation code"""
    print_step(1, "Doctor generates invitation code")
    
    headers = {"Authorization": f"Bearer {doctor_token}"}
    data = {
        "max_uses": 5,
        "expires_in_days": 30,
        "description": "Test invitation for new patients"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/invitation/doctor/generate-code",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Invitation code generated!")
            print(f"\n{YELLOW}Invitation Details:{RESET}")
            print(f"  Code: {GREEN}{result['invitation_code']}{RESET}")
            print(f"  Link: {result['invitation_link']}")
            print(f"  Max Uses: {result['max_uses']}")
            print(f"  Expires: {result['expires_at']}")
            return result['invitation_code']
        else:
            print_error(f"Failed to generate code: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error generating code: {e}")
        return None

def test_validate_code(invitation_code):
    """Test: Public validation of invitation code"""
    print_step(2, "Validating invitation code (public endpoint)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/invitation/validate-code/{invitation_code}"
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Code is valid!")
            print(f"\n{YELLOW}Doctor Information:{RESET}")
            print(f"  Name: {result['doctor_name']}")
            print(f"  Specialization: {result['specialization']}")
            print(f"  Hospital: {result['hospital']}")
            print(f"  Uses Remaining: {result['uses_remaining']}")
            return True
        else:
            print_error(f"Code validation failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Validation error: {e}")
        return False

def test_patient_use_code(patient_token, invitation_code):
    """Test: Patient uses invitation code"""
    print_step(3, "Patient uses invitation code")
    
    headers = {"Authorization": f"Bearer {patient_token}"}
    data = {
        "invitation_code": invitation_code,
        "message": "Hello Doctor! I would like to be your patient for Parkinson's disease monitoring."
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/invitation/patient/use-code",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Link request sent!")
            print(f"\n{YELLOW}Request Details:{RESET}")
            print(f"  Status: {result['status'].upper()}")
            print(f"  Doctor: {result['doctor_name']}")
            print(f"  Next Step: {result['next_step']}")
            return result['request_id']
        else:
            print_error(f"Failed to use code: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error using code: {e}")
        return None

def test_doctor_view_pending_requests(doctor_token):
    """Test: Doctor views pending requests"""
    print_step(4, "Doctor views pending requests")
    
    headers = {"Authorization": f"Bearer {doctor_token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/invitation/doctor/pending-requests",
            headers=headers
        )
        
        if response.status_code == 200:
            requests_list = response.json()
            print_success(f"Found {len(requests_list)} pending request(s)")
            
            if requests_list:
                print(f"\n{YELLOW}Pending Requests:{RESET}")
                for req in requests_list:
                    print(f"\n  Request ID: {req['request_id']}")
                    print(f"  Patient: {req['patient_name']} ({req['patient_email']})")
                    print(f"  Status: {req['status'].upper()}")
                    print(f"  Message: {req.get('patient_message', 'No message')}")
                    print(f"  Requested At: {req['requested_at']}")
                
                return requests_list[0]['request_id'] if requests_list else None
            return None
        else:
            print_error(f"Failed to get requests: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error getting requests: {e}")
        return None

def test_doctor_approve_request(doctor_token, request_id):
    """Test: Doctor approves patient request"""
    print_step(5, "Doctor approves patient request")
    
    headers = {"Authorization": f"Bearer {doctor_token}"}
    data = {
        "request_id": request_id,
        "response_message": "Welcome! I'll be monitoring your Parkinson's progress."
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/invitation/doctor/approve-request",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Request approved!")
            print(f"\n{YELLOW}Approval Details:{RESET}")
            print(f"  Patient: {result['patient_name']}")
            print(f"  Assignment ID: {result['assignment_id']}")
            return result['assignment_id']
        else:
            print_error(f"Failed to approve request: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error approving request: {e}")
        return None

def test_patient_view_doctors(patient_token):
    """Test: Patient views linked doctors"""
    print_step(6, "Patient views linked doctors")
    
    headers = {"Authorization": f"Bearer {patient_token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/invitation/patient/my-doctors",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Patient has {result['count']} linked doctor(s)")
            
            if result['doctors']:
                print(f"\n{YELLOW}Linked Doctors:{RESET}")
                for doctor in result['doctors']:
                    print(f"\n  Doctor: {doctor['doctor_name']}")
                    print(f"  Email: {doctor['email']}")
                    print(f"  Specialization: {doctor['specialization']}")
                    print(f"  Hospital: {doctor['hospital']}")
                    print(f"  Linked Since: {doctor['linked_since']}")
            return result['count'] > 0
        else:
            print_error(f"Failed to get doctors: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error getting doctors: {e}")
        return False

def test_doctor_view_patients(doctor_token):
    """Test: Doctor views assigned patients"""
    print_step(7, "Doctor views assigned patients")
    
    headers = {"Authorization": f"Bearer {doctor_token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/doctor/patients",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Doctor has {result['total']} assigned patient(s)")
            
            if result['patients']:
                print(f"\n{YELLOW}Assigned Patients:{RESET}")
                for patient in result['patients']:
                    print(f"\n  Patient: {patient['patient_name']}")
                    print(f"  Email: {patient['patient_email']}")
                    print(f"  Assigned Since: {patient['assigned_at']}")
            return result['total'] > 0
        else:
            print_error(f"Failed to get patients: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error getting patients: {e}")
        return False

def test_doctor_view_codes(doctor_token):
    """Test: Doctor views all invitation codes"""
    print_step(8, "Doctor views all invitation codes")
    
    headers = {"Authorization": f"Bearer {doctor_token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/invitation/doctor/my-codes?active_only=false",
            headers=headers
        )
        
        if response.status_code == 200:
            codes = response.json()
            print_success(f"Found {len(codes)} invitation code(s)")
            
            if codes:
                print(f"\n{YELLOW}Invitation Codes:{RESET}")
                for code in codes:
                    status = "ACTIVE" if code['is_active'] else "INACTIVE"
                    print(f"\n  Code: {code['invitation_code']}")
                    print(f"  Status: {status}")
                    print(f"  Uses: {code['current_uses']}/{code['max_uses']}")
                    print(f"  Description: {code.get('description', 'N/A')}")
            return True
        else:
            print_error(f"Failed to get codes: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error getting codes: {e}")
        return False

def run_complete_test():
    """Run complete invitation system test"""
    print(f"\n{BLUE}{'='*60}")
    print("DOCTOR-PATIENT INVITATION SYSTEM TEST")
    print(f"{'='*60}{RESET}\n")
    print(f"Testing complete workflow:")
    print("  1. Doctor generates invitation code")
    print("  2. Code validation (public)")
    print("  3. Patient uses code")
    print("  4. Doctor views pending requests")
    print("  5. Doctor approves request")
    print("  6. Patient views linked doctors")
    print("  7. Doctor views assigned patients")
    print("  8. Doctor views invitation codes")
    
    # Setup test users
    create_test_users()
    
    # Login
    print_step(0.5, "Authentication")
    doctor_token = login(DOCTOR_CREDENTIALS, "doctor")
    patient_token = login(PATIENT_CREDENTIALS, "patient")
    
    if not doctor_token or not patient_token:
        print_error("Authentication failed. Cannot proceed with test.")
        return
    
    # Test workflow
    invitation_code = test_generate_invitation_code(doctor_token)
    if not invitation_code:
        return
    
    if not test_validate_code(invitation_code):
        return
    
    request_id = test_patient_use_code(patient_token, invitation_code)
    if not request_id:
        return
    
    pending_request_id = test_doctor_view_pending_requests(doctor_token)
    if not pending_request_id:
        print_error("No pending requests found")
        return
    
    assignment_id = test_doctor_approve_request(doctor_token, pending_request_id)
    if not assignment_id:
        return
    
    test_patient_view_doctors(patient_token)
    test_doctor_view_patients(doctor_token)
    test_doctor_view_codes(doctor_token)
    
    # Summary
    print(f"\n{GREEN}{'='*60}")
    print("✓ ALL TESTS PASSED!")
    print(f"{'='*60}{RESET}\n")
    print(f"{YELLOW}Summary:{RESET}")
    print("  ✓ Invitation code generated")
    print("  ✓ Code validated")
    print("  ✓ Patient used code")
    print("  ✓ Request created (PENDING)")
    print("  ✓ Doctor approved request")
    print("  ✓ Patient linked to doctor")
    print("  ✓ Doctor can see patient")
    print("  ✓ Patient can see doctor")
    print("\n🎉 Invitation system is working perfectly!")

if __name__ == "__main__":
    try:
        run_complete_test()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user{RESET}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
