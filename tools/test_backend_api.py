#!/usr/bin/env python3
"""Test memory-aware backend API"""

import json
import requests
import uuid

def test_backend_memory_chat():
    """Test the backend /api/chat endpoint with memory awareness"""
    
    # Test data
    session_id = str(uuid.uuid4())
    
    test_data = {
        "session_id": session_id,
        "persona_id": "jane",
        "message": "I need help with team conflicts. #client_fact The team is an engineering team",
        "context": {}
    }
    
    print("Testing memory-aware chat API...")
    print(f"Session: {session_id}")
    print(f"Message: {test_data['message']}")
    
    # Send request
    response = requests.post(
        "http://127.0.0.1:3001/api/chat",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nSUCCESS:")
        print(f"Provider: {result.get('provider')}")
        print(f"Response length: {len(result.get('response', ''))}")
        print(f"Memory layers used: {result.get('memory_info', {}).get('layers_used', {})}")
        print(f"Tags processed: {result.get('memory_info', {}).get('tags_processed', [])}")
        print(f"Processing time: {result.get('timing', {}).get('processing_time', 0):.2f}s")
        
        # Test follow-up with memory
        test_data2 = {
            "session_id": session_id,
            "persona_id": "jane", 
            "message": "What specific strategies would you recommend?",
            "context": {}
        }
        
        print(f"\nTesting follow-up...")
        response2 = requests.post(
            "http://127.0.0.1:3001/api/chat",
            json=test_data2,
            headers={"Content-Type": "application/json"}
        )
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"Follow-up response length: {len(result2.get('response', ''))}")
            print(f"Memory layers used: {result2.get('memory_info', {}).get('layers_used', {})}")
            return True
        else:
            print(f"Follow-up failed: {response2.status_code}")
            return False
    else:
        print(f"FAILED: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    test_backend_memory_chat()
