"""
ShortTermMemoryHandler - Sprint 2.2 Refactor
Manages temporary memory storage and processing
Extracted from MemoryConsolidationEngine
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any

from memory.db import db
from core.logging_config import get_valis_logger
from core.exceptions import MemoryConsolidationError


class ShortTermMemoryHandler:
    """
    Handles short-term memory storage, retrieval, and preparation for consolidation
    Manages working memory and recent experiences
    """
    
    def __init__(self, database_client=None):
        self.db = database_client or db
        self.logger = get_valis_logger()
        
        # Short-term memory configuration
        self.MAX_WORKING_MEMORY_SIZE = 100
        self.MEMORY_RETENTION_HOURS = 24
        
        self.logger.info("ShortTermMemoryHandler initialized")
    
    def store_working_memory(self, agent_id: str, content: str, 
                           context: Dict[str, Any] = None) -> str:
        """Store content in working memory"""
        try:
            memory_id = self.db.execute("""
                INSERT INTO working_memory (agent_id, content, context, timestamp)
                VALUES (%s, %s, %s, %s)
                RETURNING memory_id
            """, (agent_id, content, context or {}, datetime.now()))
            
            self.logger.debug(f"Stored working memory for {agent_id}: {memory_id}")
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Failed to store working memory for {agent_id}: {e}")
            raise MemoryConsolidationError(f"Working memory storage failed: {e}")
    
    def get_recent_memories(self, agent_id: str, hours: int = None) -> List[Dict[str, Any]]:
        """Retrieve recent working memories for agent"""
        hours = hours or self.MEMORY_RETENTION_HOURS
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        try:
            memories = self.db.query("""
                SELECT * FROM working_memory 
                WHERE agent_id = %s AND timestamp > %s
                ORDER BY timestamp DESC
            """, (agent_id, cutoff_time))
            
            self.logger.debug(f"Retrieved {len(memories)} recent memories for {agent_id}")
            return memories
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve recent memories for {agent_id}: {e}")
            raise MemoryConsolidationError(f"Memory retrieval failed: {e}")
    
    def cleanup_expired_memories(self, agent_id: str = None) -> int:
        """Clean up expired working memories"""
        cutoff_time = datetime.now() - timedelta(hours=self.MEMORY_RETENTION_HOURS * 2)
        
        try:
            if agent_id:
                deleted = self.db.execute("""
                    DELETE FROM working_memory 
                    WHERE agent_id = %s AND timestamp < %s
                """, (agent_id, cutoff_time))
            else:
                deleted = self.db.execute("""
                    DELETE FROM working_memory WHERE timestamp < %s
                """, (cutoff_time,))
            
            self.logger.info(f"Cleaned up {deleted} expired working memories")
            return deleted
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired memories: {e}")
            raise MemoryConsolidationError(f"Memory cleanup failed: {e}")
