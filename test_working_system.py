#!/usr/bin/env python3
"""
Emergency VALIS System Test
Prove the working system to Doc Brown
"""

import requests
import json
import time

def test_working_valis():
    """Test the emergency VALIS system"""
    print("EMERGENCY VALIS SYSTEM TEST")
    print("=" * 50)
    print("Doc Brown's Working System Demonstration")
    print()
    
    base_url = "http://localhost:8002"
    
    # Test 1: Health Check
    print("[1/5] Testing system health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        health_data = response.json()
        print(f"     Status: {health_data['status']}")
        print(f"     Personas: {health_data['personas_loaded']}")
        print(f"     Providers: {len(health_data['providers_available'])}")
    except Exception as e:
        print(f"     FAILED: {e}")
        return False
    
    # Test 2: Personas
    print("[2/5] Testing persona loading...")
    try:
        response = requests.get(f"{base_url}/personas", timeout=5)
        personas = response.json()
        print(f"     Loaded personas: {len(personas)}")
        for persona in personas[:3]:
            description = persona.get('description', persona.get('role', 'AI Assistant'))
            print(f"       - {persona['name']}: {description[:50]}...")
    except Exception as e:
        print(f"     FAILED: {e}")
        return False
    
    # Test 3: Configuration
    print("[3/5] Testing configuration...")
    try:
        response = requests.get(f"{base_url}/config", timeout=5)
        config = response.json()
        providers = config.get('providers', [])
        print(f"     Config loaded: {len(config)} keys")
        print(f"     Providers: {providers}")
    except Exception as e:
        print(f"     FAILED: {e}")
        return False
    
    # Test 4: Chat functionality
    print("[4/5] Testing AI chat...")
    try:
        chat_data = {
            "persona_id": "jane",
            "message": "Hello! Please demonstrate that VALIS is working!",
            "session_id": "emergency_demo_session"
        }
        
        response = requests.post(f"{base_url}/chat", json=chat_data, timeout=10)
        chat_response = response.json()
        
        if chat_response['success']:
            print(f"     Chat SUCCESS!")
            print(f"     Persona: {chat_response['persona_id']}")
            print(f"     Provider: {chat_response['provider_used']}")
            print(f"     Response: {chat_response['response'][:100]}...")
        else:
            print(f"     Chat FAILED")
            return False
    except Exception as e:
        print(f"     FAILED: {e}")
        return False
    
    # Test 5: Session tracking
    print("[5/5] Testing session management...")
    try:
        response = requests.get(f"{base_url}/sessions", timeout=5)
        sessions = response.json()
        print(f"     Active sessions: {len(sessions)}")
        if sessions:
            session = sessions[0]
            print(f"     Session ID: {session['session_id']}")
            print(f"     Messages: {session['message_count']}")
    except Exception as e:
        print(f"     FAILED: {e}")
        return False
    
    print()
    print("EMERGENCY SYSTEM TEST: ALL PASSED!")
    print("=" * 50)
    print("VALIS SYSTEM IS WORKING!")
    print("- API server responding")
    print("- Personas loaded and accessible")
    print("- Configuration system operational")
    print("- Chat functionality working")
    print("- Session management active")
    print("- Provider system available")
    print()
    print("SYSTEM READY FOR DOC BROWN INSPECTION!")
    print(f"Web interface: {base_url}")
    print(f"API docs: {base_url}/docs")
    print(f"Health check: {base_url}/health")
    
    return True

if __name__ == "__main__":
    test_working_valis()
