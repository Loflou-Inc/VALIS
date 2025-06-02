#!/usr/bin/env python3
"""
Simple Sessions Test
"""

from fastapi.testclient import TestClient
from valis_api import app

def test_sessions_only():
    print("TESTING SESSIONS ENDPOINT ONLY")
    print("=" * 40)
    
    client = TestClient(app)
    
    # Test sessions endpoint
    response = client.get("/sessions")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        sessions = response.json()
        print(f"Sessions: {sessions}")
        print("SUCCESS")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_sessions_only()
