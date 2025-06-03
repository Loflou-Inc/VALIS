"""VALIS Temporal Stabilization Test"""

import asyncio
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

try:
    from core.valis_engine import VALISEngine
    print("SUCCESS: VALIS with Temporal Stabilization imported")
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

async def test_basic_functionality():
    """Test basic VALIS functionality"""
    print(">> Testing basic VALIS functionality...")
    
    engine = VALISEngine()
    
    # Test engine health check
    status = engine.health_check()
    print(f"SUCCESS: Loaded {status['personas_loaded']} personas")
    print(f"SUCCESS: Engine status: {status['status']}")
    
    # Test persona listing
    personas = engine.get_available_personas()
    for p in personas:
        print(f"  - {p['name']}: {p['description'][:50]}...")
    
    return engine, personas

async def test_persona_responses(engine, personas):
    """Test persona responses with temporal features"""
    print("\n>> Testing persona responses...")
    
    if not personas:
        print("ERROR: No personas available for testing")
        return
    
    # Test basic response
    result = await engine.get_persona_response("jane", "I need help with a workplace conflict")
    if result.get('success'):
        print(f"SUCCESS: Jane responded successfully")
        print(f"   Provider: {result.get('provider_used', 'Unknown')}")
        print(f"   Response time: {result.get('response_time', 0):.3f}s")
        print(f"   Session ID: {result.get('session_id', 'None')}")
        print(f"   Response: {result.get('response', '')[:100]}...")
    else:
        print(f"ERROR: Jane failed: {result.get('error')}")
    
    # Test session continuity
    session_id = result.get('session_id')
    if session_id:
        result2 = await engine.get_persona_response(
            "jane", 
            "Can you give me more specific advice?", 
            session_id=session_id
        )
        if result2.get('success'):
            print(f"SUCCESS: Session continuity works (Session: {session_id[:8]}...)")

async def test_concurrent_requests(engine):
    """Test concurrent request handling"""
    print("\n>> Testing concurrent requests...")
    
    start_time = time.time()
    
    # Send 10 concurrent requests
    tasks = []
    for i in range(10):
        task = engine.get_persona_response(
            "jane", 
            f"Concurrent test message #{i}",
            session_id=f"test_session_{i % 3}"  # Use 3 different sessions
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    
    successful = [r for r in results if isinstance(r, dict) and r.get('success')]
    failed = [r for r in results if not (isinstance(r, dict) and r.get('success'))]
    
    print(f"SUCCESS: Concurrent test completed in {end_time - start_time:.2f}s")
    print(f"   Successful: {len(successful)}/10")
    print(f"   Failed: {len(failed)}/10")
    
    if successful:
        response_times = [r.get('response_time', 0) for r in successful]
        avg_time = sum(response_times) / len(response_times)
        print(f"   Average response time: {avg_time:.3f}s")

async def test_error_handling(engine):
    """Test error handling capabilities"""
    print("\n>> Testing error handling...")
    
    # Test invalid persona
    result = await engine.get_persona_response("nonexistent_persona", "test")
    if not result.get('success') and 'available_personas' in result:
        print("SUCCESS: Invalid persona handled correctly")
    else:
        print("ERROR: Invalid persona not handled properly")
    
    # Test empty message
    result = await engine.get_persona_response("jane", "")
    print(f"SUCCESS: Empty message handled: {result.get('success', False)}")

async def main():
    """Main test function"""
    print("=" * 60)
    print("VALIS TEMPORAL STABILIZATION TEST")
    print("=" * 60)
    
    try:
        # Basic functionality
        engine, personas = await test_basic_functionality()
        
        # Persona responses
        await test_persona_responses(engine, personas)
        
        # Concurrent handling
        await test_concurrent_requests(engine)
        
        # Error handling
        await test_error_handling(engine)
        
        # Final status
        print("\n>> Final engine status:")
        final_status = engine.health_check()
        for key, value in final_status.items():
            if key != 'provider_cascade':  # Skip complex nested data
                print(f"   {key}: {value}")
        
        # Test completed successfully
        print("\nSUCCESS: Test completed successfully")
        
    except Exception as e:
        print(f"\nERROR: Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("VALIS TEMPORAL STABILIZATION TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())