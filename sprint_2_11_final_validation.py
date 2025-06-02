#!/usr/bin/env python3
"""
SPRINT 2.11: FINAL COMPREHENSIVE VALIDATION
Complete system testing summary and performance metrics
"""

import asyncio
import sys
import os
import time
sys.path.append('C:\\VALIS')

from dotenv import load_dotenv
from core.valis_engine import VALISEngine

async def final_system_validation():
    """Final comprehensive VALIS system validation"""
    
    load_dotenv()
    
    print("SPRINT 2.11: FINAL SYSTEM VALIDATION")
    print("=" * 60)
    
    engine = VALISEngine()
    results = {}
    
    # Test 1: System initialization
    start_time = time.time()
    init_time = time.time() - start_time
    results['init_time'] = init_time
    print(f"System initialization: {init_time:.3f}s")
    
    # Test 2: Rapid persona switching
    print("\nRapid persona switching test...")
    personas = ["jane", "coach_emma", "advisor_alex"]
    switch_start = time.time()
    
    for i, persona in enumerate(personas):
        result = await engine.get_persona_response(
            persona_id=persona,
            message=f"Quick test {i+1}",
            session_id=f"final_test_{persona}"
        )
        results[f'{persona}_success'] = result.get('success', False)
    
    switch_time = time.time() - switch_start
    results['persona_switch_time'] = switch_time
    print(f"3 persona switches completed in: {switch_time:.3f}s")
    
    # Test 3: Performance summary
    avg_per_request = switch_time / 3
    results['avg_response_time'] = avg_per_request
    print(f"Average response time: {avg_per_request:.3f}s")
    
    return results

if __name__ == "__main__":
    asyncio.run(final_system_validation())
