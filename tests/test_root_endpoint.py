#!/usr/bin/env python
"""Test the root endpoint"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

print("[*] Testing app import and root endpoint...")

try:
    from app import app
    print("[OK] App imported successfully")
    
    # Create test client
    with app.test_client() as client:
        print("[*] Making GET request to /...")
        response = client.get('/')
        print("[OK] Got response with status: {}".format(response.status_code))
        print("[OK] Response data:")
        print(response.get_json())
        
        if response.status_code == 200:
            print("\n[SUCCESS] Root endpoint is working correctly!")
        else:
            print("\n[ERROR] Root endpoint returned unexpected status code")
            
except Exception as e:
    print("[ERROR] {}".format(e))
    import traceback
    traceback.print_exc()
