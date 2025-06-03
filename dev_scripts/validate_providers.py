#!/usr/bin/env python3
"""Provider Validation Utility - Sprint 2: Provider System Cleanup"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from providers.base_provider import get_registered_providers, create_provider

async def validate_provider(provider_name: str, provider_instance):
    """Validate a provider implements the correct interface"""
    results = {"provider": provider_name, "passed": 0, "failed": 0}
    
    # Test is_available method
    try:
        if hasattr(provider_instance, 'is_available'):
            is_available = await provider_instance.is_available()
            if isinstance(is_available, bool):
                results["passed"] += 1
            else:
                results["failed"] += 1
        else:
            results["failed"] += 1
    except:
        results["failed"] += 1
    
    # Test get_response method  
    try:
        if hasattr(provider_instance, 'get_response'):
            dummy_persona = {"id": "jane", "name": "Jane"}
            response = await provider_instance.get_response(dummy_persona, "Test message")
            if isinstance(response, dict) and "success" in response and "response" in response:
                results["passed"] += 1
            else:
                results["failed"] += 1
        else:
            results["failed"] += 1
    except:
        results["failed"] += 1
    
    return results

async def validate_all_providers():
    """Validate all active providers"""
    print("=== Provider Validation - Sprint 2 ===")
    providers = get_registered_providers()
    print(f"Found {len(providers)} registered providers: {list(providers.keys())}")
    
    total_passed = 0
    total_failed = 0
    
    for provider_name in providers:
        provider = create_provider(provider_name)
        if provider:
            results = await validate_provider(provider_name, provider)
            print(f"{provider_name}: {results['passed']}/2 tests passed")
            total_passed += results["passed"]
            total_failed += results["failed"]
        else:
            print(f"{provider_name}: FAILED TO CREATE")
            total_failed += 2
    
    print(f"\nOverall: {total_passed}/{total_passed + total_failed} tests passed")
    return total_failed == 0

if __name__ == "__main__":
    success = asyncio.run(validate_all_providers())
    sys.exit(0 if success else 1)
