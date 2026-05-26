import requests
import json

url = "http://127.0.0.1:8000/api/v1/auth/register"
data = {
    "email": "rahulgosavi624@gmail.com",
    "password": "Rahul@123",
    "full_name": "Rahul Gosavi",
    "shop_name": "RG Super Mart"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error occurred: {e}")
