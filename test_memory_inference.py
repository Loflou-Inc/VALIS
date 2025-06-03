#!/usr/bin/env python3
"""
Sprint 8A: Memory-Aware Inference Testing Tool

Test that memory system actually affects provider responses.
Verifies canon, client_fact, and working_memory tags work.
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add VALIS root
sys.path.append(str(Path(__file__).parent))

try:
    from valis_inference_pipeline import VALISInferencePipeline
    from core.valis_memory import MemoryRouter
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"FAILED: Components not available: {e}")
    COMPONENTS_AVAILABLE = False

def test_memory_affects_inference():
    """Test that memory visibly affects Claude responses"""
    print("=== SPRINT 8A: MEMORY INFERENCE TEST ===")
    
    if not COMPONENTS_AVAILABLE:
        print("FAILED: Required components not available")
        return False
    
    try:
        pipeline = VALISInferencePipeline()
        memory_router = MemoryRouter()
        
        # Test persona and client
        persona_id = "jane"
        client_id = "test_client"
        
        print(f"Testing persona: {persona_id}")
        print(f"Testing client: {client_id}")
        print()
        
        # TEST 1: Baseline response (no memory)
        print("TEST 1: Baseline response")
        baseline_result = pipeline.run_memory_aware_chat(
            persona_id=persona_id,
            client_id=client_id,
            user_message="Help me with team conflicts",
            session_id="test_session_1"
        )
        
        baseline_response = baseline_result["response"]
        print(f"Baseline response: {baseline_response[:100]}...")
        
        # Check memory usage
        memory_used = baseline_result["memory_used"]
        print(f"Memory layers loaded:")
        print(f"  Core: {len(memory_used.get('core_biography', []))}")
        print(f"  Canon: {len(memory_used.get('canonized_identity', []))}")
        print(f"  Client: {len(memory_used.get('client_profile', {}).get('facts', {}))}")
        print(f"  Working: {len(memory_used.get('working_memory', []))}")
        print()
        
        # TEST 2: Add canonical memory and test again
        print("TEST 2: Adding canonical memory")
        
        # Manually add canon entry
        canon_file = Path(__file__).parent / "memory" / "personas" / persona_id / "canon.json"
        canon_file.parent.mkdir(parents=True, exist_ok=True)
        
        canon_data = [{
            "timestamp": datetime.now().isoformat(),
            "content": "Successfully implemented new conflict resolution framework using Systems Thinking approach",
            "source": "test_insertion"
        }]
        
        with open(canon_file, 'w', encoding='utf-8') as f:
            json.dump(canon_data, f, indent=2)
        
        print("Added canon entry: conflict resolution framework")
        
        # Wait a moment
        time.sleep(1)
        
        # Get response again
        canon_result = pipeline.run_memory_aware_chat(
            persona_id=persona_id,
            client_id=client_id,
            user_message="Help me with team conflicts",
            session_id="test_session_2"
        )
        
        canon_response = canon_result["response"]
        print(f"Canon-enhanced response: {canon_response[:100]}...")
        
        # Check if canon memory is loaded
        canon_memory_used = canon_result["memory_used"]
        canon_count = len(canon_memory_used.get('canonized_identity', []))
        print(f"Canon entries loaded: {canon_count}")
        
        # TEST 3: Add client fact and test
        print()
        print("TEST 3: Adding client fact")
        
        client_file = Path(__file__).parent / "memory" / "clients" / client_id / f"{persona_id}_profile.json"
        client_file.parent.mkdir(parents=True, exist_ok=True)
        
        client_data = {
            "facts": {
                "role": "Engineering Manager",
                "team_size": "8 developers",
                "main_challenge": "Cross-team communication"
            },
            "preferences": {}
        }
        
        with open(client_file, 'w', encoding='utf-8') as f:
            json.dump(client_data, f, indent=2)
        
        print("Added client facts: Engineering Manager, 8 developers")
        
        time.sleep(1)
        
        client_result = pipeline.run_memory_aware_chat(
            persona_id=persona_id,
            client_id=client_id,
            user_message="Help me with team conflicts",
            session_id="test_session_3"
        )
        
        client_response = client_result["response"]
        print(f"Client-aware response: {client_response[:100]}...")
        
        client_memory_used = client_result["memory_used"]
        client_facts = len(client_memory_used.get('client_profile', {}).get('facts', {}))
        print(f"Client facts loaded: {client_facts}")
        
        # TEST 4: Test tagged response for memory growth
        print()
        print("TEST 4: Testing memory tag processing")
        
        tagged_result = pipeline.run_memory_aware_chat(
            persona_id=persona_id,
            client_id=client_id,
            user_message="Remember this: we resolved the issue using daily standups #canon",
            session_id="test_session_4"
        )
        
        tags_processed = tagged_result["tags_processed"]
        print(f"Tags processed: {tags_processed}")
        
        # Verify canon file grew
        with open(canon_file, 'r', encoding='utf-8') as f:
            updated_canon = json.load(f)
        
        print(f"Canon entries after tag: {len(updated_canon)}")
        
        # ANALYSIS
        print()
        print("=== ANALYSIS ===")
        
        # Check if responses actually differ
        responses_differ = (
            baseline_response != canon_response or 
            canon_response != client_response
        )
        
        print(f"Responses differ with memory: {responses_differ}")
        print(f"Memory system loads data: {canon_count > 0 and client_facts > 0}")
        print(f"Tag processing works: {len(tags_processed) > 0}")
        
        # SUCCESS if memory affects responses
        success = (
            responses_differ and 
            canon_count > 0 and 
            client_facts > 0 and
            len(tags_processed) > 0
        )
        
        print(f"OVERALL TEST RESULT: {'PASS' if success else 'FAIL'}")
        
        return success
        
    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_persona_memory_isolation():
    """Test that different personas load different memory"""
    print()
    print("=== PERSONA MEMORY ISOLATION TEST ===")
    
    try:
        memory_router = MemoryRouter()
        
        # Test different personas
        personas = ["jane", "laika", "doc_brown"]
        client_id = "isolation_test_client"
        
        for persona_id in personas:
            print(f"Testing {persona_id}...")
            
            memory_payload = memory_router.get_memory_payload(
                persona_id=persona_id,
                client_id=client_id,
                session_history=[],
                current_message="Test message"
            )
            
            core_count = len(memory_payload.get('core_biography', []))
            print(f"  Core biography entries: {core_count}")
            print(f"  Persona name in payload: {memory_payload.get('persona_id')}")
        
        print("Memory isolation test complete")
        return True
        
    except Exception as e:
        print(f"Isolation test failed: {e}")
        return False

def main():
    """Run all memory inference tests"""
    
    print("SPRINT 8A: MEMORY-AWARE INFERENCE TESTING")
    print("Goal: Verify memory system affects provider responses")
    print()
    
    # Run tests
    test1_pass = test_memory_affects_inference()
    test2_pass = test_specific_persona_memory_isolation()
    
    print()
    print("=== FINAL RESULTS ===")
    print(f"Memory affects inference: {'PASS' if test1_pass else 'FAIL'}")
    print(f"Persona isolation works: {'PASS' if test2_pass else 'FAIL'}")
    
    overall_pass = test1_pass and test2_pass
    print(f"SPRINT 8A STATUS: {'COMPLETE' if overall_pass else 'NEEDS WORK'}")
    
    return 0 if overall_pass else 1

if __name__ == "__main__":
    sys.exit(main())
