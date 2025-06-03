#!/usr/bin/env python3
import requests
import json

# Test chat endpoint with Jane
url = "http://127.0.0.1:3001/api/chat"
payload = {
    "message": "Hi Jane, how are you?",
    "persona_id": "jane",
    "session_id": "test_session_fix"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")
except Exception as e:
    print(f"Error: {e}")
