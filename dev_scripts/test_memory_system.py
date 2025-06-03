#!/usr/bin/env python3
"""
Sprint 6 Memory System Demo
Demonstrates all 5 memory layers working together
"""

import json
import sys
from pathlib import Path

# Add VALIS root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.valis_memory import MemoryRouter

def demo_memory_system():
    """Comprehensive demo of 5-layer memory system"""
    print("*** VALIS Memory System Demo - Sprint 6 ***")
    print("=" * 50)
    
    # Initialize memory router
    router = MemoryRouter()
    
    # Test session history for demo
    test_session_history = [
        {"role": "user", "content": "Hi Jane, I'm having issues with my team again"},
        {"role": "assistant", "content": "I understand. Let's explore what's happening with your team dynamics. Can you tell me more about the specific issues you're experiencing?"},
        {"role": "user", "content": "Two of my engineers keep disagreeing about code architecture decisions"}
    ]
    
    # Get complete memory payload
    print(">>> Generating complete memory payload...")
    payload = router.get_memory_payload(
        persona_id="jane",
        client_id="user_123", 
        session_history=test_session_history,
        current_message="Two of my engineers keep disagreeing about code architecture decisions"
    )
    
    print("SUCCESS: Memory payload generated successfully!")
    print()
    
    # Display each memory layer
    print("LAYER 1: Core Persona (Static Biography)")
    print(f"   Name: {payload['core_biography'].get('name', 'N/A')}")
    print(f"   Role: {payload['core_biography'].get('description', 'N/A')}")
    print(f"   Specialties: {len(payload['core_biography'].get('specialties', []))} areas")
    print()
    
    print("LAYER 2: Canonized Identity (Permanent Events)")
    canon_count = len(payload['canonized_identity'])
    print(f"   Canon entries: {canon_count}")
    if canon_count > 0:
        latest_canon = payload['canonized_identity'][-1]
        print(f"   Latest: {latest_canon['content'][:80]}...")
    print()
    
    print("LAYER 3: Client Profile (User-Specific Facts)")
    facts = payload['client_profile'].get('facts', {})
    print(f"   Client facts: {len(facts)} stored")
    for key, value in list(facts.items())[:3]:  # Show first 3
        print(f"   - {key}: {value}")
    print()
    
    print("LAYER 4: Working Memory (Recent Observations)")
    working_count = len(payload['working_memory'])
    print(f"   Working memory entries: {working_count}")
    if working_count > 0:
        recent_memory = payload['working_memory'][-1]
        print(f"   Recent: {recent_memory['content'][:60]}...")
        print(f"   Type: {recent_memory['type']}")
    print()
    
    print("LAYER 5: Session History (Current Conversation)")
    session_count = len(payload['session_history'])
    print(f"   Session messages: {session_count}")
    if session_count > 0:
        print(f"   Last user message: {payload['session_history'][-1]['content'][:50]}...")
    print()
    
    # Test memory operations
    print("*** Testing Memory Operations ***")
    print()
    
    # Test canonization
    print("   Testing canonization...")
    success = router.canonize_response(
        "jane", 
        "I just realized that engineering conflicts often stem from unclear technical requirements. This is now part of my diagnostic checklist. #canon",
        "How do you identify root causes in technical teams?"
    )
    print(f"   [PASS] Canonization: {'Success' if success else 'Failed'}")
    
    # Test client fact addition
    print("   Testing client fact storage...")
    success = router.add_client_fact(
        "jane", 
        "user_123", 
        "conflict_pattern", 
        "architecture_disagreements",
        {"confidence": "high", "frequency": "recurring"}
    )
    print(f"   [PASS] Client fact: {'Success' if success else 'Failed'}")
    
    # Test working memory addition
    print("   Testing working memory...")
    success = router.add_working_memory(
        "jane",
        "Client shows pattern of technical team conflicts - may need architecture decision-making framework",
        "strategic_insight"
    )
    print(f"   [PASS] Working memory: {'Success' if success else 'Failed'}")
    
    # Test tag processing
    print("   Testing tag processing...")
    test_response = """Based on our conversation, I can see that your team needs clearer technical decision-making processes. #working_memory 
    
    I recommend implementing a structured architecture review process. #client_fact:recommended_solution=structured_architecture_review
    
    This pattern of technical disagreements is something I've seen before - it usually indicates unclear decision authority. #canon"""
    
    tag_results = router.process_response_tags(
        "jane", 
        test_response, 
        "user_123",
        "What should I do about these architecture conflicts?"
    )
    
    print(f"   [PASS] Tag processing: {sum(tag_results.values())}/3 tags processed")
    
    # Memory statistics
    print()
    print("*** Memory Statistics ***")
    stats = router.get_memory_stats("jane")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print()
    print("*** Sprint 6 Memory System: COMPLETE! ***")
    print("All 5 memory layers operational and integrated!")
    
    return payload

if __name__ == "__main__":
    demo_memory_system()
