import requests
r = requests.get("http://127.0.0.1:3002/")
print(f"Port 3002: {r.status_code} - {r.text}")
