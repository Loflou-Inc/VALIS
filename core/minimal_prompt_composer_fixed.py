#!/usr/bin/env python3
"""Minimal Prompt Composer - External Memory Version"""

from pathlib import Path
from datetime import datetime

class MinimalPromptComposer:
    def __init__(self, valis_root: str = None):
        if valis_root is None:
            valis_root = Path(__file__).parent.parent
        self.valis_root = Path(valis_root)
    
    def create_minimal_prompt(self, persona_id: str, message: str, 
                            client_id: str = "default", 
                            session_id: str = None) -> str:
        current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        prompt = f"""You are {persona_id}, operating with external memory loaded.

Current time: {current_time}
Client: {client_id}
Session: {session_id or 'new'}

User: {message}READY`"""

    def format_dev_command(self, command: str, persona_id: str) -> str:
        if command == "memory_status":
            return f"Report memory system status for {persona_id} using external files only."
        elif command == "persona_summary":
            return f"Provide brief summary of {persona_id} based on loaded memory."
        else:
            return f"Execute dev command: {command}"
