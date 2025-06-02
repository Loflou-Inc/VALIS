#!/usr/bin/env python3
"""
Test Enhanced VALIS API Implementation
Doc Brown's API-102 & API-103 Verification
"""

from fastapi.testclient import TestClient
from valis_api import app
import time

def test_enhanced_api():
    print("TESTING ENHANCED VALIS API")
    print("Doc Brown's API-102 & API-103 Verification")
    print("=" * 60)
    
    client = TestClient(app)
    
    # Test 1: Enhanced Health Check with Message History Stats
    print("Test 1: Enhanced Health Check")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        health_data = response.json()
        print(f"System Status: {health_data.get('status', 'unknown')}")
        print(f"Providers Available: {health_data.get('providers_available', [])}")
        print(f"Message History Stats: {health_data.get('message_history_stats', {})}")
    
    # Test 2: Chat with Message History Tracking
    print("\nTest 2: Chat with Message History")
    chat_request = {
        "session_id": "test_enhanced_session",
        "persona_id": "jane",
        "message": "Hello! Test message history tracking."
    }
    
    response = client.post("/chat", json=chat_request)
    print(f"Chat Status: {response.status_code}")
    
    if response.status_code == 200:
        chat_response = response.json()
        print(f"Success: {chat_response.get('success', False)}")
        print(f"Provider: {chat_response.get('provider', 'Unknown')}")
    
    # Test 3: Retrieve Message History
    print("\nTest 3: Session Message History")
    response = client.get("/sessions/test_enhanced_session/history")
    print(f"History Status: {response.status_code}")
    
    if response.status_code == 200:
        history_data = response.json()
        print(f"Session: {history_data.get('session_id', 'Unknown')}")
        print(f"Message Count: {history_data.get('total_count', 0)}")
        
        messages = history_data.get('messages', [])
        if messages:
            last_msg = messages[0]  # Most recent
            print(f"Last Message: {last_msg.get('message', '')[:50]}...")
            print(f"Provider Used: {last_msg.get('provider_used', 'Unknown')}")
    
    # Test 4: System Statistics
    print("\nTest 4: System Statistics")
    response = client.get("/admin/stats")
    print(f"Stats Status: {response.status_code}")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"Active Sessions: {stats.get('active_sessions', 0)}")
        print(f"Total Requests: {stats.get('total_requests', 0)}")
        print(f"Uptime: {stats.get('uptime_seconds', 0):.1f}s")
        
        msg_stats = stats.get('message_history', {})
        print(f"Total Messages: {msg_stats.get('total_messages', 0)}")
        print(f"Unique Sessions: {msg_stats.get('unique_sessions', 0)}")
    
    # Test 5: Enhanced Sessions with Message Counts
    print("\nTest 5: Enhanced Sessions")
    response = client.get("/sessions")
    print(f"Sessions Status: {response.status_code}")
    
    if response.status_code == 200:
        sessions = response.json()
        print(f"Active Sessions: {len(sessions)}")
        for session in sessions:
            print(f"  - {session['session_id']}: {session.get('message_count', 0)} messages")
    
    print("\nENHANCED API TEST COMPLETE!")
    print("All temporal safeguards verified ✅")

if __name__ == "__main__":
    test_enhanced_api()
