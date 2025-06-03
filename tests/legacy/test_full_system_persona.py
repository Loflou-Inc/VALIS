#!/usr/bin/env python3
"""Test full system persona integration"""

import asyncio
from core.valis_engine import VALISEngine

async def test_full_system():
    engine = VALISEngine()
    
    # Test with advisor_alex
    result = await engine.get_persona_response('advisor_alex', 'Hello', 'test_session')
    print(f"Provider used: {result.get('provider_used')}")
    print(f"Alex response: {result.get('response', 'No response')[:150]}...")
    
    return result.get('success', False)

if __name__ == "__main__":
    success = asyncio.run(test_full_system())
    print(f"Full system test successful: {success}")
