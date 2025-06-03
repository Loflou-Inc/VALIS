#!/usr/bin/env python3
"""Direct API test to bypass route issues"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.valis_memory import MemoryRouter

def test_direct_memory():
    """Test memory router directly"""
    memory_router = MemoryRouter()
    
    memory_payload = memory_router.get_memory_payload(
        persona_id="jane",
        client_id="test_client",
        current_message="Test"
    )
    
    print("DIRECT MEMORY TEST:")
    print(f"Core biography: {len(memory_payload.get('core_biography', {}))}")
    print(f"Canon entries: {len(memory_payload.get('canonized_identity', []))}")
    print(f"Client facts: {len(memory_payload.get('client_profile', {}).get('facts', {}))}")
    print(f"Working memory: {len(memory_payload.get('working_memory', []))}")
    
    return memory_payload

if __name__ == "__main__":
    test_direct_memory()
