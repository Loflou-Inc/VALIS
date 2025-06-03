#!/usr/bin/env python3
"""SPRINT 2.8: Configurability Evolution Test"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_configuration_system():
    print("SPRINT 2.8: CONFIGURABILITY EVOLUTION TEST")
    print("=" * 60)
    
    try:
        # Test config loading and schema
        from core.config_manager import get_config
        from core.config_schema import VALISConfig
        
        config = get_config()
        print(f"Config type: {type(config).__name__}")
        print(f"Max concurrent: {config.performance.max_concurrent_requests}")
        print(f"Provider timeout: {config.performance.provider_timeout}")
        print(f"Circuit threshold: {config.performance.circuit_breaker.failure_threshold}")
        
        # Test ProviderManager uses config
        from core.provider_manager import ProviderManager
        manager = ProviderManager(["hardcoded_fallback"])
        
        config_matches = (
            manager.request_semaphore._value == config.performance.max_concurrent_requests and
            manager.provider_timeout == config.performance.provider_timeout and
            manager.circuit_breaker_threshold == config.performance.circuit_breaker.failure_threshold
        )
        
        print(f"Manager uses config: {config_matches}")
        
        # Test custom validation
        custom_config = VALISConfig(performance={"max_concurrent_requests": 5})
        custom_works = custom_config.performance.max_concurrent_requests == 5
        
        success = isinstance(config, VALISConfig) and config_matches and custom_works
        print(f"All tests: {success}")
        print(f"RESULT: {'SUCCESS' if success else 'FAILURE'}")
        return success
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_configuration_system())
    print(f"SPRINT 2.8: {'COMPLETE' if result else 'NEEDS ATTENTION'}")
