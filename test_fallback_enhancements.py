"""
Test hardcoded fallback enhancements for VALIS
Tests Task 5 of Sprint 1: Fallback provider using persona JSON data
"""

import asyncio
import sys
from pathlib import Path

# Add VALIS root to path
valis_root = Path(__file__).parent
sys.path.insert(0, str(valis_root))

async def test_fallback_persona_data():
    """Test that fallback provider uses persona JSON data instead of hardcoded responses"""
    print("Testing Fallback Provider with Persona Data...")
    
    from providers.hardcoded_fallback import HardcodedFallbackProvider
    from core.valis_engine import VALISEngine
    
    # Initialize engine to load personas
    engine = VALISEngine()
    fallback_provider = HardcodedFallbackProvider()
    
    # Test each persona
    test_cases = [
        ("jane", "I need help with workplace stress"),
        ("advisor_alex", "I need some strategic advice"),
        ("guide_sam", "I need guidance on my goals"),
        ("coach_emma", "Help me with leadership challenges"),
        ("billy_corgan", "I'm struggling with creative blocks")
    ]
    
    print("✅ Testing all personas with fallback provider:")
    
    for persona_id, message in test_cases:
        if persona_id in engine.personas:
            persona = engine.personas[persona_id]
            result = await fallback_provider.get_response(persona, message)
            
            assert result["success"] == True, f"Fallback should always succeed for {persona_id}"
            assert "persona_data_used" in result, f"Should indicate persona data usage for {persona_id}"
            assert result["persona_data_used"] == True, f"Should use persona data for {persona_id}"
            
            response = result["response"]
            persona_name = persona["name"]
            
            # Check that the response includes the persona's name
            assert persona_name in response, f"Response should include persona name for {persona_id}: {response}"
            
            print(f"   ✓ {persona_id} ({persona_name}): {response[:80]}...")
        else:
            print(f"   ⚠ Persona {persona_id} not found in engine")
    
    print("🎯 Persona data integration test PASSED!")

async def test_fallback_unknown_persona():
    """Test graceful handling of unknown persona IDs (DEV-502)"""
    print("Testing Unknown Persona Handling...")
    
    from providers.hardcoded_fallback import HardcodedFallbackProvider
    
    fallback_provider = HardcodedFallbackProvider()
    
    # Create a fake unknown persona
    unknown_persona = {
        "id": "unknown_test_persona",
        "name": "Unknown Test Person",
        "description": "A test persona that doesn't exist in the system",
        "tone": "neutral and helpful",
        "background": "This persona is for testing unknown persona handling",
        "approach": "I provide helpful responses even when unknown."
    }
    
    result = await fallback_provider.get_response(unknown_persona, "Hello, can you help me?")
    
    assert result["success"] == True, "Fallback should always succeed even for unknown personas"
    assert "Unknown Test Person" in result["response"], "Should use the persona name from the data"
    assert "jane" not in result["response"].lower(), "Should NOT default to Jane for unknown personas"
    
    print(f"   ✓ Unknown persona handled gracefully: {result['response'][:80]}...")
    print("🎯 Unknown persona handling test PASSED!")

async def test_fallback_neural_context():
    """Test that fallback provider handles neural context properly"""
    print("Testing Neural Context Integration...")
    
    from providers.hardcoded_fallback import HardcodedFallbackProvider
    from core.valis_engine import VALISEngine
    
    engine = VALISEngine()
    fallback_provider = HardcodedFallbackProvider()
    
    # Use Jane persona for this test
    persona = engine.personas["jane"]
    
    # Create mock neural context
    neural_context = {
        "conversation_summary": "Previous conversation context: User mentioned team conflicts and stress management needs",
        "context_source": "neural_matrix"
    }
    
    context = {
        "neural_context": neural_context,
        "session_info": {
            "request_count": 3,
            "session_continuity": "This is request #3 in this session"
        }
    }
    
    result = await fallback_provider.get_response(persona, "I need more help", context=context)
    
    assert result["success"] == True, "Fallback should succeed with neural context"
    assert result["neural_context_used"] == True, "Should indicate neural context was used"
    assert result["context_handoff_successful"] == True, "Should indicate successful context handoff"
    
    response = result["response"]
    assert "previous conversations" in response.lower(), f"Should mention previous conversations: {response}"
    
    print(f"   ✓ Neural context integrated: {response[:100]}...")
    print("🎯 Neural context integration test PASSED!")

async def test_fallback_emergency_mode():
    """Test emergency fallback when persona data fails"""
    print("Testing Emergency Fallback Mode...")
    
    from providers.hardcoded_fallback import HardcodedFallbackProvider
    
    fallback_provider = HardcodedFallbackProvider()
    
    # Create a broken persona that will cause template formatting to fail
    broken_persona = {
        "id": "broken_persona",
        "name": None,  # This will cause issues
        "description": None,
        "language_patterns": {
            "common_phrases": []
        }
    }
    
    result = await fallback_provider.get_response(broken_persona, "Hello")
    
    assert result["success"] == True, "Even emergency fallback should succeed"
    assert "I'm here to help you" in result["response"], "Should provide emergency response"
    
    print(f"   ✓ Emergency fallback worked: {result['response']}")
    print("🎯 Emergency fallback test PASSED!")

async def main():
    """Run all fallback enhancement tests"""
    print("🚀 VALIS Sprint 1, Task 5: Hardcoded Fallback Enhancement Tests\n")
    
    try:
        await test_fallback_persona_data()
        print()
        await test_fallback_unknown_persona()
        print()
        await test_fallback_neural_context()
        print()
        await test_fallback_emergency_mode()
        
        print("\n✅ ALL FALLBACK ENHANCEMENT TESTS PASSED!")
        print("🎯 Sprint 1, Task 5 - COMPLETE!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)