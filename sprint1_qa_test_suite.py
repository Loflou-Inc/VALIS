"""SPRINT 1 QA Test Suite - Simple"""
import asyncio
import json
import tempfile
import sys
import os
from pathlib import Path

valis_root = Path(__file__).parent
sys.path.insert(0, str(valis_root))

async def run_qa_tests():
    print("SPRINT 1 QA TEST SUITE")
    print("="*50)
    
    from core.valis_engine import VALISEngine
    
    # QA-701: Provider Cascade Test
    print("QA-701: Provider Cascade Test")
    engine = VALISEngine()
    result = await engine.get_persona_response("jane", "Test cascade")
    print(f"   Normal cascade: {result.get('provider_used')}")
    
    # Force fallback test
    config = {"providers": ["hardcoded_fallback"], "enable_memory": False}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_path = f.name
    
    try:
        fallback_engine = VALISEngine(config_path=temp_path)
        fallback_result = await fallback_engine.get_persona_response("jane", "Test fallback")
        print(f"   Fallback cascade: {fallback_result.get('provider_used')}")
    finally:
        os.unlink(temp_path)
    
    # QA-702: Persona Switch Test
    print("QA-702: Persona Switch Test")
    session_id = "qa_test_session"
    
    for persona_id in ["jane", "advisor_alex", "guide_sam"]:
        result = await engine.get_persona_response(persona_id, f"Hello {persona_id}", session_id=session_id)
        print(f"   {persona_id}: {result.get('success')}")
    
    print(f"   Sessions: {engine.health_check().get('active_sessions')}")
    
    # QA-703: Config Test
    print("QA-703: Config Test")
    from core.config_validator import VALISConfigValidator
    
    # Test broken config
    broken_config = {"max_concurrent_requests": "invalid", "unknown_key": "should_ignore"}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(broken_config, f)
        temp_path = f.name
    
    try:
        validated_config = VALISConfigValidator.validate_and_load_config(temp_path)
        print(f"   Config validation: max_concurrent_requests = {validated_config.get('max_concurrent_requests')}")
        print(f"   Unknown keys ignored: {'unknown_key' not in validated_config}")
    finally:
        os.unlink(temp_path)
    
    # QA-704: Memory Integration Test
    print("QA-704: Memory Integration Test")
    result = await engine.get_persona_response("jane", "Test memory integration")
    health = engine.health_check()
    print(f"   Memory enabled: {health.get('memory_enabled')}")
    print(f"   Memory connected: {health.get('memory_connected')}")
    
    print("\nSPRINT 1 QA TESTS COMPLETE!")

if __name__ == "__main__":
    asyncio.run(run_qa_tests())