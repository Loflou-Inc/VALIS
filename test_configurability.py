"""
Test configurability improvements for VALIS
Tests Task 4 of Sprint 1: Configuration validation and usage
"""

import asyncio
import json
import tempfile
import sys
import os
from pathlib import Path

# Add VALIS root to path
valis_root = Path(__file__).parent
sys.path.insert(0, str(valis_root))

async def test_config_validation():
    """Test configuration validation and schema enforcement"""
    print("🔧 Testing VALIS Configuration Validation...")
    
    from core.config_validator import VALISConfigValidator
    
    # Test 1: Default configuration
    print("✅ Test 1: Default configuration")
    default_config = VALISConfigValidator.validate_and_load_config()
    
    expected_keys = [
        'max_concurrent_requests', 'provider_timeout', 'circuit_breaker_threshold',
        'circuit_breaker_timeout', 'retry_schedule', 'session_timeout'
    ]
    
    for key in expected_keys:
        assert key in default_config, f"Missing config key: {key}"
        print(f"   ✓ {key}: {default_config[key]}")
    
    # Test 2: Custom configuration with validation
    print("✅ Test 2: Custom configuration validation")
    
    # Create a temporary config file with some invalid values
    custom_config = {
        "max_concurrent_requests": 150,  # Above max (100)
        "provider_timeout": 0.5,         # Below min (1.0)
        "circuit_breaker_threshold": 5,  # Valid
        "logging_level": "INVALID",      # Invalid value
        "session_timeout": 600,          # Valid
        "unknown_key": "should_be_ignored"  # Unknown key
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(custom_config, f)
        temp_config_path = f.name
    
    try:
        validated_config = VALISConfigValidator.validate_and_load_config(temp_config_path)
        
        # Check that values were corrected
        assert validated_config['max_concurrent_requests'] == 100, "Max concurrent requests should be clamped to 100"
        assert validated_config['provider_timeout'] == 1.0, "Provider timeout should be clamped to 1.0"
        assert validated_config['circuit_breaker_threshold'] == 5, "Circuit breaker threshold should be preserved"
        assert validated_config['logging_level'] == "INFO", "Invalid logging level should default to INFO"
        assert validated_config['session_timeout'] == 600, "Session timeout should be preserved"
        assert 'unknown_key' not in validated_config, "Unknown keys should be ignored"
        
        print("   ✓ Values corrected properly by validation")
        
    finally:
        os.unlink(temp_config_path)
    
    print("🎯 Configuration validation tests PASSED!")

async def test_valis_with_config():
    """Test VALIS engine using configuration values"""
    print("🚀 Testing VALIS with Configuration...")
    
    # Create custom config
    custom_config = {
        "max_concurrent_requests": 5,
        "provider_timeout": 10.0,
        "circuit_breaker_threshold": 2,
        "session_timeout": 900,
        "enable_memory": False  # Disable memory for this test
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(custom_config, f)
        temp_config_path = f.name
    
    try:
        # Initialize VALIS with custom config
        from core.valis_engine import VALISEngine
        engine = VALISEngine(config_path=temp_config_path)
        
        # Check that provider manager got the config
        provider_manager = engine.provider_manager
        
        assert provider_manager.request_semaphore._value == 5, "Max concurrent requests should be 5"
        assert provider_manager.provider_timeout == 10.0, "Provider timeout should be 10.0"
        assert provider_manager.circuit_breaker_threshold == 2, "Circuit breaker threshold should be 2"
        assert engine.session_timeout == 900, "Session timeout should be 900"
        
        print("   ✓ VALIS engine properly uses configuration values")
        
        # Test a simple persona response to ensure everything still works
        personas = engine.get_available_personas()
        if personas:
            persona_id = personas[0]['id']
            result = await engine.get_persona_response(persona_id, "Test configurability message")
            
            assert 'success' in result, "Should get a response"
            print(f"   ✓ Persona response works: {result.get('success')}")
        
    finally:
        os.unlink(temp_config_path)
    
    print("🎯 VALIS configuration integration tests PASSED!")

async def main():
    """Run all configurability tests"""
    print("🚀 VALIS Sprint 1, Task 4: Configurability Improvements Test\n")
    
    try:
        await test_config_validation()
        print()
        await test_valis_with_config()
        
        print("\n✅ ALL CONFIGURABILITY TESTS PASSED!")
        print("🎯 Sprint 1, Task 4 - COMPLETE!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)