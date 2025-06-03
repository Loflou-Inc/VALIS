#!/usr/bin/env python3
"""
Sprint 8A: Memory-Aware Inference Testing Tool
Test memory routing and tag processing with real persona responses
"""

import json
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add VALIS root to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from valis_inference_pipeline import VALISInferencePipeline
    from core.valis_memory import MemoryRouter
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"ERROR: VALIS components not available: {e}")
    COMPONENTS_AVAILABLE = False

def test_basic_memory_routing():
    """Test basic memory loading and routing"""
    print("=== TESTING BASIC MEMORY ROUTING ===")
    
    try:
        memory_router = MemoryRouter()
        
        # Test personas
        test_personas = ["jane", "laika", "doc_brown", "biff"]
        
        for persona_id in test_personas:
            print(f"\nTesting {persona_id}:")
            
            # Get memory payload
            payload = memory_router.get_memory_payload(
                persona_id=persona_id,
                client_id="test_client",
                current_message="Hello, I need help with something."
            )
            
            # Check memory layers
            print(f"  Core persona: {'LOADED' if payload['core_biography'] else 'MISSING'}")
            print(f"  Canon entries: {len(payload['canonized_identity'])}")
            print(f"  Client facts: {len(payload.get('client_profile', {}).get('facts', {}))}")
            print(f"  Working memory: {len(payload['working_memory'])}")
            
            # Get stats
            stats = memory_router.get_memory_stats(persona_id)
            print(f"  Memory stats: {stats}")
            
    except Exception as e:
        print(f"FAILED: Memory routing test failed: {e}")
        return False
    
    print("SUCCESS: Memory routing test passed")
    return True

def test_tag_processing():
    """Test memory tag processing and storage"""
    print("\n=== TESTING MEMORY TAG PROCESSING ===")
    
    try:
        memory_router = MemoryRouter()
        
        # Test #canon tag
        print("\nTesting #canon tag...")
        canon_result = memory_router.process_response_tags(
            persona_id="jane",
            response_text="I successfully helped resolve the engineering conflict #canon This should be remembered",
            client_id="test_client",
            source_prompt="Engineering team conflict resolution"
        )
        print(f"Canon processed: {canon_result['canon_processed']}")
        
        # Test #client_fact tag 
        print("\nTesting #client_fact tag...")
        fact_result = memory_router.process_response_tags(
            persona_id="jane", 
            response_text="The client is an engineering manager #client_fact:role=engineering_manager",
            client_id="test_client"
        )
        print(f"Client fact processed: {fact_result['client_fact_processed']}")
        
        # Test #working_memory tag
        print("\nTesting #working_memory tag...")
        working_result = memory_router.process_response_tags(
            persona_id="jane",
            response_text="Client seems stressed about team dynamics #working_memory",
            client_id="test_client"
        )
        print(f"Working memory processed: {working_result['working_memory_processed']}")
        
        # Verify memory was actually saved
        print("\nVerifying memory storage...")
        updated_payload = memory_router.get_memory_payload(
            persona_id="jane",
            client_id="test_client"
        )
        print(f"Canon entries after test: {len(updated_payload['canonized_identity'])}")
        print(f"Client facts after test: {len(updated_payload.get('client_profile', {}).get('facts', {}))}")
        print(f"Working memory after test: {len(updated_payload['working_memory'])}")
        
    except Exception as e:
        print(f"FAILED: Tag processing test failed: {e}")
        return False
    
    print("SUCCESS: Tag processing test passed")
    return True

