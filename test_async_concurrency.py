#!/usr/bin/env python3
"""Test async safety and concurrent operations"""

import asyncio
import time
from core.valis_engine import VALISEngine

async def test_concurrent_operations():
    """Test that multiple operations can run concurrently without blocking"""
    
    engine = VALISEngine()
    
    async def single_request(session_id):
        start_time = time.time()
        result = await engine.get_persona_response("jane", f"Test request for {session_id}", session_id)
        end_time = time.time()
        return {
            "session": session_id,
            "success": result.get("success"),
            "provider": result.get("provider_used"), 
            "time": end_time - start_time
        }
    
    # Test concurrent requests
    print("Testing concurrent async operations...")
    start_time = time.time()
    
    tasks = [
        single_request("session_1"),
        single_request("session_2"), 
        single_request("session_3"),
        single_request("session_4")
    ]
    
    results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    
    print(f"Total time for 4 concurrent requests: {total_time:.3f}s")
    for result in results:
        print(f"  {result['session']}: {result['time']:.3f}s - {result['provider']}")
    
    # Verify no blocking occurred
    all_successful = all(r["success"] for r in results)
    reasonable_time = total_time < 2.0  # Should be much faster than 4 sequential requests
    
    return all_successful and reasonable_time

if __name__ == "__main__":
    success = asyncio.run(test_concurrent_operations())
    print(f"\nAsync safety test passed: {success}")
