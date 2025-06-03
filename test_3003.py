import requests
r = requests.get("http://127.0.0.1:3003/api/health")
print(f"Health: {r.status_code} - {r.json()}")

r = requests.get("http://127.0.0.1:3003/")  
print(f"Root: {r.status_code}")
print(r.text[:200])
