#!/usr/bin/env python3
"""
VALIS Memory Integration Test
Tests the actual working memory pipeline end-to-end
"""

import sys
from pathlib import Path

# Add VALIS root to path
sys.path.append(str(Path(__file__).parent))

try:
    from valis_inference_pipeline import VALISInferencePipeline
    print("SUCCESS: Successfully imported VALISInferencePipeline")
except ImportError as e:
    print(f"FAILED: Failed to import pipeline: {e}")
    sys.exit(1)

def test_memory_pipeline():
    """Test the complete memory-aware chat pipeline"""
    
    print("TESTING VALIS MEMORY PIPELINE")
    print("=" * 50)
    
    try:
        # Initialize pipeline
        pipeline = VALISInferencePipeline()
        print("SUCCESS: Pipeline initialized")
        
        # Test basic chat
        print("\\nTEST 1: Basic memory-aware chat")
        result1 = pipeline.run_memory_aware_chat(
            persona_id="marty",
            client_id="test_user",
            user_message="Hello! This is a test message."
        )
        
        print(f"Response: {result1['response'][:100]}...")
        print(f"Provider: {result1['provider']}")
        print(f"Memory used: {len(result1['memory_used'])} layers")
        
        # Test with canon tag
        print("\\nTEST 2: Canon memory tag")
        result2 = pipeline.run_memory_aware_chat(
            persona_id="marty", 
            client_id="test_user",
            user_message="Tell me something important to remember. #canon"
        )
        
        print(f"Tags processed: {result2['tags_processed']}")
        
        # Test with client fact tag
        print("\\nTEST 3: Client fact tag")
        result3 = pipeline.run_memory_aware_chat(
            persona_id="marty",
            client_id="test_user", 
            user_message="I prefer technical explanations. #client_fact"
        )
        
        print(f"Tags processed: {result3['tags_processed']}")
        
        # Test memory persistence
        print("\\nTEST 4: Memory persistence check")
        result4 = pipeline.run_memory_aware_chat(
            persona_id="marty",
            client_id="test_user",
            user_message="What do you remember about me?"
        )
        
        client_facts = result4['memory_used'].get('client_profile', {}).get('facts', {})
        print(f"Client facts in memory: {len(client_facts)}")
        if client_facts:
            print(f"Sample fact: {list(client_facts.values())[0]}")
        
        print("\\nSUCCESS: ALL TESTS COMPLETED")
        return True
        
    except Exception as e:
        print(f"FAILED: TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_memory_pipeline()
    sys.exit(0 if success else 1)
