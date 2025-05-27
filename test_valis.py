"""VALIS Test"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

try:
    from core.valis_engine import VALISEngine
    print("SUCCESS: VALIS imported")
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

async def test():
    print("Testing VALIS...")
    
    engine = VALISEngine()
    health = engine.health_check()
    print(f"Loaded {health['personas_loaded']} personas")
    
    personas = engine.get_available_personas()
    for p in personas:
        print(f"- {p['name']}")
    
    if personas:
        result = await engine.get_persona_response("jane", "Hello")
        if result.get('success'):
            print(f"Jane: {result.get('response', '')[:50]}...")
            print(f"Via: {result.get('provider_used', 'Unknown')}")
        else:
            print(f"Error: {result.get('error')}")
    
    print("VALIS TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(test())