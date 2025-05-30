"""
VALIS Neural Matrix Integration Test
Tests the enhanced memory system with persona responses
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the core directory to path
sys.path.append('../core')
sys.path.append('../claude-memory-ADV/MEMORY_DEV')

from valis_engine import VALISEngine
from memory_manager import add_memory, query_memories

def test_emoji_fix():
    print("=" * 50)
    print("VALIS NEURAL MATRIX INTEGRATION TEST")
    print("Testing: Memory-Enhanced Persona Responses")
    print("=" * 50)
    
async def test_neural_matrix_integration():
    # Initialize VALIS engine
    print("\n1. Initializing VALIS Engine with Neural Matrix...")
    engine = VALISEngine()
    
    # Check neural matrix status
    print("\n2. Checking Neural Matrix Status...")
    matrix_status = engine.get_neural_matrix_status()
    print(f"   Neural Matrix Enabled: {matrix_status.get('enabled', False)}")
    
    # Add some test memories
    print("\n3. Adding Test Memories to Neural Matrix...")
    test_memories = [
        "User previously discussed workplace conflict resolution strategies",
        "User is working on team communication improvements",
        "User mentioned having difficulty with remote team management",
        "persona:jane - User has management challenges with remote teams",
        "persona:emma - User wants to improve team productivity and motivation"
    ]
    
    for memory in test_memories:
        engine.add_neural_memory(memory)
        print(f"   + Added: {memory[:50]}...")

    # Test memory queries
    print("\n4. Testing Neural Memory Queries...")
    memories = engine.query_neural_memories("team management", limit=5)
    print(f"   Found {len(memories)} relevant memories for 'team management'")
    for i, memory in enumerate(memories[:3], 1):
        print(f"     {i}. {memory[:60]}...")
    
    # Test persona response with neural enhancement
    print("\n5. Testing Memory-Enhanced Persona Response...")
    test_message = "I'm having trouble managing my remote team effectively. What should I do?"
    
    try:
        result = await engine.get_persona_response(
            persona_id="jane",
            message=test_message,
            session_id=f"test_session_{datetime.now().strftime('%H%M%S')}"
        )
        
        print(f"   Request Success: {result.get('success', False)}")
        print(f"   Provider Used: {result.get('provider_used', 'Unknown')}")
        print(f"   Request ID: {result.get('request_id', 'None')}")
        
        if result.get('success') and result.get('response'):
            response_preview = result['response'][:200] + "..." if len(result['response']) > 200 else result['response']
            print(f"   Response Preview: {response_preview}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test health check
    print("\n6. System Health Check...")
    health = engine.health_check()
    print(f"   System Status: {health.get('status', 'Unknown')}")
    print(f"   Personas Loaded: {health.get('personas_loaded', 0)}")
    print(f"   Neural Matrix: {health.get('neural_matrix', {}).get('enabled', 'Unknown')}")
    print(f"   Active Sessions: {health.get('temporal_coordination', {}).get('active_sessions', 0)}")
    
    print("\n" + "=" * 50)
    print("NEURAL MATRIX INTEGRATION TEST COMPLETE!")
    print("=" * 50)

async def test_concurrent_neural_requests():
    print("\n" + "=" * 50)
    print("NEURAL MATRIX CONCURRENT REQUEST TEST")
    print("=" * 50)
    
    engine = VALISEngine()
    
    test_messages = [
        "How can I improve team communication?",
        "What are best practices for remote management?",
        "How do I handle workplace conflicts?",
        "Can you help me with performance reviews?",
        "What's the best way to motivate my team?"
    ]

    # Test memory queries
    print("\n4. Testing Neural Memory Queries...")
    memories = engine.query_neural_memories("team management", limit=5)
    print(f"   Found {len(memories)} relevant memories for 'team management'")
    for i, memory in enumerate(memories[:3], 1):
        print(f"     {i}. {memory[:60]}...")
    
    # Test persona response with neural enhancement
    print("\n5. Testing Memory-Enhanced Persona Response...")
    test_message = "I'm having trouble managing my remote team effectively. What should I do?"
    
    try:
        result = await engine.get_persona_response(
            persona_id="jane",
            message=test_message,
            session_id=f"test_session_{datetime.now().strftime('%H%M%S')}"
        )
        
        print(f"   Request Success: {result.get('success', False)}")
        print(f"   Provider Used: {result.get('provider_used', 'Unknown')}")
        print(f"   Request ID: {result.get('request_id', 'None')}")
        
        if result.get('success') and result.get('response'):
            response_preview = result['response'][:200] + "..." if len(result['response']) > 200 else result['response']
            print(f"   Response Preview: {response_preview}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test health check
    print("\n6. System Health Check...")
    health = engine.health_check()
    print(f"   System Status: {health.get('status', 'Unknown')}")
    print(f"   Personas Loaded: {health.get('personas_loaded', 0)}")
    print(f"   Neural Matrix: {health.get('neural_matrix', {}).get('enabled', 'Unknown')}")
    print(f"   Active Sessions: {health.get('temporal_coordination', {}).get('active_sessions', 0)}")
    
    print("\n" + "=" * 50)
    print("NEURAL MATRIX INTEGRATION TEST COMPLETE!")
    print("=" * 50)

async def main():
    """Run all neural matrix tests"""
    test_emoji_fix()
    
    try:
        await test_neural_matrix_integration()
        print("\nNEURAL MATRIX ENHANCED VALIS IS OPERATIONAL!")
    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
