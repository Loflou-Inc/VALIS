#!/usr/bin/env python3
"""
TEMPORAL DISASTER PREVENTION: Test Fixed Provider Availability
"""

import asyncio
import sys
import os
sys.path.append('C:\\VALIS')

from dotenv import load_dotenv
from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider

async def test_fixed_provider_availability():
    """Test that providers now correctly detect invalid API keys"""
    
    load_dotenv()
    
    print("TESTING FIXED PROVIDER AVAILABILITY CHECKS")
    print("=" * 60)
    
    # Save original keys
    original_openai = os.environ.get('OPENAI_API_KEY', '')
    original_anthropic = os.environ.get('ANTHROPIC_API_KEY', '')
    
    try:
        # Test 1: OpenAI with invalid key
        print("\nTest 1: OpenAI with INVALID key")
        print("-" * 40)
        os.environ['OPENAI_API_KEY'] = 'sk-invalid_chaos_test_key'
        
        openai_provider = OpenAIProvider()
        openai_available = await openai_provider.is_available()
        print(f"OpenAI available with invalid key: {openai_available}")
        
        if openai_available:
            print("ERROR: OpenAI should reject invalid key!")
        else:
            print("SUCCESS: OpenAI correctly rejected invalid key!")
        
        # Test 2: OpenAI with valid key (if we have one)
        if original_openai:
            print("\nTest 2: OpenAI with VALID key")
            print("-" * 40)
            os.environ['OPENAI_API_KEY'] = original_openai
            
            openai_available_valid = await openai_provider.is_available()
            print(f"OpenAI available with valid key: {openai_available_valid}")
        
        # Test 3: Anthropic with no key
        print("\nTest 3: Anthropic with NO key")
        print("-" * 40)
        if 'ANTHROPIC_API_KEY' in os.environ:
            del os.environ['ANTHROPIC_API_KEY']
        
        anthropic_provider = AnthropicProvider()
        anthropic_available = await anthropic_provider.is_available()
        print(f"Anthropic available with no key: {anthropic_available}")
        
        if anthropic_available:
            print("ERROR: Anthropic should require API key!")
        else:
            print("SUCCESS: Anthropic correctly requires API key!")
        
        return {
            'openai_invalid_rejected': not openai_available,
            'anthropic_no_key_rejected': not anthropic_available
        }
        
    finally:
        # Restore original keys
        if original_openai:
            os.environ['OPENAI_API_KEY'] = original_openai
        if original_anthropic:
            os.environ['ANTHROPIC_API_KEY'] = original_anthropic

if __name__ == "__main__":
    asyncio.run(test_fixed_provider_availability())
