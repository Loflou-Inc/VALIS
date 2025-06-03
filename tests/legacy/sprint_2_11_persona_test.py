#!/usr/bin/env python3
"""
SPRINT 2.11: Persona Switch Testing
Test different personas with provider cascade
"""

import asyncio
import sys
import os
sys.path.append('C:\\VALIS')

from dotenv import load_dotenv
from core.valis_engine import VALISEngine

async def test_persona_switch():
    """Test persona switching functionality"""
    
    load_dotenv()
    
    print("SPRINT 2.11: PERSONA SWITCH TESTING")
    print("=" * 50)
    
    engine = VALISEngine()
    
    # Test different personas
    personas_to_test = ["jane", "coach_emma", "advisor_alex"]
    
    for persona_id in personas_to_test:
        print(f"\nTesting persona: {persona_id}")
        print("-" * 30)
        
        result = await engine.get_persona_response(
            persona_id=persona_id,
            message="Tell me about yourself briefly.",
            session_id=f"persona_test_{persona_id}"
        )
        
        print(f"Success: {result.get('success', False)}")
        print(f"Provider: {result.get('provider', 'Unknown')}")
        if result.get('success'):
            response = result.get('response', '')
            print(f"Response: {response[:150]}...")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_persona_switch())
