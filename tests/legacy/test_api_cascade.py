#!/usr/bin/env python3
"""
FORCE API PROVIDER CASCADE: Test Fixed Providers Directly
"""

import asyncio
import sys
import os
sys.path.append('C:\\VALIS')

from dotenv import load_dotenv
from core.provider_manager import ProviderManager

async def test_api_cascade():
    """Test API provider cascade by checking availability directly"""
    
    load_dotenv()
    
    print("FORCED API PROVIDER CASCADE TEST")
    print("=" * 50)
    
    # Create provider manager with default config
    config = {
        "providers": ["anthropic_api", "openai_api", "hardcoded_fallback"],
        "enable_memory": True,
        "logging_level": "INFO"
    }
    
    performance_config = {
        "max_concurrent_requests": 10,
        "provider_timeout": 30,
        "circuit_breaker": {
            "failure_threshold": 3,
            "timeout_minutes": 5
        },
        "retry_schedule": [1, 2, 4]
    }
    
    manager = ProviderManager(config, performance_config)
    
    # Test 1: Check availability with invalid keys
    print("\nTest 1: Provider availability with broken keys")
    print("-" * 45)
    
    # Break API keys
    os.environ['OPENAI_API_KEY'] = 'sk-invalid_test'
    os.environ['ANTHROPIC_API_KEY'] = 'invalid_test'
    
    for provider in manager.providers:
        available = await provider.is_available()
        print(f"{provider.name}: Available = {available}")
    
    # Test 2: Try to get response (should fall back to hardcoded)
    print("\nTest 2: Get response with broken APIs")
    print("-" * 40)
    
    test_persona = {"name": "Jane", "role": "Test"}
    result = await manager.get_response(
        persona=test_persona,
        message="Test cascade with broken APIs",
        session_id="api_cascade_test"
    )
    
    print(f"Success: {result.get('success', False)}")
    print(f"Provider: {result.get('provider', 'Unknown')}")
    print(f"Error: {result.get('error', 'None')}")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_api_cascade())
