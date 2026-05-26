import requests
import json

url = "http://localhost:8000/api/v1/auth/register"
data = {
    "email": "test_auto_login@example.com",
    "password": "password123",
    "full_name": "Test Auto Login",
    "shop_name": "Test Shop"
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
