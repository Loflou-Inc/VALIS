#!/usr/bin/env python3
import requests
import json

url = "http://127.0.0.1:3001/api/chat"
session_id = "stress_test_session"

messages = [
    "Hi Jane, I'm starting a new project",
    "The project involves workplace conflict resolution training",
    "What frameworks would you recommend for this?"
]

for i, message in enumerate(messages, 1):
    print(f"ROUND {i}: {message}")
    payload = {
        "message": message,
        "persona_id": "jane", 
        "session_id": session_id
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Memory layers: {data['memory_info']['layers_used']}")
            print(f"Response length: {len(data.get('response', ''))}")
        print()
    except Exception as e:
        print(f"ERROR: {e}")
        break
