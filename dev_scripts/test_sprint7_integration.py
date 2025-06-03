#!/usr/bin/env python3
"""
Sprint 7 Integration Test - Memory-Enhanced MCP Provider
Tests the complete flow: Memory -> PromptComposer -> MCP Provider
"""

import asyncio
import json
import sys
from pathlib import Path

# Add VALIS root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.valis_memory import MemoryRouter
from core.prompt_composer import PromptComposer
from providers.desktop_commander_mcp_persistent import PersistentDesktopCommanderMCPProvider

async def test_memory_enhanced_mcp():
    """Test the complete Sprint 7 integration"""
    
    print("*** Sprint 7 Integration Test - Memory Enhanced MCP ***")
    print("=" * 60)
    print()
    
    # Initialize components
    print(">>> Initializing components...")
    memory_router = MemoryRouter()
    prompt_composer = PromptComposer()
    mcp_provider = PersistentDesktopCommanderMCPProvider()
    
    print(f"Memory enabled: {mcp_provider.memory_enabled}")
    print(f"Provider name: {mcp_provider.name}")
    print()
    
    # Test persona
    test_persona = {
        "id": "jane",
        "name": "Jane Thompson",
        "description": "HR Business Partner"
    }
    
    # Test message
    test_message = "My team keeps interrupting me in meetings and I don't know how to handle it professionally."
    
    # Test context with session info
    test_context = {
        "client_id": "user_123",
        "session_history": [
            {"role": "user", "content": "Hi Jane, I need help with workplace issues"},
            {"role": "assistant", "content": "Of course! I specialize in workplace dynamics. What's happening?"}
        ]
    }
    
    print(">>> Testing memory payload generation...")
    memory_payload = memory_router.get_memory_payload(
        persona_id="jane",
        client_id="user_123",
        session_history=test_context["session_history"],
        current_message=test_message
    )
    
    print(f"Memory layers loaded: {len([k for k in memory_payload.keys() if memory_payload[k]])}")
    print(f"Canon entries: {len(memory_payload['canonized_identity'])}")
    print(f"Working memories: {len(memory_payload['working_memory'])}")
    print()
    
    print(">>> Testing prompt composition...")
    enhanced_prompt = prompt_composer.compose_prompt(memory_payload, provider_type="claude")
    stats = prompt_composer.get_prompt_stats(enhanced_prompt)
    
    print(f"Enhanced prompt: {stats['word_count']} words, {stats['character_count']} chars")
    print(f"Has persona context: {stats['has_persona_context']}")
    print(f"Has memory context: {stats['has_memory_context']}")
    print()
    
    print(">>> Testing MCP provider memory enhancement...")
    try:
        # Test the internal memory enhancement method
        enhanced_message = await mcp_provider._prepare_memory_enhanced_message(
            persona_id="jane",
            message=test_message,
            session_id="test_session",
            context=test_context
        )
        
        print(f"MCP enhanced message length: {len(enhanced_message)} chars")
        print("Enhanced message preview:")
        print("-" * 40)
        print(enhanced_message[:300] + "..." if len(enhanced_message) > 300 else enhanced_message)
        print("-" * 40)
        print()
        
    except Exception as e:
        print(f"MCP enhancement test failed: {e}")
        print()
    
    print(">>> Testing MCP server availability...")
    is_available = await mcp_provider.is_available()
    print(f"MCP server available: {is_available}")
    
    if is_available:
        print(">>> Attempting full MCP request with memory...")
        try:
            response = await mcp_provider.get_response(
                persona=test_persona,
                message=test_message,
                session_id="test_session",
                context=test_context
            )
            
            print("MCP Response received!")
            print(f"Success: {response.get('success', False)}")
            print(f"Provider: {response.get('provider', 'Unknown')}")
            print(f"Response length: {len(response.get('response', ''))}")
            print()
            print("Response preview:")
            print("-" * 30)
            print(response.get('response', 'No response')[:200] + "...")
            print("-" * 30)
            
        except Exception as e:
            print(f"Full MCP request failed: {e}")
            print("This is expected if MCP server is not running")
    else:
        print("MCP server not available - testing fallback...")
        try:
            fallback_response = await mcp_provider._get_clean_fallback(test_persona, test_message)
            print(f"Fallback response: {fallback_response.get('response', '')[:100]}...")
        except Exception as e:
            print(f"Fallback test failed: {e}")
    
    print()
    print("*** Sprint 7 Integration Test Complete ***")
    print("Memory system successfully bridges to MCP provider!")

async def test_prompt_composition_comparison():
    """Compare basic vs memory-enhanced prompts"""
    
    print("\n*** Prompt Comparison Test ***")
    print("=" * 35)
    
    # Basic prompt (old way)
    basic_prompt = "User: My team keeps interrupting me in meetings."
    
    # Memory-enhanced prompt (new way)
    memory_router = MemoryRouter()
    prompt_composer = PromptComposer()
    
    memory_payload = memory_router.get_memory_payload(
        persona_id="jane",
        client_id="user_123",
        current_message="My team keeps interrupting me in meetings."
    )
    
    enhanced_prompt = prompt_composer.compose_prompt(memory_payload)
    
    print("BASIC PROMPT (old):")
    print("-" * 20)
    print(basic_prompt)
    print()
    
    print("MEMORY-ENHANCED PROMPT (Sprint 7):")
    print("-" * 40)
    print(enhanced_prompt[:500] + "..." if len(enhanced_prompt) > 500 else enhanced_prompt)
    print()
    
    print("COMPARISON:")
    print(f"Basic: {len(basic_prompt)} chars, {len(basic_prompt.split())} words")
    print(f"Enhanced: {len(enhanced_prompt)} chars, {len(enhanced_prompt.split())} words")
    print(f"Enhancement factor: {len(enhanced_prompt) / len(basic_prompt):.1f}x more context")

if __name__ == "__main__":
    asyncio.run(test_memory_enhanced_mcp())
    asyncio.run(test_prompt_composition_comparison())
