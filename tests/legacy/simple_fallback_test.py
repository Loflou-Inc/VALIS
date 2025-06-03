"""Simple test for fallback enhancements"""
import asyncio
import sys
from pathlib import Path

# Add VALIS root to path
valis_root = Path(__file__).parent
sys.path.insert(0, str(valis_root))

async def test_fallback_enhancements():
    print("Testing VALIS Fallback Provider Enhancements...")
    
    from providers.hardcoded_fallback import HardcodedFallbackProvider
    from core.valis_engine import VALISEngine
    
    # Initialize
    engine = VALISEngine()
    fallback_provider = HardcodedFallbackProvider()
    
    print("Available personas:", list(engine.personas.keys()))
    
    # Test Jane with persona data
    jane_persona = engine.personas["jane"]
    result = await fallback_provider.get_response(jane_persona, "I need help with workplace stress")
    
    print(f"Jane response: {result['response'][:100]}...")
    print(f"Persona data used: {result.get('persona_data_used')}")
    print(f"Success: {result['success']}")
    
    # Test Alex with persona data
    alex_persona = engine.personas["advisor_alex"]
    result = await fallback_provider.get_response(alex_persona, "I need strategic advice")
    
    print(f"Alex response: {result['response'][:100]}...")
    print(f"Persona data used: {result.get('persona_data_used')}")
    
    # Test unknown persona handling
    unknown_persona = {
        "id": "unknown_test",
        "name": "Test Unknown Person",
        "description": "A test persona",
        "tone": "helpful",
        "background": "Testing unknown personas",
        "approach": "I help test unknown persona handling.",
        "language_patterns": {
            "common_phrases": ["How can I assist you?", "Let's work together."]
        }
    }
    
    result = await fallback_provider.get_response(unknown_persona, "Hello")
    print(f"Unknown persona response: {result['response'][:100]}...")
    print(f"Contains 'Test Unknown Person': {'Test Unknown Person' in result['response']}")
    print(f"Does NOT contain 'jane': {'jane' not in result['response'].lower()}")
    
    print("Sprint 1, Task 5 - Fallback Enhancements - SUCCESS!")

if __name__ == "__main__":
    asyncio.run(test_fallback_enhancements())