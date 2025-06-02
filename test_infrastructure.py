"""
Sprint 2.5 Infrastructure Tests
Comprehensive testing for package structure and dependency management
"""

import asyncio
import sys
import os
from pathlib import Path

# Add VALIS root to path
valis_root = Path(__file__).parent
sys.path.insert(0, str(valis_root))

async def test_package_imports():
    """Test all package imports work correctly"""
    print("INFRA-101: Testing Package Import Structure")
    
    # Test core imports
    try:
        from core import VALISEngine, ProviderManager, VALISConfigValidator
        print("   [PASS] Core imports successful")
    except ImportError as e:
        print(f"   [FAIL] Core imports failed: {e}")
        return False
    
    # Test provider imports with graceful degradation
    try:
        from providers import DesktopCommanderProvider, HardcodedFallbackProvider
        print("   [PASS] Basic provider imports successful")
    except ImportError as e:
        print(f"   [FAIL] Basic provider imports failed: {e}")
        return False
    
    # Test API provider imports (should handle missing dependencies gracefully)
    try:
        from providers import AnthropicProvider, OpenAIProvider
        if AnthropicProvider is None:
            print("   [INFO] AnthropicProvider not available (missing dependencies)")
        else:
            print("   [PASS] AnthropicProvider import successful")
            
        if OpenAIProvider is None:
            print("   [INFO] OpenAIProvider not available (missing dependencies)")
        else:
            print("   [PASS] OpenAIProvider import successful")
    except ImportError as e:
        print(f"   [WARN] API provider imports failed: {e}")
    
    return True

async def test_provider_registration():
    """Test provider registration and availability checking"""
    print("INFRA-102: Testing Provider Registration")
    
    from core.valis_engine import VALISEngine
    
    # Initialize engine
    engine = VALISEngine()
    
    # Test provider manager initialization
    provider_manager = engine.provider_manager
    providers = [p.__class__.__name__ for p in provider_manager.providers]
    
    print(f"   [INFO] Initialized providers: {providers}")
    
    # Test availability checks
    for provider in provider_manager.providers:
        try:
            is_available = await provider.is_available()
            print(f"   [INFO] {provider.__class__.__name__}: Available = {is_available}")
        except Exception as e:
            print(f"   [WARN] {provider.__class__.__name__}: Availability check failed = {e}")
    
    # Verify fallback provider always available
    fallback_available = False
    for provider in provider_manager.providers:
        if "Fallback" in provider.__class__.__name__:
            fallback_available = await provider.is_available()
            break
    
    if fallback_available:
        print("   [PASS] Fallback provider available (system will never fail)")
    else:
        print("   [FAIL] Fallback provider not available!")
        return False
    
    return True

async def test_dependency_handling():
    """Test dependency validation and graceful degradation"""
    print("INFRA-202: Testing Dependency Validation")
    
    # Test aiohttp dependency detection
    try:
        import aiohttp
        print("   [INFO] aiohttp is installed and available")
        aiohttp_available = True
    except ImportError:
        print("   [INFO] aiohttp not available - API providers will gracefully degrade")
        aiohttp_available = False
    
    # Test provider behavior with/without dependencies
    from core.provider_manager import ProviderManager
    
    provider_manager = ProviderManager(["anthropic_api", "openai_api", "hardcoded_fallback"])
    
    working_providers = [p for p in provider_manager.providers if p is not None]
    print(f"   [INFO] Working providers: {len(working_providers)}")
    
    # Should always have at least fallback
    if len(working_providers) == 0:
        print("   [FAIL] No providers available!")
        return False
    
    print("   [PASS] Graceful degradation working")
    return True

async def test_end_to_end_functionality():
    """Test complete system functionality with current dependencies"""
    print("INFRA-402: Testing End-to-End Functionality")
    
    from core.valis_engine import VALISEngine
    
    # Test basic persona response
    engine = VALISEngine()
    
    try:
        result = await engine.get_persona_response("jane", "Test infrastructure functionality")
        
        if result.get("success"):
            print(f"   [PASS] End-to-end test successful: {result.get('provider_used')}")
            print(f"   [INFO] Response time: {result.get('response_time', 0):.3f}s")
        else:
            print(f"   [FAIL] End-to-end test failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] End-to-end test exception: {e}")
        return False
    
    # Test health check
    health = engine.health_check()
    print(f"   [INFO] System status: {health.get('status')}")
    print(f"   [INFO] Providers available: {health.get('providers_available')}")
    print(f"   [INFO] Personas loaded: {health.get('personas_loaded')}")
    
    return True

async def main():
    """Run all infrastructure tests"""
    print("SPRINT 2.5: INFRASTRUCTURE TIMELINE REPAIR")
    print("="*60)
    
    tests = [
        test_package_imports,
        test_provider_registration, 
        test_dependency_handling,
        test_end_to_end_functionality
    ]
    
    all_passed = True
    
    for test in tests:
        try:
            passed = await test()
            if not passed:
                all_passed = False
            print()
        except Exception as e:
            print(f"   [ERROR] Test failed with exception: {e}")
            all_passed = False
            print()
    
    if all_passed:
        print("SPRINT 2.5 SUCCESS: Infrastructure Timeline Restored!")
        print("Ready for Sprint 3: Provider Implementation!")
    else:
        print("SPRINT 2.5 PARTIAL: Some infrastructure issues remain")
        print("Recommend: pip install -r requirements.txt")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)