"""
VALIS Conscious Agent
Core agent class for digital consciousness runtime
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

class ConsciousAgent:
    """
    Core conscious agent for VALIS digital consciousness
    Minimal implementation to support Cloud Soul API
    """
    
    def __init__(self, persona_id: str = None, agent_id: str = None):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.persona_id = persona_id
        self.created_at = datetime.now(timezone.utc)
        self.status = "active"
        self.memory = {}
        self.traits = {}
        
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "persona_id": self.persona_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "uptime": (datetime.now(timezone.utc) - self.created_at).total_seconds()
        }
    
    def set_persona(self, persona_id: str, traits: Dict[str, Any] = None):
        """Set persona for this agent"""
        self.persona_id = persona_id
        if traits:
            self.traits.update(traits)
    
    def process_input(self, input_text: str, context: Dict[str, Any] = None) -> str:
        """Process input and return response"""
        # Minimal implementation - just echo back for now
        return f"Agent {self.agent_id[:8]} processed: {input_text}"
    
    def add_memory(self, memory_type: str, content: str, metadata: Dict[str, Any] = None):
        """Add memory to agent"""
        memory_id = str(uuid.uuid4())
        self.memory[memory_id] = {
            "type": memory_type,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        return memory_id
    
    def get_memories(self, memory_type: str = None) -> List[Dict[str, Any]]:
        """Get agent memories"""
        if memory_type:
            return [mem for mem in self.memory.values() if mem["type"] == memory_type]
        return list(self.memory.values())
    
    def activate(self):
        """Activate agent"""
        self.status = "active"
    
    def deactivate(self):
        """Deactivate agent"""
        self.status = "inactive"
