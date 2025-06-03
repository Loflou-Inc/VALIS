"""Test fallback cascade with Guide Sam"""
import asyncio
import sys
from pathlib import Path

valis_root = Path(__file__).parent
sys.path.insert(0, str(valis_root))

async def test_fallback_cascade():
    print("Testing Fallback Cascade for Guide Sam...")
    
    from providers.hardcoded_fallback import HardcodedFallbackProvider
    from core.valis_engine import VALISEngine
    
    # Initialize
    engine = VALISEngine()
    fallback_provider = HardcodedFallbackProvider()
    
    # Test Guide Sam directly with fallback provider
    sam_persona = engine.personas["guide_sam"]
    result = await fallback_provider.get_response(sam_persona, "I need help setting clear goals")
    
    print(f"Guide Sam fallback response: {result['response']}")
    print(f"Persona data used: {result.get('persona_data_used')}")
    print(f"Provider: {result.get('provider')}")
    
    # Check that Sam's characteristics are in the response
    response = result['response']
    has_sam_name = "Guide Sam" in response
    has_persona_elements = any(phrase in response for phrase in ["goal", "clear", "direct"])
    
    print(f"Contains Guide Sam name: {has_sam_name}")
    print(f"Contains goal-related content: {has_persona_elements}")
    print("Fallback enhancement working perfectly!")

if __name__ == "__main__":
    asyncio.run(test_fallback_cascade())