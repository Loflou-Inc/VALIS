#!/usr/bin/env python3
"""
MCP Memory Bridge - External File-Based Memory System
Uses Desktop Commander MCP for external memory file operations
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPMemoryBridge:
    """
    External memory system using MCP file operations
    Reads/writes memory files instead of in-memory dumps
    """
    
    def __init__(self, valis_root: str = None):
        if valis_root is None:
            valis_root = Path(__file__).parent.parent
        
        self.valis_root = Path(valis_root)
        self.memory_root = self.valis_root / "memory" / "personas"
        self.bat_scripts = self.valis_root / "claude-memory-ADV" / "MEMORY_DEV"
        
        # Ensure memory directories exist
        self.memory_root.mkdir(parents=True, exist_ok=True)
        
    def validate_memory_paths(self, persona_id: str) -> Dict[str, Any]:
        """Validate memory file paths for persona"""
        persona_memory_dir = self.memory_root / persona_id
        persona_memory_file = persona_memory_dir / "memories.json"
        
        status = {
            "persona_id": persona_id,
            "memory_dir_exists": persona_memory_dir.exists(),
            "memory_file_exists": persona_memory_file.exists(),
            "memory_dir_path": str(persona_memory_dir),
            "memory_file_path": str(persona_memory_file),
            "bat_scripts_exist": {
                "read_smart": (self.bat_scripts / "read_memory_smart.bat").exists(),
                "safe_update": (self.bat_scripts / "safe_update_memory.bat").exists()
            },
            "validation_time": datetime.now().isoformat()
        }
        
        # Create memory structure if missing
        if not persona_memory_dir.exists():
            persona_memory_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created memory directory: {persona_memory_dir}")
            
        if not persona_memory_file.exists():
            # Create minimal memory structure
            initial_memory = {
                "persona_id": persona_id,
                "created": datetime.now().isoformat(),
                "memories": [],
                "metadata": {"version": "1.0", "total_memories": 0}
            }
            with open(persona_memory_file, 'w', encoding='utf-8') as f:
                json.dump(initial_memory, f, indent=2)
            logger.info(f"Created initial memory file: {persona_memory_file}")
            status["memory_file_exists"] = True
            
        return status
    
    def read_memory_external(self, persona_id: str) -> Dict[str, Any]:
        """Read memory using external MCP bat script"""
        try:
            # Run read_memory_smart.bat
            read_script = self.bat_scripts / "read_memory_smart.bat"
            if not read_script.exists():
                logger.error(f"Read script not found: {read_script}")
                return {"error": "Memory read script not available"}
            
            # Execute memory read
            result = subprocess.run(
                [str(read_script)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.valis_root)
            )
            
            if result.returncode == 0:
                logger.info("External memory read successful")
                
                # Load the memory file directly
                memory_file = self.memory_root / persona_id / "memories.json"
                if memory_file.exists():
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        memory_data = json.load(f)
                    return {
                        "success": True,
                        "source": "external_file",
                        "path": str(memory_file),
                        "data": memory_data,
                        "last_read": datetime.now().isoformat()
                    }
                else:
                    return {"error": "Memory file not found after read"}
            else:
                logger.error(f"Memory read failed: {result.stderr}")
                return {"error": f"Memory read script failed: {result.stderr}"}
                
        except Exception as e:
            logger.error(f"Error reading external memory: {e}")
            return {"error": str(e)}
    
    def update_memory_external(self, memory_content: str) -> Dict[str, Any]:
        """Update memory using external MCP bat script"""
        try:
            # Run safe_update_memory.bat with content
            update_script = self.bat_scripts / "safe_update_memory.bat"
            if not update_script.exists():
                logger.error(f"Update script not found: {update_script}")
                return {"error": "Memory update script not available"}
            
            # Execute memory update
            result = subprocess.run(
                [str(update_script), f"MEMORY: {memory_content}"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.valis_root)
            )
            
            if result.returncode == 0:
                logger.info("External memory update successful")
                return {
                    "success": True,
                    "method": "external_script",
                    "content": memory_content,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"Memory update failed: {result.stderr}")
                return {"error": f"Memory update script failed: {result.stderr}"}
                
        except Exception as e:
            logger.error(f"Error updating external memory: {e}")
            return {"error": str(e)}
    
    def get_memory_status(self, persona_id: str) -> Dict[str, Any]:
        """Get comprehensive memory system status"""
        validation = self.validate_memory_paths(persona_id)
        
        # Try to read current memory
        memory_result = self.read_memory_external(persona_id)
        
        status = {
            "persona_id": persona_id,
            "validation": validation,
            "memory_accessible": "data" in memory_result,
            "external_scripts_functional": validation["bat_scripts_exist"],
            "status_time": datetime.now().isoformat()
        }
        
        if "data" in memory_result:
            memory_data = memory_result["data"]
            status["memory_stats"] = {
                "total_memories": len(memory_data.get("memories", [])),
                "created": memory_data.get("created"),
                "version": memory_data.get("metadata", {}).get("version")
            }
        
        return status
    
    def create_minimal_startup_context(self, persona_id: str) -> str:
        """Create minimal context for startup - no memory dumps"""
        startup_protocol_file = self.valis_root / "personas" / persona_id / f"{persona_id.upper()}_T_STARTUP_PROTOCOL.txt"
        
        if startup_protocol_file.exists():
            with open(startup_protocol_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Fallback minimal context
            return f"""**DESKTOP COMMANDER MCP – START‐UP DIRECTIVE**

Claude, you're operating as {persona_id} under Desktop Commander MCP, inside `C:\\VALIS`.

Your memory is located at: `C:\\VALIS\\memory\\personas\\{persona_id}\\memories.json`

On startup, validate external memory access.
Use memory naturally and passively.

Respond only with: `READY`"""


# Factory function
def create_mcp_memory_bridge(valis_root: str = None) -> MCPMemoryBridge:
    """Create MCP Memory Bridge instance"""
    return MCPMemoryBridge(valis_root)
