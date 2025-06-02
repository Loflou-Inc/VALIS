#!/usr/bin/env python3
"""SPRINT 2.7: Provider Registry Evolution Test"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_registry_system():
    print("SPRINT 2.7: PROVIDER REGISTRY EVOLUTION TEST")
    print("=" * 60)
    
    # Import all providers to trigger registration
    try:
        from providers.base_provider import get_registered_providers, create_provider
        from providers import desktop_commander_provider
        from providers import anthropic_provider
        from providers import openai_provider
        from providers import hardcoded_fallback
        
        registered = get_registered_providers()
        expected = ["desktop_commander_mcp", "anthropic_api", "openai_api", "hardcoded_fallback"]
        
        print(f"Registered: {list(registered.keys())}")
        
        all_reg = all(name in registered for name in expected)
        provider = create_provider("desktop_commander_mcp")
        creation = provider is not None
        
        from core.provider_manager import ProviderManager
        manager = ProviderManager(expected)
        integration = len(manager.providers) > 0
        
        success = all_reg and creation and integration
        print(f"All registered: {all_reg}")
        print(f"Creation works: {creation}")
        print(f"Integration works: {integration}")
        print(f"RESULT: {'SUCCESS' if success else 'FAILURE'}")
        return success
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_registry_system())
    print(f"SPRINT 2.7: {'COMPLETE' if result else 'NEEDS ATTENTION'}")
