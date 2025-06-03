#!/usr/bin/env python3
"""VALIS Persistent MCP Integration Test"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from core.valis_engine import VALISEngine

async def test_integration():
    print("=== VALIS Persistent MCP Integration Test ===")
    
    try:
        engine = VALISEngine()
        print("[PASS] VALIS engine initialized")
    except Exception as e:
        print(f"[FAIL] Engine init failed: {e}")
        return False
    
    test_cases = [("jane", "Test message"), ("emma", "Coach me")]
    persistent_count = 0
    
    for persona_id, message in test_cases:
        try:
            response = await engine.get_persona_response(persona_id=persona_id, message=message)
            if response.get("success"):
                provider = response.get("provider", "Unknown")
                print(f"[PASS] {persona_id} -> {provider}")
                if "Persistent" in provider:
                    persistent_count += 1
            else:
                print(f"[FAIL] {persona_id}: {response.get('error')}")
        except Exception as e:
            print(f"[FAIL] {persona_id}: {e}")
    
    print(f"\nResult: {persistent_count}/{len(test_cases)} used persistent MCP")
    
    if persistent_count > 0:
        print("[SUCCESS] Persistent MCP integration working!")
        return True
    else:
        print("[WARNING] No persistent MCP usage detected")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_integration())
    sys.exit(0 if success else 1)
