#!/usr/bin/env python3
"""
Test Sessions After Chat
"""

from fastapi.testclient import TestClient
from valis_api import app

def test_sessions_after_chat():
    print("TESTING SESSIONS AFTER CHAT")
    print("=" * 40)
    
    client = TestClient(app)
    
    # First make a chat request to create a session
    print("Step 1: Making chat request...")
    chat_request = {
        "session_id": "test_session_api",
        "persona_id": "jane",
        "message": "Hello!"
    }
    
    response = client.post("/chat", json=chat_request)
    print(f"Chat Status: {response.status_code}")
    
    # Now test sessions endpoint
    print("\nStep 2: Getting sessions...")
    response = client.get("/sessions")
    print(f"Sessions Status: {response.status_code}")
    
    if response.status_code == 200:
        sessions = response.json()
        print(f"Sessions: {sessions}")
        print("SUCCESS")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_sessions_after_chat()
