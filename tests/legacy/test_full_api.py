#!/usr/bin/env python3
"""
Comprehensive VALIS API Test
"""

from fastapi.testclient import TestClient
from valis_api import app

def test_full_api():
    print("COMPREHENSIVE VALIS API TEST")
    print("=" * 50)
    
    client = TestClient(app)
    
    # Test 1: Health check
    print("Test 1: Health Check")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        health_data = response.json()
        print(f"System Status: {health_data.get('status', 'unknown')}")
        print(f"Providers Available: {health_data.get('providers_available', [])}")
    
    # Test 2: Get personas
    print("\nTest 2: Get Personas")
    response = client.get("/personas")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        personas = response.json()
        print(f"Personas loaded: {len(personas)}")
        for persona in personas[:2]:
            print(f"  - {persona['name']} ({persona['role']})")
    
    # Test 3: Chat endpoint
    print("\nTest 3: Chat Request")
    chat_request = {
        "session_id": "test_session_api",
        "persona_id": "jane",
        "message": "Hello, can you tell me about yourself?"
    }
    
    response = client.post("/chat", json=chat_request)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        chat_response = response.json()
        print(f"Success: {chat_response.get('success', False)}")
        print(f"Provider: {chat_response.get('provider', 'Unknown')}")
        if chat_response.get('response'):
            print(f"Response: {chat_response['response'][:100]}...")
    
    # Test 4: Get sessions
    print("\nTest 4: Active Sessions")
    response = client.get("/sessions")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        sessions = response.json()
        print(f"Active sessions: {len(sessions)}")
    
    print("\nFULL API TEST COMPLETE!")

if __name__ == "__main__":
    test_full_api()
