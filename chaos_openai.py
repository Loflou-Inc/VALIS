#!/usr/bin/env python3
"""
CHAOS ENGINEERING: OpenAI Failure Test
"""

import asyncio
import sys
import os
sys.path.append('C:\\VALIS')

from dotenv import load_dotenv
from providers.openai_provider import OpenAIProvider

async def chaos_openai_test():
    load_dotenv()
    
    print("CHAOS: Testing OpenAI with invalid API key")
    print("=" * 50)
    
    # Break OpenAI key
    original = os.environ.get('OPENAI_API_KEY', '')
    os.environ['OPENAI_API_KEY'] = 'chaos_invalid_key'
    
    try:
        provider = OpenAIProvider()
        available = await provider.is_available()
        print(f"Available with invalid key: {available}")
        
        if not available:
            print("GOOD: Provider correctly detected invalid key")
        else:
            # Test actual API call
            result = await provider.get_response(
                persona={"name": "Jane", "role": "Test"},
                message="Chaos test",
                session_id="chaos"
            )
            print(f"API call success: {result.get('success', False)}")
            print(f"Error message: {result.get('error', 'None')}")
            
    finally:
        # Restore key
        if original:
            os.environ['OPENAI_API_KEY'] = original
        else:
            os.environ.pop('OPENAI_API_KEY', None)

if __name__ == "__main__":
    asyncio.run(chaos_openai_test())
