"""API Provider Test - Fixed Imports"""
import asyncio
import sys
from pathlib import Path

valis_root = Path(__file__).parent
sys.path.insert(0, str(valis_root))

async def test_api_providers():
    print("API PROVIDER TEST - FIXED IMPORTS")
    print("="*40)
    
    # Test provider imports with correct syntax
    try:
        from providers.anthropic_provider import AnthropicProvider
        print("[PASS] AnthropicProvider imported")
        anthropic = AnthropicProvider()
        available = await anthropic.is_available()
        print(f"[INFO] Anthropic available: {available}")
    except ImportError as e:
        print(f"[FAIL] AnthropicProvider: {e}")
    
    try:
        from providers.openai_provider import OpenAIProvider
        print("[PASS] OpenAIProvider imported")
        openai = OpenAIProvider()
        available = await openai.is_available()
        print(f"[INFO] OpenAI available: {available}")
    except ImportError as e:
        print(f"[FAIL] OpenAIProvider: {e}")
    
    # Test VALIS integration
    from core.valis_engine import VALISEngine
    
    engine = VALISEngine()
    providers = [p.__class__.__name__ for p in engine.provider_manager.providers]
    print(f"[INFO] Loaded providers: {len(providers)}")
    
    result = await engine.get_persona_response("jane", "Test integration")
    print(f"[INFO] Response via: {result.get('provider_used')}")
    print("API PROVIDER TESTS COMPLETE!")

if __name__ == "__main__":
    asyncio.run(test_api_providers())