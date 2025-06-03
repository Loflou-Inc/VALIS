#!/usr/bin/env python3
"""
DOC BROWN'S TEMPORAL VERIFICATION TEST
Force test OpenAI provider specifically to verify Marty's claims
"""

import asyncio
import sys
import os
sys.path.append('C:\\VALIS')

from dotenv import load_dotenv
from providers.openai_provider import OpenAIProvider

async def doc_brown_openai_verification():
    """Direct OpenAI provider verification - bypassing cascade"""
    
    load_dotenv()
    
    print("DOC BROWN'S OPENAI TEMPORAL VERIFICATION")
    print("=" * 60)
    print("Testing OpenAI provider directly to verify integration...")
    
    # Create OpenAI provider directly
    provider = OpenAIProvider()
    
    # Test 1: Check availability
    print("\nTest 1: Provider Availability Check")
    available = await provider.is_available()
    print(f"OpenAI Provider Available: {available}")
    
    if available:
        # Test 2: Direct API call
        print("\nTest 2: Direct API Integration Test")
        
        # Load a persona for testing
        import json
        with open('C:/VALIS/personas/jane.json', 'r') as f:
            persona = json.load(f)
        
        result = await provider.get_response(
            persona=persona,
            message="Hello! What's your role and how can you help me?",
            session_id="doc_brown_verification"
        )
        
        print(f"Success: {result.get('success', False)}")
        print(f"Provider: {result.get('provider', 'Unknown')}")
        print(f"Model: {result.get('model', 'Unknown')}")
        print(f"Cost: {result.get('cost', 'Unknown')}")
        
        if result.get('success'):
            response = result.get('response', '')
            print(f"Response length: {len(response)} characters")
            print(f"Response preview: {response[:300]}...")
            print("\nOPENAI INTEGRATION: VERIFIED ✅")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            print("\nOPENAI INTEGRATION: FAILED ❌")
    else:
        print("\nOPENAI INTEGRATION: UNAVAILABLE ❌")
        print("Reason: No API key or provider not configured")

if __name__ == "__main__":
    asyncio.run(doc_brown_openai_verification())
