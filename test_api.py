#!/usr/bin/env python3
"""Quick API test for VALIS backend"""

import requests
import json

def test_health():
    try:
        r = requests.get("http://127.0.0.1:3001/api/health")
        print(f"Health endpoint: {r.status_code}")
        print(json.dumps(r.json(), indent=2))
        return True
    except Exception as e:
        print(f"Health test failed: {e}")
        return False

def test_personas():
    try:
        r = requests.get("http://127.0.0.1:3001/api/personas")
        print(f"\nPersonas endpoint: {r.status_code}")
        print(json.dumps(r.json(), indent=2))
        return True
    except Exception as e:
        print(f"Personas test failed: {e}")
        return False

def test_memory():
    try:
        r = requests.get("http://127.0.0.1:3001/api/memory/jane?client_id=test_client")
        print(f"\nMemory endpoint: {r.status_code}")
        data = r.json()
        print(f"Memory layers available: {len(data.get('layers', []))}")
        return True
    except Exception as e:
        print(f"Memory test failed: {e}")
        return False

def test_chat():
    try:
        payload = {
            "persona": "jane",
            "message": "Hello, can you confirm you have access to your memory?",
            "client_id": "test_client"
        }
        r = requests.post("http://127.0.0.1:3001/api/chat", json=payload)
        print(f"\nChat endpoint: {r.status_code}")
        data = r.json()
        print(f"Response: {data.get('response', 'No response')[:100]}...")
        return True
    except Exception as e:
        print(f"Chat test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing VALIS API endpoints...")
    
    tests = [test_health, test_personas, test_memory, test_chat]
    results = []
    
    for test in tests:
        results.append(test())
    
    print(f"\nTests completed: {sum(results)}/{len(results)} passed")
