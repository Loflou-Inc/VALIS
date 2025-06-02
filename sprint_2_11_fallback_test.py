#!/usr/bin/env python3
"""
SPRINT 2.11: Fallback Testing
Test hardcoded fallback provider directly
"""

import asyncio
import sys
import os
sys.path.append('C:\\VALIS')

from providers.hardcoded_fallback import HardcodedFallbackProvider

async def test_fallback_system():
    """Test hardcoded fallback provider"""
    
    print("SPRINT 2.11: FALLBACK PROVIDER TESTING")
    print("=" * 50)
    
    fallback = HardcodedFallbackProvider()
    
    # Test different personas with fallback
    personas_data = {
        "jane": {"name": "Jane Thompson", "role": "HR Manager"},
        "coach_emma": {"name": "Coach Emma", "role": "Fitness Coach"},
        "advisor_alex": {"name": "Advisor Alex", "role": "Business Advisor"},
        "unknown_persona": {"name": "Unknown Persona", "role": "Unknown"}
    }
    
    for persona_id, persona_data in personas_data.items():
        print(f"\nTesting fallback for: {persona_id}")
        print("-" * 30)
        
        result = await fallback.get_response(
            persona=persona_data,
            message="Tell me about yourself.",
            session_id=f"fallback_test_{persona_id}"
        )
        
        print(f"Success: {result.get('success', False)}")
        if result.get('success'):
            response = result.get('response', '')
            print(f"Response: {response[:100]}...")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_fallback_system())
