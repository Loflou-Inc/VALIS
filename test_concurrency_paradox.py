"""
SPRINT 2.6: Concurrency Paradox Resolution Tests
Comprehensive testing for proper session synchronization and race condition elimination
"""

import asyncio
import time
import sys
from pathlib import Path

valis_root = Path(__file__).parent
sys.path.insert(0, str(valis_root))

async def test_scenario_1_simultaneous_requests():
    """TEST SCENARIO 1: Fire 3 simultaneous requests to same persona/session"""
    print("TEST SCENARIO 1: Simultaneous Requests to Same Session")
    print("-" * 60)
    
    from core.valis_engine import VALISEngine
    
    engine = VALISEngine()
    session_id = "test_concurrent_session"
    
    async def make_request(request_num):
        start_time = time.time()
        result = await engine.get_persona_response(
            "jane",
            f"Concurrent request #{request_num}",
            session_id=session_id
        )
        end_time = time.time()
        return {
            "request_num": request_num,
            "success": result.get("success"),
            "provider": result.get("provider_used"),
            "response_time": end_time - start_time,
            "timestamp": end_time
        }
    
    # Fire 3 simultaneous requests
    print("Firing 3 simultaneous requests to same session...")
    start_time = time.time()
    
    tasks = [
        make_request(1),
        make_request(2), 
        make_request(3)
    ]
    
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    # Analyze results
    print(f"Total time for 3 requests: {total_time:.3f}s")
    
    for result in results:
        print(f"   Request {result['request_num']}: {result['response_time']:.3f}s - {result['provider']}")
    
    # Verify serialization (requests should have been processed sequentially)
    timestamps = [r['timestamp'] for r in results]
    timestamps.sort()
    
    # Check if requests were processed in sequence (with some tolerance)
    sequential = True
    for i in range(1, len(timestamps)):
        gap = timestamps[i] - timestamps[i-1]
        if gap < 0.05:  # Less than 50ms gap suggests overlapping
            sequential = False
            break
    
    print(f"   [{'PASS' if sequential else 'FAIL'}] Requests processed sequentially")
    print(f"   [{'PASS' if all(r['success'] for r in results) else 'FAIL'}] All requests successful")
    
    return all(r['success'] for r in results) and sequential

async def test_scenario_2_rapid_requests():
    """TEST SCENARIO 2: Fire 10 rapid requests to same session while provider is slow"""
    print("\nTEST SCENARIO 2: Rapid Requests to Same Session")
    print("-" * 60)
    
    from core.valis_engine import VALISEngine
    
    engine = VALISEngine()
    session_id = "test_rapid_session"
    
    async def make_rapid_request(request_num):
        result = await engine.get_persona_response(
            "jane",
            f"Rapid request #{request_num}",
            session_id=session_id
        )
        return {
            "request_num": request_num,
            "success": result.get("success"),
            "provider": result.get("provider_used")
        }
    
    print("Firing 10 rapid requests to same session...")
    
    # Fire all requests with minimal delay
    tasks = []
    for i in range(1, 11):
        tasks.append(make_rapid_request(i))
        await asyncio.sleep(0.01)  # Tiny delay to simulate rapid firing
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    print(f"10 rapid requests completed in: {total_time:.3f}s")
    
    successful_requests = sum(1 for r in results if r['success'])
    print(f"   [{'PASS' if successful_requests == 10 else 'FAIL'}] {successful_requests}/10 requests successful")
    
    # Check for consistent provider usage (no session mixing)
    providers = [r['provider'] for r in results if r['success']]
    consistent_provider = len(set(providers)) == 1 if providers else False
    print(f"   [{'PASS' if consistent_provider else 'FAIL'}] Consistent provider usage: {set(providers)}")
    
    return successful_requests == 10 and consistent_provider

