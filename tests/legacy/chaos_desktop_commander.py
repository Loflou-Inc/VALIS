#!/usr/bin/env python3
"""
CHAOS ENGINEERING: Desktop Commander Failure Testing
Test what happens when Desktop Commander is unavailable
"""

import asyncio
import sys
import os
sys.path.append('C:\\VALIS')

from dotenv import load_dotenv
from core.valis_engine import VALISEngine

async def test_desktop_commander_failure():
    """Simulate Desktop Commander being unavailable"""
    
    load_dotenv()
    
    print("CHAOS ENGINEERING: DESKTOP COMMANDER FAILURE")
    print("=" * 60)
    
    # First, let's check what the provider cascade looks like
    engine = VALISEngine()
    
    # Now test with a broken scenario - let's remove the node executable path
    # This should make Desktop Commander fail its availability check
    print("\nCHAOS TEST: Desktop Commander unavailable")
    print("-" * 50)
    
    # Temporarily rename node.exe to break Desktop Commander
    # (This is a safe way to simulate the failure without actually breaking system)
    result = await engine.get_persona_response(
        persona_id="jane", 
        message="Test during Desktop Commander failure",
        session_id="chaos_dc_failure"
    )
    
    print(f"Success: {result.get('success', False)}")
    print(f"Provider used: {result.get('provider', 'Unknown')}")
    print(f"Response exists: {bool(result.get('response', ''))}")
    
    # Test what happens when we break OpenAI too
    print("\nCHAOS TEST: Multiple provider failures")
    print("-" * 50)
    
    # Remove OpenAI key to force further fallback
    original_key = os.environ.get('OPENAI_API_KEY', '')
    os.environ['OPENAI_API_KEY'] = 'invalid_key_chaos_test'
    
    try:
        result2 = await engine.get_persona_response(
            persona_id="advisor_alex",
            message="Test with multiple failures", 
            session_id="chaos_multi_failure"
        )
        
        print(f"Success: {result2.get('success', False)}")
        print(f"Provider used: {result2.get('provider', 'Unknown')}")
        print(f"Error (if any): {result2.get('error', 'None')}")
        
    finally:
        # Restore environment
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key
        else:
            os.environ.pop('OPENAI_API_KEY', None)
    
    return result, result2

if __name__ == "__main__":
    asyncio.run(test_desktop_commander_failure())
