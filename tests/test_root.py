#!/usr/bin/env python
"""Test the root endpoint"""
import time
import requests
import json

time.sleep(3)

try:
    response = requests.get('http://localhost:5000/')
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
