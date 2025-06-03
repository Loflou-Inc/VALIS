#!/usr/bin/env python3
"""
VALIS Prompt Render Test Tool - Sprint 7
Debug and preview tool for prompt composition

Shows exactly what prompt will be sent to Claude with full memory context.
Essential for debugging memory integration and template issues.
"""

import json
import sys
from pathlib import Path

# Add VALIS root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.valis_memory import MemoryRouter
from core.prompt_composer import PromptComposer

def test_prompt_render(persona_id="jane", client_id="user_123", 
                      user_message="I'm being talked over in meetings again.",
                      persona_override=None):
    """
    Main test function - shows complete prompt composition process
    Sprint 7.5: Added persona_override parameter
    """
    print("*** VALIS Prompt Render Test - Sprint 7.5 Enhanced ***")
    print("=" * 60)
    print()
    
    # Sprint 7.5: Handle persona override
    if persona_override:
        print(f">>> PERSONA OVERRIDE: Using {persona_override} instead of {persona_id}")
        persona_id = persona_override
    
    # Initialize components
    memory_router = MemoryRouter()
    prompt_composer = PromptComposer()
    
    # Create test session history
    test_session = [
        {"role": "user", "content": "Hi Jane, I need help with workplace issues"},
        {"role": "assistant", "content": "Of course! I'm here to help. What specific challenges are you facing?"},
        {"role": "user", "content": "My team keeps interrupting me during meetings"}
    ]
    
    print(f">>> Loading memory for persona: {persona_id}")
    print(f">>> Client: {client_id}")
    print(f">>> User message: {user_message}")
    print()
    
    # Get memory payload
    memory_payload = memory_router.get_memory_payload(
        persona_id=persona_id,
        client_id=client_id,
        session_history=test_session,
        current_message=user_message
    )
    
    print("MEMORY PAYLOAD LOADED:")
    print("-" * 25)
    print(f"Persona ID: {memory_payload['persona_id']}")
    print(f"Core bio available: {bool(memory_payload['core_biography'])}")
    print(f"Canon entries: {len(memory_payload['canonized_identity'])}")
    print(f"Client facts: {len(memory_payload.get('client_profile', {}).get('facts', {}))}")
    print(f"Working memories: {len(memory_payload['working_memory'])}")
    print(f"Session history: {len(memory_payload['session_history'])}")
    print()
    
    # Compose prompt
    print(">>> Composing prompt with PromptComposer...")
    final_prompt = prompt_composer.compose_prompt(memory_payload)
    
    # Get debug info
    debug_info = prompt_composer.debug_prompt_composition(memory_payload)
    
    print("FORMATTED COMPONENTS:")
    print("-" * 25)
    for component, content in debug_info['formatted_components'].items():
        content_preview = str(content)[:100] + "..." if len(str(content)) > 100 else str(content)
        print(f"{component}: {content_preview}")
    print()
    
    print("PROMPT STATISTICS:")
    print("-" * 20)
    stats = debug_info['prompt_stats']
    for stat, value in stats.items():
        print(f"{stat}: {value}")
    print()
    
    print("FINAL PROMPT FOR CLAUDE:")
    print("=" * 30)
    print(final_prompt)
    print("=" * 30)
    print()
    
    # Test different scenarios
    print(">>> Testing edge cases...")
    test_edge_cases(memory_router, prompt_composer)
    
    return final_prompt

def test_edge_cases(memory_router, prompt_composer):
    """Test prompt composition with various edge cases"""
    
    edge_cases = [
        {
            "name": "Empty Memory",
            "persona_id": "nonexistent",
            "client_id": None,
            "message": "Hello"
        },
        {
            "name": "Long Message", 
            "persona_id": "jane",
            "client_id": "user_123",
            "message": "This is a very long message " * 50
        },
        {
            "name": "Special Characters",
            "persona_id": "jane", 
            "client_id": "user_123",
            "message": "Help with unicode: 🤔 and 'quotes' and \"double quotes\""
        }
    ]
    
    print("EDGE CASE TESTING:")
    print("-" * 20)
    
    for case in edge_cases:
        print(f"Testing: {case['name']}")
        
        try:
            memory_payload = memory_router.get_memory_payload(
                persona_id=case['persona_id'],
                client_id=case['client_id'],
                session_history=[],
                current_message=case['message']
            )
            
            prompt = prompt_composer.compose_prompt(memory_payload)
            stats = prompt_composer.get_prompt_stats(prompt)
            
            print(f"  [PASS] Length: {stats['character_count']} chars, {stats['word_count']} words")
            
        except Exception as e:
            print(f"  [FAIL] Error: {str(e)[:50]}...")
    
    print()