async def test_scenario_3_mixed_sessions():
    """TEST SCENARIO 3: Mixed sessions - some concurrent, some sequential"""
    print("\nTEST SCENARIO 3: Mixed Concurrent and Sequential Sessions")
    print("-" * 60)
    
    from core.valis_engine import VALISEngine
    
    engine = VALISEngine()
    
    async def session_worker(session_id, num_requests):
        results = []
        for i in range(num_requests):
            result = await engine.get_persona_response(
                "advisor_alex",
                f"Session {session_id} request {i+1}",
                session_id=session_id
            )
            results.append(result.get("success", False))
        return session_id, results
    
    # Create tasks for multiple sessions
    print("Running 5 concurrent sessions with 3 requests each...")
    
    tasks = [
        session_worker("session_A", 3),
        session_worker("session_B", 3),
        session_worker("session_C", 3),
        session_worker("session_D", 3),
        session_worker("session_E", 3)
    ]
    
    start_time = time.time()
    session_results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    print(f"5 sessions with 15 total requests completed in: {total_time:.3f}s")
    
    # Analyze results
    total_requests = 0
    successful_requests = 0
    
    for session_id, results in session_results:
        session_success = sum(results)
        total_requests += len(results)
        successful_requests += session_success
        print(f"   Session {session_id}: {session_success}/{len(results)} successful")
    
    print(f"   [{'PASS' if successful_requests == total_requests else 'FAIL'}] {successful_requests}/{total_requests} total requests successful")
    
    return successful_requests == total_requests

async def test_stress_concurrent_sessions():
    """Stress Test: 100 concurrent requests across 10 different sessions"""
    print("\nSTRESS TEST: 100 Concurrent Requests Across 10 Sessions")
    print("-" * 60)
    
    from core.valis_engine import VALISEngine
    
    engine = VALISEngine()
    
    async def stress_request(session_num, request_num):
        session_id = f"stress_session_{session_num}"
        result = await engine.get_persona_response(
            "guide_sam",
            f"Stress test S{session_num}R{request_num}",
            session_id=session_id
        )
        return {
            "session": session_num,
            "request": request_num,
            "success": result.get("success", False),
            "provider": result.get("provider_used")
        }
    
    print("Generating 100 requests across 10 sessions...")
    
    # Create 100 requests (10 requests per session across 10 sessions)
    tasks = []
    for session_num in range(1, 11):
        for request_num in range(1, 11):
            tasks.append(stress_request(session_num, request_num))
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    print(f"100 requests completed in: {total_time:.3f}s")
    print(f"Average response time: {total_time/100:.3f}s per request")
    
    # Analyze results
    successful = sum(1 for r in results if r['success'])
    print(f"   [{'PASS' if successful >= 95 else 'FAIL'}] {successful}/100 requests successful ({successful}%)")
    
    # Check session distribution
    session_counts = {}
    for r in results:
        if r['success']:
            session_counts[r['session']] = session_counts.get(r['session'], 0) + 1
    
    balanced_sessions = len([s for s in session_counts.values() if s >= 8])  # At least 8/10 successful per session
    print(f"   [{'PASS' if balanced_sessions >= 8 else 'FAIL'}] {balanced_sessions}/10 sessions had good success rate")
    
    return successful >= 95 and balanced_sessions >= 8

async def main():
    """Run all concurrency tests"""
    print("SPRINT 2.6: CONCURRENCY PARADOX RESOLUTION TESTS")
    print("=" * 70)
    
    tests = [
        test_scenario_1_simultaneous_requests,
        test_scenario_2_rapid_requests,
        test_scenario_3_mixed_sessions,
        test_stress_concurrent_sessions
    ]
    
    all_passed = True
    
    for test in tests:
        try:
            passed = await test()
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"   [ERROR] Test failed with exception: {e}")
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("SPRINT 2.6 SUCCESS: All concurrency tests PASSED!")
        print("Race condition eliminated - proper session synchronization working!")
    else:
        print("SPRINT 2.6 ISSUES: Some concurrency tests failed")
        print("Race conditions may still exist - review implementation")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)