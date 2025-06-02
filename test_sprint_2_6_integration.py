#!/usr/bin/env python3
"""SPRINT 2.6: CONCURRENCY INTEGRATION TESTS"""

import asyncio
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.valis_engine import VALISEngine

async def test_concurrency_fixes():
    print("SPRINT 2.6: CONCURRENCY INTEGRATION TESTS")
    print("=" * 60)
    
    engine = VALISEngine()
    
    # Test session collision handling
    print("\nTEST: Session Collision Handling")
    start_time = time.time()
    tasks = []
    
    # Send 10 requests to same session simultaneously  
    for i in range(10):
        task = asyncio.create_task(
            engine.get_persona_response("jane", f"Test {i+1}", session_id="test_session")
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    elapsed = time.time() - start_time
    successes = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
    print(f"Results: {successes}/10 successful in {elapsed:.3f}s")
    print(f"[PASS] Queue system working" if successes == 10 else "[FAIL] Race conditions detected")
    
    return successes == 10

if __name__ == "__main__":
    result = asyncio.run(test_concurrency_fixes())
    print(f"\nOVERALL RESULT: {'PASS' if result else 'FAIL'}")
