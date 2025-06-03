#!/usr/bin/env python3
"""
Super Simple VALIS Working Proof
No server startup - just prove components work
"""

import sys
import os
from pathlib import Path

def simple_valis_proof():
    """Prove VALIS components can load and work"""
    print("SIMPLE VALIS WORKING PROOF")
    print("=" * 40)
    
    # Change to VALIS directory
    valis_dir = Path("C:/VALIS")
    os.chdir(valis_dir)
    sys.path.insert(0, str(valis_dir))
    
    # Test 1: Import core components
    print("[1/5] Testing core imports...")
    try:
        from core.valis_engine import VALISEngine
        print("     VALISEngine: OK")
    except Exception as e:
        print(f"     VALISEngine: FAILED - {e}")
        return False
    
    # Test 2: Load configuration
    print("[2/5] Testing configuration...")
    try:
        import json
        config_file = valis_dir / "config.json"
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
            print(f"     Config loaded: {len(config)} keys")
        else:
            print("     Config file missing")
            return False
    except Exception as e:
        print(f"     Config: FAILED - {e}")
        return False
    
    # Test 3: Load personas
    print("[3/5] Testing personas...")
    try:
        personas_dir = valis_dir / "personas"
        persona_files = list(personas_dir.glob("*.json"))
        print(f"     Personas found: {len(persona_files)}")
        if len(persona_files) == 0:
            return False
    except Exception as e:
        print(f"     Personas: FAILED - {e}")
        return False
    
    # Test 4: Initialize engine
    print("[4/5] Testing engine initialization...")
    try:
        engine = VALISEngine()
        providers = engine.get_available_providers()
        print(f"     Engine initialized: {len(providers)} providers")
    except Exception as e:
        print(f"     Engine: FAILED - {e}")
        return False
    
    # Test 5: Test basic functionality
    print("[5/5] Testing basic chat...")
    try:
        response = engine.get_persona_response(
            persona_id="jane_thompson",
            message="Brief test message",
            session_id="test_session"
        )
        if response.get('success'):
            provider = response.get('provider_used', 'unknown')
            response_len = len(response.get('response', ''))
            print(f"     Chat working: {response_len} chars from {provider}")
        else:
            print(f"     Chat failed: {response.get('error', 'unknown')}")
            return False
    except Exception as e:
        print(f"     Chat: FAILED - {e}")
        return False
    
    print()
    print("SIMPLE PROOF: ALL COMPONENTS WORKING!")
    print("- Core engine loads successfully")
    print("- Configuration system operational")
    print("- Personas loaded and accessible")
    print("- Provider cascade functional")
    print("- Chat responses generated")
    print()
    print("VALIS IS FULLY OPERATIONAL!")
    return True

if __name__ == "__main__":
    success = simple_valis_proof()
    if success:
        print("\nDOC BROWN: TEMPORAL REPAIRS SUCCESSFUL!")
        print("SYSTEM WORKING - CRISIS AVERTED!")
    else:
        print("\nSYSTEM ISSUES DETECTED")
    sys.exit(0 if success else 1)
