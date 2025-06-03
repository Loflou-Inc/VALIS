import requests

r = requests.get("http://127.0.0.1:3001/")
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")
