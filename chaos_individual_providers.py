#!/usr/bin/env python3
"""
CHAOS ENGINEERING: Forced Provider Cascade Testing
Directly test provider failures by examining provider manager
"""

import asyncio
import sys
import os
sys.path.append('C:\\VALIS')

from dotenv import load_dotenv
from core.provider_manager import ProviderManager
from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider
from providers.hardcoded_fallback import HardcodedFallbackProvider

async def test_forced_provider_failures():
    """Test each provider individually under failure conditions"""
    
    load_dotenv()
    
    print("CHAOS ENGINEERING: INDIVIDUAL PROVIDER FAILURE TESTING")
    print("=" * 70)
    
    # Test 1: OpenAI with invalid key
    print("\nCHAOS TEST 1: OpenAI with invalid API key")
    print("-" * 50)
    
    # Save original key
    original_openai = os.environ.get('OPENAI_API_KEY', '')
    os.environ['OPENAI_API_KEY'] = 'invalid_chaos_key'
    
    try:
        openai_provider = OpenAIProvider()
        available = await openai_provider.is_available()
        print(f"OpenAI available with invalid key: {available}")
        
        if available:  # This should be False, but let's test anyway
            result = await openai_provider.get_response(
                persona={"name": "Jane", "role": "Test"},
                message="Chaos test",
                session_id="chaos_openai"
            )
            print(f"OpenAI Success: {result.get('success', False)}")
            print(f"OpenAI Error: {result.get('error', 'None')}")
    
    finally:
        # Restore original key
        if original_openai:
            os.environ['OPENAI_API_KEY'] = original_openai
        else:
            os.environ.pop('OPENAI_API_KEY', None)
    
    # Test 2: Hardcoded fallback (should never fail)
    print("\nCHAOS TEST 2: Hardcoded Fallback Provider")
    print("-" * 50)
    
    fallback = HardcodedFallbackProvider()
    fallback_result = await fallback.get_response(
        persona={"name": "Jane Thompson", "role": "HR Manager"},
        message="Emergency fallback test",
        session_id="chaos_fallback"
    )
    
    print(f"Fallback Success: {fallback_result.get('success', False)}")
    print(f"Fallback Response exists: {bool(fallback_result.get('response', ''))}")

if __name__ == "__main__":
    asyncio.run(test_forced_provider_failures())
