"""
VALIS Installation Verification Script
Tests pip install and validates all dependencies work correctly
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    print("Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"   [FAIL] Python {version.major}.{version.minor} not supported. Requires Python 3.8+")
        return False
    
    print(f"   [PASS] Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install VALIS dependencies"""
    print("Installing VALIS dependencies...")
    
    # Check if requirements.txt exists
    req_file = Path(__file__).parent / "requirements.txt"
    if not req_file.exists():
        print("   [FAIL] requirements.txt not found!")
        return False
    
    try:
        # Install requirements
        cmd = [sys.executable, "-m", "pip", "install", "-r", str(req_file)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("   [PASS] Dependencies installed successfully")
            return True
        else:
            print(f"   [FAIL] Installation failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   [FAIL] Installation timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"   [FAIL] Installation error: {e}")
        return False

def verify_critical_imports():
    """Verify all critical dependencies can be imported"""
    print("Verifying critical imports...")
    
    critical_imports = [
        ("aiohttp", "HTTP client for API providers"),
        ("asyncio", "Async support"),
        ("json", "JSON handling"),
        ("pathlib", "Path operations"),
    ]
    
    all_passed = True
    
    for module_name, description in critical_imports:
        try:
            __import__(module_name)
            print(f"   [PASS] {module_name}: {description}")
        except ImportError as e:
            print(f"   [FAIL] {module_name}: {e}")
            all_passed = False
    
    return all_passed

def test_valis_functionality():
    """Test that VALIS works after installation"""
    print("Testing VALIS functionality...")
    
    # Add current directory to path
    valis_root = Path(__file__).parent
    sys.path.insert(0, str(valis_root))
    
    try:
        # Test basic imports
        from core import VALISEngine
        print("   [PASS] VALIS core imports successful")
        
        # Test provider imports with dependencies
        from providers import AnthropicProvider, OpenAIProvider
        if AnthropicProvider is not None:
            print("   [PASS] AnthropicProvider available")
        if OpenAIProvider is not None:
            print("   [PASS] OpenAIProvider available")
        
        # Test engine initialization
        engine = VALISEngine()
        print("   [PASS] VALISEngine initialization successful")
        
        # Test provider availability
        provider_manager = engine.provider_manager
        providers = [p.__class__.__name__ for p in provider_manager.providers]
        print(f"   [INFO] Available providers: {providers}")
        
        return True
        
    except Exception as e:
        print(f"   [FAIL] VALIS functionality test failed: {e}")
        return False

async def test_async_functionality():
    """Test async functionality works"""
    print("Testing async functionality...")
    
    try:
        from core import VALISEngine
        
        engine = VALISEngine()
        result = await engine.get_persona_response("jane", "Installation test message")
        
        if result.get("success"):
            print(f"   [PASS] Async test successful: {result.get('provider_used')}")
            return True
        else:
            print(f"   [FAIL] Async test failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Async test exception: {e}")
        return False

def main():
    """Run complete installation verification"""
    print("VALIS INSTALLATION VERIFICATION")
    print("="*50)
    
    # Run verification steps
    steps = [
        check_python_version,
        install_dependencies,
        verify_critical_imports,
        test_valis_functionality
    ]
    
    all_passed = True
    
    for step in steps:
        try:
            passed = step()
            if not passed:
                all_passed = False
            print()
        except Exception as e:
            print(f"   [ERROR] Step failed: {e}")
            all_passed = False
            print()
    
    # Test async functionality
    try:
        import asyncio
        print("Testing async functionality...")
        passed = asyncio.run(test_async_functionality())
        if not passed:
            all_passed = False
        print()
    except Exception as e:
        print(f"   [ERROR] Async test failed: {e}")
        all_passed = False
        print()
    
    if all_passed:
        print("INSTALLATION VERIFICATION SUCCESS!")
        print("VALIS is ready for use!")
        print()
        print("Next steps:")
        print("1. Set API keys (optional): ANTHROPIC_API_KEY, OPENAI_API_KEY")
        print("2. Run: python -c \"from core import VALISEngine; engine = VALISEngine()\"")
        print("3. Ready for Sprint 3: Provider Implementation!")
    else:
        print("INSTALLATION VERIFICATION FAILED!")
        print("Some components need attention.")
        print("Check error messages above for details.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)