#!/usr/bin/env python3
"""Test persona fallback behavior"""

import asyncio
from providers.hardcoded_fallback import HardcodedFallbackProvider

async def test_persona_fallbacks():
    provider = HardcodedFallbackProvider()
    
    # Test 1: Advisor Alex
    alex_persona = {
        'id': 'advisor_alex', 
        'name': 'Advisor Alex', 
        'tone': 'analytical and strategic', 
        'approach': 'systematic problem-solving'
    }
    alex_result = await provider.get_response(alex_persona, 'Hello')
    print(f"Alex response: {alex_result['response'][:100]}...")
    
    # Test 2: Guide Sam
    sam_persona = {
        'id': 'guide_sam',
        'name': 'Guide Sam', 
        'tone': 'direct and goal-focused',
        'approach': 'action-oriented coaching'
    }
    sam_result = await provider.get_response(sam_persona, 'Hello')
    print(f"Sam response: {sam_result['response'][:100]}...")
    
    # Test 3: Unknown persona
    unknown_persona = {
        'id': 'unknown_ai',
        'name': 'Unknown AI'
    }
    unknown_result = await provider.get_response(unknown_persona, 'Hello')
    print(f"Unknown response: {unknown_result['response'][:100]}...")
    
    return alex_result['success'] and sam_result['success'] and unknown_result['success']

if __name__ == "__main__":
    success = asyncio.run(test_persona_fallbacks())
    print(f"All tests successful: {success}")
