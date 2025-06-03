#!/usr/bin/env python3
"""Test MCP External Memory System"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.memory_mcp_bridge import create_mcp_memory_bridge
from core.mcp_valis_engine import create_mcp_valis_engine

def test_mcp_system():
    print("Testing MCP External Memory System...")
    
    # Test memory bridge
    bridge = create_mcp_memory_bridge()
    
    # Test Jane validation
    jane_status = bridge.validate_memory_paths("jane")
    print(f"Jane memory validation: {jane_status['memory_file_exists']}")
    
    # Test external memory read
    memory_result = bridge.read_memory_external("jane")
    print(f"External memory read: {'success' in memory_result}")
    
    # Test MCP engine
    engine = create_mcp_valis_engine()
    init_result = engine.initialize_persona("jane")
    print(f"Jane initialization: {init_result['ready']}")
    
    # Test minimal prompt
    prompt = engine.process_message("jane", "Hello Jane", "test_client")
    print(f"Minimal prompt length: {len(prompt)} chars")
    print("Preview:", prompt[:100] + "...")
    
    return True

if __name__ == "__main__":
    test_mcp_system()
