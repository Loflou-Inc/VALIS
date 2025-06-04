"""
VALIS 2.0 Memory Query Layer
High-level memory access methods for MCPRuntime
"""
from typing import List, Dict, Any, Optional
from .db import db
import uuid
from datetime import datetime, timedelta

class MemoryQueryClient:
    
    def get_persona(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """Get persona profile by ID including default context mode"""
        sql = "SELECT id, name, role, bio, system_prompt, traits, default_context_mode, created_at FROM persona_profiles WHERE id = %s"
        results = db.query(sql, (persona_id,))
        return results[0] if results else None
    
    def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client profile by ID"""
        sql = "SELECT * FROM client_profiles WHERE id = %s"
        results = db.query(sql, (client_id,))
        return results[0] if results else None
    
    def get_top_canon(self, persona_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top canon memories by relevance"""
        sql = """
        SELECT content, tags, category, relevance_score, token_estimate
        FROM canon_memories 
        WHERE persona_id = %s 
        ORDER BY relevance_score DESC, last_used DESC 
        LIMIT %s
        """
        return db.query(sql, (persona_id, limit))
    
    def get_recent_working(self, persona_id: str, client_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent working memory entries"""
        sql = """
        SELECT content, importance, decay_score, token_estimate, created_at
        FROM working_memory 
        WHERE persona_id = %s AND client_id = %s 
        AND (expires_at IS NULL OR expires_at > NOW())
        ORDER BY decay_score DESC, created_at DESC 
        LIMIT %s
        """
        return db.query(sql, (persona_id, client_id, limit))
    
    def get_recent_session(self, persona_id: str, client_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get recent session history"""
        sql = """
        SELECT user_input, assistant_reply, created_at
        FROM session_logs 
        WHERE persona_id = %s AND client_id = %s 
        ORDER BY created_at DESC 
        LIMIT %s
        """
        return db.query(sql, (persona_id, client_id, limit))
    
    def log_session_turn(self, client_id: str, persona_id: str, user_input: str, assistant_reply: str, session_id: str = None):
        """Log a conversation turn"""
        values = {
            'client_id': client_id,
            'persona_id': persona_id,
            'user_input': user_input,
            'assistant_reply': assistant_reply,
            'session_id': session_id or str(uuid.uuid4())
        }
        return db.insert('session_logs', values)
    
    def add_working_memory(self, persona_id: str, client_id: str, content: str, importance: int = 5):
        """Add new working memory entry"""
        values = {
            'persona_id': persona_id,
            'client_id': client_id,
            'content': content,
            'importance': importance,
            'expires_at': datetime.now() + timedelta(days=7)  # 7 day default
        }
        return db.insert('working_memory', values)

# Global instance
memory = MemoryQueryClient()
