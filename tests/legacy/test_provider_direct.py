#!/usr/bin/env python3
"""
Test the provider directly within the server environment
"""
import asyncio
import sys
import os

# Add the VALIS root to Python path
sys.path.insert(0, r'C:\VALIS')

from providers.desktop_commander_provider import DesktopCommanderProvider

async def test_provider_directly():
    """Test the provider directly as it would be called in the server"""
    
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"Environment variables related to VALIS:")
    for key, value in os.environ.items():
        if 'VALIS' in key.upper() or 'CLAUDE' in key.upper() or 'ANTHROPIC' in key.upper():
            print(f"  {key} = {value}")
    
    print("\nCreating DesktopCommanderProvider...")
    provider = DesktopCommanderProvider()
    
    print(f"Provider name: {provider.name}")
    print(f"Provider cost: {provider.cost}")
    print(f"MCP interface path: {provider.mcp_interface_path}")
    print(f"MCP interface exists: {provider.mcp_interface_path.exists()}")
    
    print("\nTesting is_available()...")
    try:
        result = await provider.is_available()
        print(f"is_available() result: {result}")
        return result
    except Exception as e:
        print(f"is_available() threw exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_provider_directly())
    print(f"\nFINAL PROVIDER AVAILABILITY: {result}")
