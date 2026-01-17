import time
import requests
import json

print("\nWaiting for server to be ready...")
time.sleep(2)

try:
    print("Testing root endpoint at http://127.0.0.1:5000/")
    response = requests.get('http://127.0.0.1:5000/', timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
