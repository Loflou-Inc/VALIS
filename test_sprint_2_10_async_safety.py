#!/usr/bin/env python3
"""SPRINT 2.10: ASYNC SAFETY VERIFICATION"""

import asyncio
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_async_safety():
    print("SPRINT 2.10: ASYNC SAFETY VERIFICATION")
    print("=" * 60)
    
    try:
        from core.valis_engine import VALISEngine
        
        engine = VALISEngine()
        
        # Test concurrent provider availability checks
        print("TEST: Provider Availability Concurrency")
        start_time = time.time()
        
        # Multiple concurrent availability checks
        tasks = []
        for provider in engine.provider_manager.providers:
            task = asyncio.create_task(provider.is_available())
            tasks.append(task)
            task = asyncio.create_task(provider.is_available())  # Duplicate for concurrency test
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start_time
        
        successful = sum(1 for r in results if isinstance(r, bool))
        print(f"Availability checks: {successful}/{len(results)} in {elapsed:.3f}s")
        
        # Should be fast (concurrent, not sequential blocking)
        concurrent_ok = elapsed < 8.0 and successful >= len(results) - 2
        print(f"[PASS] Non-blocking checks" if concurrent_ok else "[FAIL] Blocking detected")
        
        # Test concurrent responses
        print("TEST: Concurrent Response Handling")
        start_time = time.time()
        
        response_tasks = []
        for i in range(6):
            persona = "jane" if i % 2 == 0 else "advisor_alex"
            task = asyncio.create_task(
                engine.get_persona_response(persona, f"Test {i+1}", session_id=f"session_{i}")
            )
            response_tasks.append(task)
        
        responses = await asyncio.gather(*response_tasks, return_exceptions=True)
        response_elapsed = time.time() - start_time
        
        successful_responses = sum(1 for r in responses if isinstance(r, dict) and r.get('success'))
        print(f"Responses: {successful_responses}/6 in {response_elapsed:.3f}s")
        
        responses_ok = successful_responses >= 5 and response_elapsed < 15.0
        print(f"[PASS] Efficient responses" if responses_ok else "[FAIL] Response blocking")
        
        return concurrent_ok and responses_ok
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_async_safety())
    status = 'COMPLETE' if result else 'NEEDS ATTENTION'
    print(f"SPRINT 2.10: {status}")
