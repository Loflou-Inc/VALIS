#!/usr/bin/env python3
"""
MCP-Enhanced VALIS Engine
Uses external memory files instead of in-memory dumps
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from core.memory_mcp_bridge import create_mcp_memory_bridge
from core.minimal_prompt_composer_clean import MinimalPromptComposer

logger = logging.getLogger(__name__)

class MCPVALISEngine:
    """
    VALIS Engine with MCP Desktop Commander integration
    External file-based memory system
    """
    
    def __init__(self, valis_root: str = None):
        self.valis_root = Path(valis_root) if valis_root else Path(__file__).parent.parent
        
        # Initialize MCP components
        self.memory_bridge = create_mcp_memory_bridge(str(self.valis_root))
        self.prompt_composer = MinimalPromptComposer(str(self.valis_root))
        
        # Memory cache for active personas
        self.memory_cache = {}
        
        logger.info("MCP VALIS Engine initialized")
    
    def initialize_persona(self, persona_id: str) -> Dict[str, Any]:
        """Initialize persona with external memory validation"""
        
        # Validate memory paths and scripts
        validation = self.memory_bridge.validate_memory_paths(persona_id)
        
        # Load external memory
        memory_result = self.memory_bridge.read_memory_external(persona_id)
        
        # Cache memory if successful
        if "data" in memory_result:
            self.memory_cache[persona_id] = {
                "data": memory_result["data"],
                "last_loaded": memory_result["last_read"],
                "source": memory_result["source"]
            }
        
        return {
            "persona_id": persona_id,
            "validation": validation,
            "memory_loaded": "data" in memory_result,
            "external_scripts_ok": all(validation["bat_scripts_exist"].values()),
            "ready": validation["memory_file_exists"] and "data" in memory_result
        }
    
    def get_startup_prompt(self, persona_id: str) -> str:
        """Get startup protocol for persona"""
        return self.prompt_composer.get_startup_prompt(persona_id)
    
    def process_message(self, persona_id: str, message: str, 
                       client_id: str = "default", 
                       session_id: str = None) -> str:
        """Process message with minimal prompt - memory loaded externally"""
        
        # Create minimal prompt (no memory dumps)
        prompt = self.prompt_composer.create_minimal_prompt(
            persona_id=persona_id,
            message=message,
            client_id=client_id,
            session_id=session_id
        )
        
        return prompt
    
    def get_memory_status(self, persona_id: str) -> Dict[str, Any]:
        """Get memory system status for diagnostics"""
        return self.memory_bridge.get_memory_status(persona_id)
    
    def update_memory(self, content: str) -> Dict[str, Any]:
        """Update memory using external script"""
        return self.memory_bridge.update_memory_external(content)
    
    def handle_dev_command(self, command: str, persona_id: str) -> str:
        """Handle dev introspection commands"""
        if command == "memory_status":
            status = self.get_memory_status(persona_id)
            return f"Memory Status for {persona_id}: {status}"
        elif command == "persona_summary":
            if persona_id in self.memory_cache:
                memory_data = self.memory_cache[persona_id]["data"]
                total_memories = len(memory_data.get("memories", []))
                return f"Persona {persona_id}: {total_memories} memories loaded from external file"
            else:
                return f"Persona {persona_id}: No memory cache loaded"
        else:
            return f"Unknown dev command: {command}"


# Factory function
def create_mcp_valis_engine(valis_root: str = None) -> MCPVALISEngine:
    """Create MCP VALIS Engine instance"""
    return MCPVALISEngine(valis_root)
