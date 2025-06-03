#!/usr/bin/env python3
"""
Minimal Prompt Composer - External Memory Version
Creates lightweight prompts, loads memory via MCP operations
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MinimalPromptComposer:
    """
    Lightweight prompt composer that references external memory
    instead of dumping memory content into prompts
    """
    
    def __init__(self, valis_root: str = None):
        if valis_root is None:
            valis_root = Path(__file__).parent.parent
        self.valis_root = Path(valis_root)
    
    def create_minimal_prompt(self, persona_id: str, message: str, 
                            client_id: str = "default", 
                            session_id: str = None) -> str:
        """
        Create minimal prompt that references external memory
        No memory dumps - just context and current message
        """
        
        current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        prompt = f"""You are {persona_id}, operating with external memory loaded from:
C:\\VALIS\\memory\\personas\\{persona_id}\\memories.json

Current time: {current_time}
Client: {client_id}
Session: {session_id or 'new'}

Use your loaded memory naturally. Do not summarize or reference the memory system.

User: {message}        return prompt + "\n\nAssistant:"
    
    def get_startup_prompt(self, persona_id: str) -> str:
        """Load startup protocol for persona"""
        startup_file = self.valis_root / "personas" / persona_id / f"{persona_id.upper()}_T_STARTUP_PROTOCOL.txt"
        
        if startup_file.exists():
            with open(startup_file, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Fallback minimal startup
        return f"""**DESKTOP COMMANDER MCP - START-UP DIRECTIVE**

Claude, you're operating as {persona_id} under Desktop Commander MCP.

Memory location: `C:\\VALIS\\memory\\personas\\{persona_id}\\memories.json`

Respond only with: `READY`"""

    def format_dev_command(self, command: str, persona_id: str) -> str:
        """Format dev introspection commands"""
        if command == "memory_status":
            return f"Report memory system status for {persona_id} using external files only."
        elif command == "persona_summary":
            return f"Provide brief summary of {persona_id} based on loaded memory."
        else:
            return f"Execute dev command: {command}"
