#!/usr/bin/env python3
import requests

base_url = "http://127.0.0.1:3001"

endpoints = [
    "/api/health",
    "/api/personas", 
    "/api/sessions"
]

for endpoint in endpoints:
    try:
        response = requests.get(f"{base_url}{endpoint}")
        print(f"{endpoint}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Content: {str(data)[:100]}...")
    except Exception as e:
        print(f"{endpoint}: ERROR - {e}")
