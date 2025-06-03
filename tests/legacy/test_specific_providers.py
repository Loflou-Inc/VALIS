#!/usr/bin/env python3
"""
Test specific API providers directly
"""

import asyncio
import sys
import os
sys.path.append('C:\\VALIS')

from dotenv import load_dotenv
from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider

async def test_specific_providers():
    """Test specific API providers directly"""
    
    # Load environment variables
    load_dotenv()
    
    print("TESTING SPECIFIC API PROVIDERS")
    print("=" * 50)
    
    # Test OpenAI provider availability
    openai_provider = OpenAIProvider()
    openai_available = await openai_provider.is_available()
    print(f"OpenAI Provider Available: {openai_available}")
    
    # Test Anthropic provider availability
    anthropic_provider = AnthropicProvider()
    anthropic_available = await anthropic_provider.is_available()
    print(f"Anthropic Provider Available: {anthropic_available}")
    
    # If OpenAI is available, test it directly
    if openai_available:
        print("\nTesting OpenAI provider directly...")
        
        # Create a simple persona for testing
        test_persona = {
            "name": "Jane Thompson",
            "role": "Senior HR Manager",
            "background": "Experienced HR professional with 8+ years in talent management",
            "tone": "Professional, helpful, and empathetic",
            "approach": "Systematic and thorough"
        }
        
        result = await openai_provider.get_response(
            persona=test_persona,
            message="What's your role at the company?",
            session_id="test_openai_direct"
        )
        
        print(f"OpenAI Success: {result.get('success', False)}")
        print(f"OpenAI Model: {result.get('model', 'Unknown')}")
        if result.get('success'):
            print(f"OpenAI Response: {result.get('response', '')[:200]}...")
        else:
            print(f"OpenAI Error: {result.get('error', 'Unknown error')}")
    
    return {
        'openai_available': openai_available,
        'anthropic_available': anthropic_available
    }

if __name__ == "__main__":
    asyncio.run(test_specific_providers())
