#!/usr/bin/env python3
"""
Test Desktop Commander Provider Directly
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from providers.desktop_commander_provider import DesktopCommanderProvider

async def test_provider():
    print("Testing Desktop Commander MCP Provider directly...")
    
    # Create provider instance
    provider = DesktopCommanderProvider()
    print(f"Provider name: {provider.name}")
    
    # Test availability
    print("Testing availability...")
    try:
        available = await provider.is_available()
        print(f"Is available: {available}")
    except Exception as e:
        print(f"Availability check failed: {e}")
        return
    
    if not available:
        print("Provider is not available - this is the problem!")
        return
    
    # Test actual response
    print("Testing get_response...")
    persona = {"id": "jane", "name": "Jane Thompson"}
    try:
        result = await provider.get_response(persona, "Test message from direct provider test")
        print(f"Response success: {result.get('success')}")
        print(f"Response text: {result.get('response', 'No response')[:100]}...")
        print(f"Provider used: {result.get('provider')}")
        if not result.get('success'):
            print(f"Error: {result.get('error')}")
    except Exception as e:
        print(f"get_response failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_provider())
