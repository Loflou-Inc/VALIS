#!/usr/bin/env python3
"""
SPRINT 2.11: Memory Integration Testing
Test neural memory and session continuity
"""

import asyncio
import sys
import os
sys.path.append('C:\\VALIS')

from dotenv import load_dotenv
from core.valis_engine import VALISEngine

async def test_memory_integration():
    """Test memory and session continuity"""
    
    load_dotenv()
    
    print("SPRINT 2.11: MEMORY INTEGRATION TESTING")
    print("=" * 50)
    
    engine = VALISEngine()
    session_id = "memory_test_session"
    
    # First interaction
    print("\nFirst interaction:")
    result1 = await engine.get_persona_response(
        persona_id="jane",
        message="My name is Sarah and I work in marketing.",
        session_id=session_id
    )
    print(f"Success: {result1.get('success', False)}")
    
    # Second interaction - should remember Sarah
    print("\nSecond interaction (should remember Sarah):")
    result2 = await engine.get_persona_response(
        persona_id="jane",
        message="What department did I say I work in?",
        session_id=session_id
    )
    print(f"Success: {result2.get('success', False)}")
    if result2.get('success'):
        response = result2.get('response', '')
        print(f"Response mentions marketing: {'marketing' in response.lower()}")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_memory_integration())
