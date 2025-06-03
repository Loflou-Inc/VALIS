"""Quick test of neural context handoff to fallback provider"""
import sys, asyncio, time
sys.path.append('core')
from valis_engine import VALISEngine

async def main():
    print("=== NEURAL CONTEXT HANDOFF DEMONSTRATION ===")
    engine = VALISEngine()
    session_id = f"demo_{int(time.time())}"
    
    # Build conversation history first
    print("1. Building conversation history...")
    await engine.get_persona_response("jane", "I have team conflicts about deadlines", session_id)
    await asyncio.sleep(0.5)
    await engine.get_persona_response("jane", "The conflicts are escalating badly", session_id)
    await asyncio.sleep(0.5)
    
    # Force cascade to fallback only
    print("2. Forcing cascade to hardcoded fallback...")
    original = engine.provider_manager.providers.copy()
    engine.provider_manager.providers = [p for p in original if "Hardcoded" in p.__class__.__name__]
    
    # Test with neural context
    print("3. Testing neural context handoff...")
    result = await engine.get_persona_response("jane", "What should I do about these conflicts?", session_id)
    
    print(f"Provider used: {result.get('provider_used')}")
    print(f"Neural context used: {result.get('neural_context_used', False)}")
    print(f"Context handoff successful: {result.get('context_handoff_successful', False)}")
    print(f"Response: {result.get('response', '')[:200]}...")
    
    if result.get('neural_context_used') and result.get('context_handoff_successful'):
        print("SUCCESS: Neural Matrix Context Degradation Prevention OPERATIONAL!")
    
asyncio.run(main())
