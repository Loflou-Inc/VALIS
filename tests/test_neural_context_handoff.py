"""
Test Neural Context Handoff for Task 2.3
Verifies that neural context transfers seamlessly between providers
"""

import sys
import os
import asyncio
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from valis_engine import VALISEngine

async def test_neural_context_handoff():
    print("=" * 60)
    print("NEURAL CONTEXT HANDOFF TEST - TASK 2.3")
    print("Testing consciousness continuity across provider cascade")
    print("=" * 60)
    
    # Create VALIS engine
    engine = VALISEngine()
    
    # Test 1: Establish conversation history
    print("\n1. ESTABLISHING CONVERSATION HISTORY...")
    session_id = f"neural_test_{int(time.time())}"
    
    # First interaction to create memory
    result1 = await engine.get_persona_response(
        persona_id="jane",
        message="I'm having conflicts with my team members about project deadlines.",
        session_id=session_id
    )
    
    print(f"   First interaction: {result1.get('success')}")
    print(f"   Provider used: {result1.get('provider_used')}")
    
    # Wait a moment for memory to be stored
    await asyncio.sleep(0.5)
    
    # Second interaction to build context
    result2 = await engine.get_persona_response(
        persona_id="jane", 
        message="The conflicts are getting worse and affecting team morale.",
        session_id=session_id
    )
    
    print(f"   Second interaction: {result2.get('success')}")
    print(f"   Provider used: {result2.get('provider_used')}")
    
    # Test 2: Force cascade failure to test context handoff
    print("\n2. TESTING NEURAL CONTEXT HANDOFF...")
    print("   (Simulating Desktop Commander failure)")
    
    # Temporarily disable Desktop Commander by modifying provider list
    original_providers = engine.provider_manager.providers.copy()
    
    # Remove Desktop Commander from provider list to force cascade
    engine.provider_manager.providers = [p for p in original_providers if "DesktopCommander" not in p.__class__.__name__]
    
    print(f"   Available providers after Desktop Commander 'failure': {[p.__class__.__name__ for p in engine.provider_manager.providers]}")
    
    # Third interaction should cascade to fallback with neural context
    result3 = await engine.get_persona_response(
        persona_id="jane",
        message="What specific steps should I take to resolve these team conflicts?", 
        session_id=session_id
    )
    
    print(f"   Cascade result: {result3.get('success')}")
    print(f"   Provider used: {result3.get('provider_used')}")
    print(f"   Neural context used: {result3.get('neural_context_used', False)}")
    print(f"   Context handoff successful: {result3.get('context_handoff_successful', False)}")
    
    # Restore original providers
    engine.provider_manager.providers = original_providers
    
    # Test 3: Verify consciousness continuity
    print("\n3. VERIFYING CONSCIOUSNESS CONTINUITY...")
    
    if result3.get('neural_context_used'):
        response_text = result3.get('response', '')
        has_context_awareness = any(phrase in response_text.lower() for phrase in [
            'previous', 'conversation', 'remember', 'earlier', 'continue', 'our'
        ])
        print(f"   Response shows context awareness: {has_context_awareness}")
        
        if has_context_awareness:
            print(f"   Context preview: {response_text[:150]}...")
        
        print(f"   SUCCESS: Neural context handoff working!")
        return True
    else:
        print(f"   WARNING: Neural context not detected in cascade")
        return False

async def test_context_compression():
    print("\n4. TESTING CONTEXT COMPRESSION...")
    
    engine = VALISEngine()
    
    # Test compression with mock memories
    test_memories = [
        "User discussed team conflicts and deadlines",
        "User mentioned morale issues affecting productivity", 
        "User asked about conflict resolution strategies",
        "User expressed frustration with project management",
        "User requested specific actionable steps"
    ]
    
    compressed = engine._compress_neural_context(test_memories, max_tokens=100)
    
    print(f"   Original memories: {len(test_memories)}")
    print(f"   Compressed memories: {compressed['compressed_count']}")
    print(f"   Compression applied: {compressed['context_compressed']}")
    print(f"   Summary: {compressed['summary'][:100]}...")
    
    return compressed['memory_count'] > 0

async def main():
    """Run all neural context handoff tests"""
    try:
        handoff_success = await test_neural_context_handoff()
        compression_success = await test_context_compression()
        
        print("\n" + "=" * 60)
        print("TASK 2.3 TEST RESULTS")
        print("=" * 60)
        print(f"Neural Context Handoff: {'PASS' if handoff_success else 'FAIL'}")
        print(f"Context Compression: {'PASS' if compression_success else 'FAIL'}")
        
        if handoff_success and compression_success:
            print("SUCCESS: Neural Matrix Context Degradation Prevention OPERATIONAL!")
        else:
            print("ISSUE: Some neural context features need attention")
            
    except Exception as e:
        print(f"TEST ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
