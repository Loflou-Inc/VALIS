#!/usr/bin/env python3
"""
Test real provider integration with API keys
"""

import asyncio
import sys
import os
sys.path.append('C:\\VALIS')

from dotenv import load_dotenv
from core.valis_engine import VALISEngine

async def test_real_providers():
    """Test real API provider integration"""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize VALIS engine
    engine = VALISEngine()
    
    print("TESTING REAL API PROVIDER INTEGRATION")
    print("=" * 50)
    
    # Test with Jane persona using OpenAI
    print("\nTesting OpenAI Provider with Jane persona...")
    result = await engine.get_persona_response(
        persona_id="jane",
        message="Hi! What's your role at the company?",
        session_id="test_session_openai"
    )
    
    print(f"Success: {result.get('success', False)}")
    print(f"Provider: {result.get('provider', 'Unknown')}")
    if result.get('success'):
        print(f"Response: {result.get('response', '')[:200]}...")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_real_providers())
