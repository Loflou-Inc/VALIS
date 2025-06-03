import requests
try:
    r = requests.get("http://127.0.0.1:3001/api/health")
    print(f"API: {r.status_code}")
    print(r.text[:100])
except Exception as e:
    print(f"API failed: {e}")

try:
    r = requests.get("http://127.0.0.1:3001/")
    print(f"Frontend: {r.status_code}")
    print(r.text[:100])
except Exception as e:
    print(f"Frontend failed: {e}")
