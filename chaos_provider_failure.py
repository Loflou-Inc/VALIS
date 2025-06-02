#!/usr/bin/env python3
"""
CHAOS ENGINEERING: Provider Failure Testing
Deliberately break providers to test cascade fallback
"""

import asyncio
import sys
import os
sys.path.append('C:\\VALIS')

from dotenv import load_dotenv
from core.valis_engine import VALISEngine

# Mock environment to simulate API failures
class ChaosEnvironment:
    def __init__(self):
        self.original_env = {}
        
    def break_openai(self):
        """Simulate OpenAI API failure by removing key"""
        self.original_env['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', '')
        os.environ['OPENAI_API_KEY'] = ''
        print("CHAOS: OpenAI API key removed (simulating API failure)")
        
    def break_anthropic(self):
        """Simulate Anthropic API failure"""
        self.original_env['ANTHROPIC_API_KEY'] = os.environ.get('ANTHROPIC_API_KEY', '')
        os.environ['ANTHROPIC_API_KEY'] = ''
        print("CHAOS: Anthropic API key removed (simulating API failure)")
        
    def restore_environment(self):
        """Restore original environment"""
        for key, value in self.original_env.items():
            if value:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]

async def test_provider_failure_cascade():
    """Test what happens when providers fail in sequence"""
    
    load_dotenv()
    chaos = ChaosEnvironment()
    
    print("CHAOS ENGINEERING: PROVIDER FAILURE CASCADE")
    print("=" * 60)
    
    try:
        # Test 1: All APIs broken - should fall back to Desktop Commander or Hardcoded
        print("\nCHAOS TEST 1: All API providers broken")
        print("-" * 50)
        chaos.break_openai()
        chaos.break_anthropic()
        
        engine = VALISEngine()
        result = await engine.get_persona_response(
            persona_id="jane",
            message="Emergency test during API failures",
            session_id="chaos_test_1"
        )
        
        print(f"Success: {result.get('success', False)}")
        print(f"Provider used: {result.get('provider', 'Unknown')}")
        print(f"Response exists: {bool(result.get('response', ''))}")
        
        return result
        
    finally:
        chaos.restore_environment()

if __name__ == "__main__":
    asyncio.run(test_provider_failure_cascade())
