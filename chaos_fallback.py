#!/usr/bin/env python3
"""
CHAOS ENGINEERING: Hardcoded Fallback Stress Test
"""

import asyncio
import sys
import os
sys.path.append('C:\\VALIS')

from providers.hardcoded_fallback import HardcodedFallbackProvider

async def chaos_fallback_test():
    print("CHAOS: Testing Hardcoded Fallback Under Stress")
    print("=" * 50)
    
    fallback = HardcodedFallbackProvider()
    
    # Test 1: Normal operation
    print("Test 1: Normal fallback operation")
    result1 = await fallback.get_response(
        persona={"name": "Jane Thompson", "role": "HR Manager"},
        message="Normal test",
        session_id="fallback_normal"
    )
    print(f"Success: {result1.get('success', False)}")
    
    # Test 2: Malformed persona data
    print("\nTest 2: Malformed persona data")
    result2 = await fallback.get_response(
        persona={"invalid": "data"},
        message="Test with bad persona",
        session_id="fallback_bad_persona"
    )
    print(f"Success: {result2.get('success', False)}")
    
    # Test 3: Empty/None inputs
    print("\nTest 3: Empty inputs")
    result3 = await fallback.get_response(
        persona={},
        message="",
        session_id=""
    )
    print(f"Success: {result3.get('success', False)}")
    
    # Test 4: Unknown persona
    print("\nTest 4: Unknown persona")
    result4 = await fallback.get_response(
        persona={"name": "Unknown Person", "role": "Unknown"},
        message="Who are you?",
        session_id="fallback_unknown"
    )
    print(f"Success: {result4.get('success', False)}")
    
    return all([
        result1.get('success', False),
        result2.get('success', False), 
        result3.get('success', False),
        result4.get('success', False)
    ])

if __name__ == "__main__":
    asyncio.run(chaos_fallback_test())