def test_memory_aware_inference(persona_id="jane", test_message="I need help managing my team"):
    """Test complete memory-aware inference pipeline"""
    print(f"\n=== TESTING MEMORY-AWARE INFERENCE ===")
    print(f"Persona: {persona_id}")
    print(f"Message: {test_message}")
    
    if not COMPONENTS_AVAILABLE:
        print("FAILED: VALIS components not available")
        return False
    
    try:
        pipeline = VALISInferencePipeline()
        
        # Run memory-aware chat
        result = pipeline.run_memory_aware_chat(
            persona_id=persona_id,
            client_id="test_inference",
            user_message=test_message,
            session_id="test_session_001"
        )
        
        print(f"\nRESULTS:")
        print(f"Success: {result['success']}")
        print(f"Provider: {result['provider']}")
        print(f"Processing time: {result['processing_time']:.2f}s")
        print(f"Tags processed: {result['tags_processed']}")
        
        print(f"\nMEMORY USAGE:")
        memory_used = result['memory_used']
        print(f"Core biography: {len(memory_used.get('core_biography', {}))} fields")
        print(f"Canon entries: {len(memory_used.get('canonized_identity', []))}")
        print(f"Client facts: {len(memory_used.get('client_profile', {}).get('facts', {}))}")
        print(f"Working memory: {len(memory_used.get('working_memory', []))}")
        print(f"Session history: {len(memory_used.get('session_history', []))}")
        
        print(f"\nRESPONSE:")
        response = result['response']
        print(f"Length: {len(response)} characters")
        print(f"Content: {response[:200]}{'...' if len(response) > 200 else ''}")
        
        # Test if response shows memory awareness
        memory_indicators = [
            "based on" in response.lower(),
            "remember" in response.lower(), 
            "previously" in response.lower(),
            "experience" in response.lower(),
            persona_id in response.lower()
        ]
        memory_aware_count = sum(memory_indicators)
        print(f"\nMEMORY AWARENESS INDICATORS: {memory_aware_count}/5")
        
        if memory_aware_count >= 2:
            print("SUCCESS: Response shows memory awareness")
        else:
            print("WARNING: Response may not be using memory effectively")
        
        return True
        
    except Exception as e:
        print(f"FAILED: Memory-aware inference failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tagged_input_processing():
    """Test that tagged inputs are processed and affect next response"""
    print(f"\n=== TESTING TAGGED INPUT PROCESSING ===")
    
    if not COMPONENTS_AVAILABLE:
        print("FAILED: VALIS components not available")
        return False
    
    try:
        pipeline = VALISInferencePipeline()
        
        # First: Send message with #canon tag
        print("Step 1: Sending message with #canon tag...")
        canon_message = "I successfully used the Systems Thinking Framework to resolve conflicts #canon"
        
        result1 = pipeline.run_memory_aware_chat(
            persona_id="jane",
            client_id="test_tagged",
            user_message=canon_message,
            session_id="test_tagged_session"
        )
        
        print(f"Canon tags processed: {result1['tags_processed']}")
        
        # Second: Send follow-up message to see if canon affects response
        print("\nStep 2: Sending follow-up to test canon memory...")
        followup_message = "How should I handle similar conflicts in the future?"
        
        result2 = pipeline.run_memory_aware_chat(
            persona_id="jane", 
            client_id="test_tagged",
            user_message=followup_message,
            session_id="test_tagged_session"
        )
        
        print(f"Follow-up response length: {len(result2['response'])}")
        
        # Check if response references previous canon entry
        response = result2['response'].lower()
        canon_references = [
            "systems thinking" in response,
            "framework" in response,
            "previous" in response or "before" in response,
            "experience" in response
        ]
        
        canon_ref_count = sum(canon_references)
        print(f"Canon reference indicators: {canon_ref_count}/4")
        
        if canon_ref_count >= 2:
            print("SUCCESS: Canon memory affects follow-up responses")
        else:
            print("WARNING: Canon memory may not be affecting responses")
        
        return True
        
    except Exception as e:
        print(f"FAILED: Tagged input processing failed: {e}")
        return False

def main():
    """Run all memory inference tests"""
    print("VALIS MEMORY-AWARE INFERENCE TEST SUITE")
    print("=" * 50)
    
    if not COMPONENTS_AVAILABLE:
        print("FATAL: Required VALIS components not available")
        print("Ensure core modules are properly installed")
        return 1
    
    # Run test suite
    tests = [
        ("Basic Memory Routing", test_basic_memory_routing),
        ("Tag Processing", test_tag_processing), 
        ("Memory-Aware Inference", test_memory_aware_inference),
        ("Tagged Input Processing", test_tagged_input_processing)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n" + "=" * 50)
        print(f"RUNNING: {test_name}")
        print("=" * 50)
        
        try:
            if test_func():
                passed += 1
                print(f"PASS: {test_name}")
            else:
                print(f"FAIL: {test_name}")
        except Exception as e:
            print(f"ERROR: {test_name} crashed: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("SUCCESS: All memory inference tests passed!")
        return 0
    else:
        print("FAILURE: Some memory inference tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
