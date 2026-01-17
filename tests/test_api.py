"""
TuniMed API - Quick Testing Script
This script demonstrates how to test the API endpoints using Python requests.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def print_response(response, title=""):
    """Pretty print API response"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_api():
    """Run through a complete API workflow"""
    
    # 1. Health check
    print("\n1. Testing Health Check")
    resp = requests.get(f"{BASE_URL}/info/health")
    print_response(resp, "Health Check")
    
    # 2. Register a new user
    print("\n2. Register New User")
    register_data = {
        "username": "test_citizen",
        "email": "citizen@test.com",
        "password": "testpass123",
        "role": "CITIZEN"
    }
    resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print_response(resp, "Register User")
    
    # 3. Login
    print("\n3. Login")
    login_data = {
        "username": "test_citizen",
        "password": "testpass123"
    }
    resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response(resp, "Login")
    tokens = resp.json()
    access_token = tokens.get('access_token')
    
    # 4. Get current user info
    print("\n4. Get Current User Info")
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print_response(resp, "Get Current User")
    
    # 5. Declare a medicine
    print("\n5. Declare a Medicine")
    medicine_data = {
        "name": "Paracetamol 500mg",
        "amm": "13456789",
        "batch_number": "BATCH001",
        "expiration_date": "2025-12-31",
        "quantity": 20,
        "is_imported": False,
        "country_of_origin": None
    }
    resp = requests.post(f"{BASE_URL}/medicines/declarations", 
                        json=medicine_data, headers=headers)
    print_response(resp, "Declare Medicine")
    medicine_id = resp.json().get('medicine', {}).get('id') if resp.status_code == 201 else None
    
    # 6. Get my declarations
    print("\n6. Get My Declarations")
    resp = requests.get(f"{BASE_URL}/medicines/declarations/my", headers=headers)
    print_response(resp, "Get My Declarations")
    
    # 7. Check medicine eligibility
    if medicine_id:
        print(f"\n7. Check Medicine Eligibility (ID: {medicine_id})")
        resp = requests.get(f"{BASE_URL}/medicines/{medicine_id}/eligibility", headers=headers)
        print_response(resp, "Check Eligibility")
    
    # 8. Get import rules
    print("\n8. Get Import Rules")
    resp = requests.get(f"{BASE_URL}/info/import-rules")
    print_response(resp, "Import Rules")
    
    # 9. Get workflow statuses
    print("\n9. Get Workflow Statuses")
    resp = requests.get(f"{BASE_URL}/info/workflow-statuses")
    print_response(resp, "Workflow Statuses")
    
    # 10. Get error catalog
    print("\n10. Get Error Catalog")
    resp = requests.get(f"{BASE_URL}/info/error-catalog")
    print_response(resp, "Error Catalog")
    
    print("\n" + "="*60)
    print("  API Testing Complete!")
    print("="*60)

if __name__ == "__main__":
    print("TuniMed API - Test Script")
    print("Make sure the Flask app is running: python app.py")
    
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to API at", BASE_URL)
        print("Make sure to start the Flask app first: python app.py")
    except Exception as e:
        print(f"\nERROR: {str(e)}")
