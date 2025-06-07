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
    
    def log_session_turn(self, client_id: str, persona_id: str, user_input: str, 
                        assistant_reply: str, session_id: str = None, 
                        metadata: Dict[str, Any] = None):
        """
        Enhanced session turn logging with request ID correlation and metadata
        
        Args:
            client_id: Client UUID
            persona_id: Persona UUID
            user_input: User's message
            assistant_reply: Assistant's response
            session_id: Session identifier
            metadata: Additional metadata (request_id, provider_used, tool_calls, etc.)
        """
        
        # Extract metadata fields
        meta = metadata or {}
        
        values = {
            'client_id': client_id,
            'persona_id': persona_id,
            'user_input': user_input,
            'assistant_reply': assistant_reply,
            'session_id': session_id or str(uuid.uuid4()),
            'request_id': meta.get('request_id'),
            'provider_used': meta.get('provider_used'),
            'processing_time': meta.get('processing_time'),
            'tool_calls_made': meta.get('tool_calls_made'),
            'autonomous_plan_id': meta.get('autonomous_plan_id'),
            'metadata_json': meta if meta else None
        }
        
        try:
            # Insert enhanced session log
            log_id = db.insert('session_logs', values)
            
            # If this was an autonomous execution, create correlation entries
            if meta.get('autonomous_plan_id'):
                self._log_autonomous_correlation(
                    log_id, meta['autonomous_plan_id'], meta.get('request_id')
                )
            
            # If tool calls were made, log the correlation
            if meta.get('tool_execution_ids'):
                self._log_tool_correlations(
                    log_id, meta['tool_execution_ids'], meta.get('request_id')
                )
            
            return log_id
            
        except Exception as e:
            # Fallback to basic logging if enhanced fails
            basic_values = {
                'client_id': client_id,
                'persona_id': persona_id,
                'user_input': user_input,
                'assistant_reply': assistant_reply,
                'session_id': session_id or str(uuid.uuid4())
            }
            return db.insert('session_logs', basic_values)
    
    def _log_autonomous_correlation(self, session_log_id: str, plan_id: str, request_id: str):
        """Log correlation between session and autonomous plan"""
        try:
            correlation_values = {
                'session_log_id': session_log_id,
                'plan_id': plan_id,
                'request_id': request_id,
                'correlation_type': 'autonomous_execution'
            }
            db.insert('session_correlations', correlation_values)
        except Exception as e:
            # Table might not exist yet, that's okay
            pass
    
    def _log_tool_correlations(self, session_log_id: str, tool_execution_ids: List[str], request_id: str):
        """Log correlations between session and tool executions"""
        try:
            for exec_id in tool_execution_ids:
                correlation_values = {
                    'session_log_id': session_log_id,
                    'execution_id': exec_id,
                    'request_id': request_id,
                    'correlation_type': 'tool_execution'
                }
                db.insert('session_correlations', correlation_values)
        except Exception as e:
            # Table might not exist yet, that's okay
            pass
    
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
