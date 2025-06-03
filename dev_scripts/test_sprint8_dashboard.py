#!/usr/bin/env python3
"""
Sprint 8 Dashboard Integration Test
Tests the dashboard API endpoints and functionality
"""

import requests
import json
import time

DASHBOARD_URL = "http://127.0.0.1:5001"

def test_dashboard_api():
    """Test all dashboard API endpoints"""
    
    print("*** Sprint 8 Dashboard API Test ***")
    print("=" * 40)
    print()
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   [PASS] Health check: {health['status']}")
            print(f"   Components: {health['components']}")
        else:
            print(f"   [FAIL] Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] Health check error: {e}")
    
    print()
    
    # Test personas endpoint
    print("2. Testing personas endpoint...")
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/personas")
        if response.status_code == 200:
            data = response.json()
            print(f"   [PASS] Found {data['count']} personas")
            for persona in data['personas'][:3]:  # Show first 3
                print(f"      - {persona['name']}: {persona['description'][:50]}...")
        else:
            print(f"   [FAIL] Personas failed: {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] Personas error: {e}")
    
    print()
    
    # Test chat endpoint
    print("3. Testing chat endpoint...")
    try:
        chat_data = {
            "message": "*** laika What should be our priority?",
            "user_id": "test_user",
            "persona_id": "jane"
        }
        
        response = requests.post(
            f"{DASHBOARD_URL}/api/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   [PASS] Chat successful")
            print(f"   Response: {result['response'][:100]}...")
            print(f"   Persona: {result['persona_name']}")
            print(f"   Targeting detected: {result['targeting_detected']}")
            print(f"   Provider: {result['provider']}")
        else:
            print(f"   [FAIL] Chat failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   [FAIL] Chat error: {e}")
    
    print()
    
    # Test memory endpoint
    print("4. Testing memory endpoint...")
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/memory/laika?user_id=test_user")
        if response.status_code == 200:
            data = response.json()
            print(f"   [PASS] Memory loaded for laika")
            print(f"   Stats: {data['memory_stats']}")
            print(f"   Memory layers: {len(data['memory_payload'])} total")
        else:
            print(f"   [FAIL] Memory failed: {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] Memory error: {e}")
    
    print()
    
    # Test diagnostics endpoint
    print("5. Testing diagnostics endpoint...")
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/diagnostics")
        if response.status_code == 200:
            data = response.json()
            print(f"   [PASS] Diagnostics loaded")
            print(f"   VALIS available: {data['system']['valis_available']}")
            print(f"   Personas: {data['personas']['available']}")
            print(f"   Active sessions: {data['sessions']['active_sessions']}")
        else:
            print(f"   [FAIL] Diagnostics failed: {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] Diagnostics error: {e}")
    
    print()
    print("*** Dashboard API Test Complete ***")
    print()
    print("Next steps:")
    print("1. Open http://127.0.0.1:5001 in your browser")
    print("2. Select a persona from the dropdown")
    print("3. Try messaging: *** laika What's our priority?")
    print("4. Check memory panel for live updates")
    print("5. Use debug tools for memory snapshots")

if __name__ == "__main__":
    print("Waiting 2 seconds for dashboard to fully start...")
    time.sleep(2)
    test_dashboard_api()