def compare_templates():
    """Compare different template outputs"""
    print("TEMPLATE COMPARISON:")
    print("-" * 25)
    
    # Create test payload
    memory_router = MemoryRouter()
    memory_payload = memory_router.get_memory_payload(
        persona_id="jane",
        client_id="user_123", 
        current_message="Test message"
    )
    
    composer = PromptComposer()
    
    # Test default template
    default_prompt = composer.compose_prompt(memory_payload)
    default_stats = composer.get_prompt_stats(default_prompt)
    
    print(f"Default template: {default_stats['word_count']} words, {default_stats['character_count']} chars")
    
    # Could test other templates here if we create them
    print()

def export_prompt_sample(output_file="prompt_sample.txt"):
    """Export a sample prompt for review"""
    print(f">>> Exporting sample prompt to {output_file}...")
    
    memory_router = MemoryRouter()
    composer = PromptComposer()
    
    memory_payload = memory_router.get_memory_payload(
        persona_id="jane",
        client_id="user_123",
        session_history=[
            {"role": "user", "content": "Hi Jane"},
            {"role": "assistant", "content": "Hello! How can I help?"}
        ],
        current_message="I'm having team conflicts and need advice"
    )
    
    prompt = composer.compose_prompt(memory_payload)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("VALIS PROMPT SAMPLE - Sprint 7\n")
            f.write("=" * 40 + "\n\n")
            f.write(prompt)
        
        print(f"Sample exported to {output_file}")
        return True
        
    except Exception as e:
        print(f"Export failed: {e}")
        return False

def interactive_mode():
    """Interactive prompt testing mode"""
    print("*** INTERACTIVE PROMPT TESTING ***")
    print("Type 'quit' to exit")
    print()
    
    memory_router = MemoryRouter()
    composer = PromptComposer()
    
    while True:
        try:
            persona_id = input("Persona ID (default: jane): ").strip() or "jane"
            client_id = input("Client ID (default: user_123): ").strip() or "user_123"
            message = input("User message: ").strip()
            
            if message.lower() == 'quit':
                break
            
            if not message:
                print("Please enter a message")
                continue
            
            print("\n" + "="*50)
            
            memory_payload = memory_router.get_memory_payload(
                persona_id=persona_id,
                client_id=client_id,
                current_message=message
            )
            
            prompt = composer.compose_prompt(memory_payload)
            stats = composer.get_prompt_stats(prompt)
            
            print(f"Generated prompt ({stats['word_count']} words):")
            print("-" * 30)
            print(prompt)
            print("="*50)
            print()
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main CLI interface with Sprint 7.5 persona override support"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VALIS Prompt Render Test Tool")
    parser.add_argument("command", nargs="?", choices=["interactive", "export", "compare", "test"], 
                       help="Command to run")
    parser.add_argument("--persona", "-p", default="jane", 
                       help="Persona ID to use (overrides message targeting)")
    parser.add_argument("--client", "-c", default="user_123", 
                       help="Client ID for testing")
    parser.add_argument("--message", "-m", default="I need help with something", 
                       help="Test message")
    parser.add_argument("--force-persona", action="store_true",
                       help="Force persona override even if message has targeting")
    
    args = parser.parse_args()
    
    if args.command == "interactive":
        interactive_mode()
    elif args.command == "export":
        export_prompt_sample()
    elif args.command == "compare":
        compare_templates()
    elif args.command == "test":
        persona_override = args.persona if args.force_persona else None
        test_prompt_render(args.persona, args.client, args.message, persona_override)
    else:
        # Default demo with persona override support
        persona_override = args.persona if args.force_persona or args.persona != "jane" else None
        test_prompt_render(args.persona, args.client, args.message, persona_override)

if __name__ == "__main__":
    main()
