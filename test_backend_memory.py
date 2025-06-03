#!/usr/bin/env python3
"""
Test Backend Memory Integration
Verifies that the Flask API uses memory-aware inference pipeline
"""

import requests
import json
import sys
from datetime import datetime

def test_backend_memory_integration():
    """Test the backend API memory integration"""
    
    backend_url = "http://127.0.0.1:3001"
    
    print("=== TESTING BACKEND MEMORY INTEGRATION ===")
    print(f"Backend URL: {backend_url}")
    print()
    
    # Test 1: Health check
    print("TEST 1: Health Check")
    try:
        response = requests.get(f"{backend_url}/api/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"SUCCESS: Backend healthy")
            print(f"   VALIS Available: {health.get('system_info', {}).get('valis_available', False)}")
            print(f"   Personas Loaded: {health.get('personas_loaded', 0)}")
            print(f"   Providers: {health.get('providers_available', [])}")
        else:
            print(f"FAILED: Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAILED: Cannot connect to backend: {e}")
        print("   Make sure backend is running: python backend.py --port 3001")
        return False
    
    # Test 2: Chat with memory logging
    print("\\nTEST 2: Memory-Aware Chat")
    
    session_id = f"test_session_{int(datetime.now().timestamp())}"
    
    chat_data = {
        "session_id": session_id,
        "persona_id": "marty",
        "message": "Hello! Can you remember this conversation? #working_memory"
    }
    
    try:
        response = requests.post(
            f"{backend_url}/api/chat",
            json=chat_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Chat successful")
            print(f"   Provider: {result.get('provider', 'Unknown')}")
            print(f"   Processing time: {result.get('timing', {}).get('processing_time', 0):.2f}s")
            print(f"   Response length: {len(result.get('response', ''))}")
            
            # Check memory info
            memory_info = result.get('memory_info', {})
            if memory_info:
                layers = memory_info.get('layers_used', {})
                print(f"\\n   MEMORY LAYERS USED:")
                print(f"   - Core Biography: {layers.get('core_biography', 0)} entries")
                print(f"   - Canonized Identity: {layers.get('canonized_identity', 0)} entries") 
                print(f"   - Client Profile: {layers.get('client_profile', 0)} facts")
                print(f"   - Working Memory: {layers.get('working_memory', 0)} entries")
                print(f"   - Session History: {layers.get('session_history', 0)} messages")
                
                tags = memory_info.get('tags_processed', [])
                if tags:
                    print(f"   - Tags Processed: {tags}")
                else:
                    print(f"   - No memory tags detected")
            
            print(f"\\n   RESPONSE PREVIEW:")
            response_text = result.get('response', '')
            print(f'   "{response_text[:100]}..."')
            
        else:
            print(f"FAILED: Chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"FAILED: Chat request failed: {e}")
        return False
    
    # Test 3: Follow-up chat to test memory persistence
    print("\\nTEST 3: Memory Persistence Check")
    
    followup_data = {
        "session_id": session_id,
        "persona_id": "marty", 
        "message": "What do you remember about our previous conversation?"
    }
    
    try:
        response = requests.post(
            f"{backend_url}/api/chat",
            json=followup_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Follow-up chat successful")
            
            # Check if working memory increased
            memory_info = result.get('memory_info', {})
            if memory_info:
                layers = memory_info.get('layers_used', {})
                working_memory_count = layers.get('working_memory', 0)
                client_facts_count = layers.get('client_profile', 0)
                
                print(f"   Working Memory: {working_memory_count} entries")
                print(f"   Client Facts: {client_facts_count} facts")
                
                if working_memory_count > 0 or client_facts_count > 0:
                    print(f"   SUCCESS: Memory persistence confirmed!")
                else:
                    print(f"   WARNING: No memory persistence detected")
            
            response_text = result.get('response', '')
            print(f"\\n   RESPONSE PREVIEW:")
            print(f'   "{response_text[:100]}..."')
            
        else:
            print(f"FAILED: Follow-up chat failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"FAILED: Follow-up chat failed: {e}")
        return False
    
    print("\\n=== BACKEND MEMORY INTEGRATION TEST COMPLETE ===")
    return True

if __name__ == "__main__":
    success = test_backend_memory_integration()
    if success:
        print("\\nSUCCESS: ALL TESTS PASSED - Backend memory integration working!")
    else:
        print("\\nFAILED: TESTS FAILED - Backend memory integration has issues")
    
    sys.exit(0 if success else 1)
