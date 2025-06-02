#!/usr/bin/env python3
"""SPRINT 2.6: Performance Benchmark Test"""

import asyncio
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.valis_engine import VALISEngine

async def performance_benchmark():
    print("SPRINT 2.6: PERFORMANCE BENCHMARK")
    print("=" * 50)
    
    engine = VALISEngine()
    
    # Test concurrent performance across multiple sessions
    start_time = time.time()
    tasks = []
    
    # 20 requests across 5 sessions
    for i in range(20):
        session_id = f"perf_session_{i % 5}"
        persona = ["jane", "advisor_alex"][i % 2]
        
        task = asyncio.create_task(
            engine.get_persona_response(
                persona, 
                f"Performance test {i+1}",
                session_id=session_id
            )
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time
    
    successes = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
    avg_time = total_time / 20
    
    print(f"Performance Results:")
    print(f"  Total requests: 20")
    print(f"  Successful: {successes}")
    print(f"  Total time: {total_time:.3f}s")
    print(f"  Average per request: {avg_time:.3f}s")
    print(f"  Throughput: {20/total_time:.2f} req/sec")
    
    # Performance criteria
    performance_good = (
        successes >= 19 and 
        avg_time < 0.5 and 
        total_time < 10.0
    )
    
    print(f"[PASS] Performance acceptable" if performance_good else "[FAIL] Performance issues")
    return performance_good

if __name__ == "__main__":
    result = asyncio.run(performance_benchmark())
