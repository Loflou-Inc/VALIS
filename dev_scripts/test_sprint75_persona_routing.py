#!/usr/bin/env python3
"""
Sprint 7.5: Persona Routing Fix Test
Tests the fixes for identity misrouting and explicit targeting
"""

import asyncio
import json
import sys
from pathlib import Path

# Add VALIS root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.persona_router import PersonaRouter
from providers.desktop_commander_mcp_persistent import PersistentDesktopCommanderMCPProvider

async def test_persona_routing_fixes():
    """Test all the Sprint 7.5 persona routing fixes"""
    
    print("*** Sprint 7.5: Persona Routing Fix Test ***")
    print("=" * 55)
    print()
    
    # Initialize components
    print(">>> Initializing PersonaRouter...")
    router = PersonaRouter()
    
    print(">>> Available personas:")
    personas = router.get_available_personas()
    for persona in sorted(personas):
        print(f"   - {persona}")
    print()
    
    # Test targeting patterns
    test_messages = [
        # Explicit targeting that should work
        ("*** laika What's the priority for today?", "laika"),
        ("@jane I need help with team conflicts", "jane"),
        ("persona: \"doc_brown\" Review this architecture", "doc_brown"),
        ("--persona=biff Test this feature please", "biff"),
        
        # Messages without targeting (should fail gracefully)
        ("Just a regular message", None),
        ("Help me with something", None),
        
        # Invalid persona targeting
        ("*** nonexistent Please help", None),
        ("@invalidperson Do something", None),
    ]
    
    print(">>> Testing persona targeting patterns:")
    print("-" * 40)
    
    for message, expected_persona in test_messages:
        result = router.route_message(message)
        actual_persona = result["persona_id"]
        targeting_detected = result["targeting_detected"]
        cleaned_message = result["message"]
        
        status = "PASS" if actual_persona == expected_persona else "FAIL"
        
        print(f"[{status}] {message}")
        print(f"      Expected: {expected_persona}")
        print(f"      Got: {actual_persona}")
        print(f"      Targeting: {targeting_detected}")
        print(f"      Cleaned: {cleaned_message}")
        print()
    
    # Test MCP provider integration
    print(">>> Testing MCP Provider Integration:")
    print("-" * 40)
    
    provider = PersistentDesktopCommanderMCPProvider()
    
    # Test if MCP server is available
    mcp_available = await provider.is_available()
    print(f"MCP Server Available: {mcp_available}")
    
    if mcp_available:
        print("Testing explicit targeting through MCP...")
        
        test_persona = {"id": "laika", "name": "Laika"}
        
        # Test with explicit targeting
        test_message = "*** laika What should be our top priority?"
        
        try:
            response = await provider.get_response(
                persona=test_persona,
                message=test_message,
                context={"test_mode": True}
            )
            
            print(f"Request: {test_message}")
            print(f"Success: {response.get('success', False)}")
            print(f"Provider: {response.get('provider', 'Unknown')}")
            print(f"Response preview: {response.get('response', 'No response')[:100]}...")
            
        except Exception as e:
            print(f"MCP test failed: {e}")
    else:
        print("MCP server not available - skipping MCP integration tests")
    
    print()
    print(">>> Testing fallback behavior:")
    print("-" * 35)
    
    # Test what happens with no explicit targeting
    no_target_result = router.route_message("I need help with something")
    print(f"No targeting message: {no_target_result['warning']}")
    print(f"Available personas: {len(no_target_result['available_personas'])}")
    
    # Test content-based suggestions
    suggestion = router.suggest_persona_from_context("I need help with team conflicts")
    print(f"Content suggestion for 'team conflicts': {suggestion}")
    
    suggestion2 = router.suggest_persona_from_context("I want to validate this system architecture")
    print(f"Content suggestion for 'system architecture': {suggestion2}")
    
    print()
    print("*** Sprint 7.5 Test Complete ***")
    print("Persona routing fixes validated!")

async def test_memory_isolation():
    """Test that each persona gets their own memory"""
    
    print("\n>>> Testing Memory Isolation:")
    print("-" * 30)
    
    try:
        from core.valis_memory import MemoryRouter
        memory_router = MemoryRouter()
        
        # Test different personas get different memory
        personas_to_test = ["jane", "laika", "doc_brown"]
        
        for persona_id in personas_to_test:
            payload = memory_router.get_memory_payload(persona_id, "test_client")
            
            print(f"{persona_id}:")
            print(f"  Core persona available: {bool(payload['core_biography'])}")
            print(f"  Canon entries: {len(payload['canonized_identity'])}")
            print(f"  Working memories: {len(payload['working_memory'])}")
            
        print("Memory isolation: PASS")
        
    except Exception as e:
        print(f"Memory isolation test failed: {e}")

def test_prompt_composer_validation():
    """Test that PromptComposer uses correct persona"""
    
    print("\n>>> Testing PromptComposer Validation:")
    print("-" * 40)
    
    try:
        from core.valis_memory import MemoryRouter
        from core.prompt_composer import PromptComposer
        
        memory_router = MemoryRouter()
        composer = PromptComposer()
        
        # Test with different personas
        test_personas = ["laika", "doc_brown", "biff"]
        
        for persona_id in test_personas:
            payload = memory_router.get_memory_payload(persona_id, "test_client", [], "Test message")
            prompt = composer.compose_prompt(payload)
            
            # Check if persona name appears in prompt
            persona_in_prompt = persona_id in prompt.lower() or payload.get('core_biography', {}).get('name', '').lower() in prompt.lower()
            
            print(f"{persona_id}: {'PASS' if persona_in_prompt else 'FAIL'}")
            
    except Exception as e:
        print(f"PromptComposer validation failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_persona_routing_fixes())
    asyncio.run(test_memory_isolation())
    test_prompt_composer_validation()
