"""
VALIS Simple Usage Example
Shows how easy it is to integrate AI personas into any application
"""

import asyncio
import sys
from pathlib import Path

# Add VALIS to path  
sys.path.append(str(Path(__file__).parent.parent))
from core.valis_engine import VALISEngine, ask_persona

async def demo():
    """Simple VALIS demo"""
    print("=== VALIS Demo ===")
    
    # Method 1: Simple function
    response = await ask_persona("jane", "I'm having a conflict with my coworker.")
    print(f"Jane: {response}")
    
    # Method 2: Full engine
    engine = VALISEngine()
    print(f"Available: {[p['name'] for p in engine.get_available_personas()]}")
    
    result = await engine.get_persona_response("coach_emma", "How do I motivate my team?")
    print(f"Emma: {result.get('response')}")
    print(f"Provider: {result.get('provider_used')}")
    
    result = await engine.get_persona_response("billy_corgan", "I need creative inspiration.")
    print(f"Billy: {result.get('response')}")

async def multi_perspective():
    """Get multiple perspectives on same issue"""
    print("=== Multiple Perspectives ===")
    
    engine = VALISEngine()
    situation = "Team members have creative differences affecting deadlines."
    
    for persona_id in ["jane", "coach_emma", "billy_corgan"]:
        result = await engine.get_persona_response(persona_id, situation)
        name = engine.get_persona_info(persona_id).get("name", persona_id)
        print(f"{name}: {result.get('response', 'No response')}")

if __name__ == "__main__":
    asyncio.run(demo())
    asyncio.run(multi_perspective())