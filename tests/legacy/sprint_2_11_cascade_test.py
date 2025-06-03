#!/usr/bin/env python3
"""
SPRINT 2.11: Comprehensive Provider Cascade Testing
Test provider fallback scenarios and system resilience
"""

import asyncio
import sys
import os
sys.path.append('C:\\VALIS')

from dotenv import load_dotenv
from core.valis_engine import VALISEngine

async def test_provider_cascade():
    """Test provider cascade with various failure scenarios"""
    
    load_dotenv()
    
    print("SPRINT 2.11: PROVIDER CASCADE TESTING")
    print("=" * 60)
    
    engine = VALISEngine()
    
    # Test 1: Normal operation (should use Desktop Commander)
    print("\nTest 1: Normal Provider Cascade")
    print("-" * 40)
    result1 = await engine.get_persona_response(
        persona_id="jane",
        message="What's your background in HR?",
        session_id="cascade_test_1"
    )
    print(f"Provider used: {result1.get('provider', 'Unknown')}")
    print(f"Success: {result1.get('success', False)}")
    
    # Test 2: Provider availability check
    print("\nTest 2: Provider Availability Status")
    print("-" * 40)
    from core.provider_manager import ProviderManager
    
    manager = ProviderManager(engine.config.providers, engine.config.performance)
    for provider in manager.providers:
        available = await provider.is_available()
        print(f"{provider.name}: {'Available' if available else 'Unavailable'}")
    
    return {
        'test1_success': result1.get('success', False),
        'test1_provider': result1.get('provider', 'Unknown')
    }

if __name__ == "__main__":
    asyncio.run(test_provider_cascade())
