#!/usr/bin/env python3
"""
REAL CHAOS ENGINEERING: Provider Cascade Under Fire
Force multiple provider failures to test real cascade behavior
"""

import asyncio
import sys
import os
sys.path.append('C:\\VALIS')

from dotenv import load_dotenv
from core.valis_engine import VALISEngine

async def real_cascade_chaos_test():
    """Force provider failures in sequence to test real cascade"""
    
    load_dotenv()
    
    print("REAL CHAOS ENGINEERING: PROVIDER CASCADE STRESS TEST")
    print("=" * 70)
    
    # Save original keys
    original_openai = os.environ.get('OPENAI_API_KEY', '')
    original_anthropic = os.environ.get('ANTHROPIC_API_KEY', '')
    
    try:
        # CHAOS SCENARIO 1: Break all API providers
        print("\nCHAOS SCENARIO 1: All API providers broken")
        print("-" * 50)
        
        os.environ['OPENAI_API_KEY'] = 'sk-invalid_chaos_key'
        os.environ['ANTHROPIC_API_KEY'] = 'invalid_anthropic_key'
        
        engine = VALISEngine()
        result1 = await engine.get_persona_response(
            persona_id="jane",
            message="Test with all APIs broken",
            session_id="cascade_chaos_1"
        )
        
        print(f"Result: Success={result1.get('success', False)}")
        print(f"Provider used: {result1.get('provider', 'Unknown')}")
        print(f"Response exists: {bool(result1.get('response', ''))}")
        
        # CHAOS SCENARIO 2: Restore OpenAI, break others
        print("\nCHAOS SCENARIO 2: Only OpenAI working")
        print("-" * 50)
        
        if original_openai:
            os.environ['OPENAI_API_KEY'] = original_openai
        
        result2 = await engine.get_persona_response(
            persona_id="advisor_alex", 
            message="Test with OpenAI restored",
            session_id="cascade_chaos_2"
        )
        
        print(f"Result: Success={result2.get('success', False)}")
        print(f"Provider used: {result2.get('provider', 'Unknown')}")
        
        return {
            'all_broken_success': result1.get('success', False),
            'all_broken_provider': result1.get('provider', 'Unknown'),
            'openai_working_success': result2.get('success', False),
            'openai_working_provider': result2.get('provider', 'Unknown')
        }
        
    finally:
        # Restore environment
        if original_openai:
            os.environ['OPENAI_API_KEY'] = original_openai
        if original_anthropic:
            os.environ['ANTHROPIC_API_KEY'] = original_anthropic

if __name__ == "__main__":
    asyncio.run(real_cascade_chaos_test())
