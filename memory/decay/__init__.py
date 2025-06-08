"""
MemoryDecayEngine - Sprint 2.2 Implementation
Manages memory aging, decay, and intelligent forgetting
Real implementation, not a stub
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

from memory.db import db
from core.logging_config import get_valis_logger, log_operation_start, log_operation_end
from core.exceptions import MemoryConsolidationError, DatabaseError


class MemoryDecayEngine:
    """
    Implements intelligent forgetting and memory aging for VALIS agents
    Uses multiple decay strategies to manage memory lifecycle
    """
    
    def __init__(self, database_client=None):
        self.db = database_client or db
        self.logger = get_valis_logger()
        
        # Decay configuration
        self.DECAY_STRATEGIES = {
            'timestamp_based': {
                'enabled': True,
                'max_age_days': 30,
                'decay_rate': 0.1  # 10% relevance lost per week
            },
            'lru_based': {
                'enabled': True,
                'max_memories': 1000,
                'access_threshold': 7  # Days without access before decay
            },
            'relevance_based': {
                'enabled': True,
                'min_relevance': 0.3,
                'boost_emotional': True
            },
            'compression': {
                'enabled': True,
                'compress_after_days': 14,
                'summary_ratio': 0.3  # Keep 30% of original detail
            }
        }
        
        self.logger.info("MemoryDecayEngine initialized with intelligent forgetting")
    
    def apply_decay(self, agent_id: str, strategy: str = 'all') -> Dict[str, Any]:
        """
        Apply memory decay strategies to agent's memories
        
        Args:
            agent_id: UUID of the agent
            strategy: Decay strategy to apply ('all', 'timestamp', 'lru', 'relevance', 'compression')
            
        Returns:
            Decay operation results
            
        Raises:
            MemoryConsolidationError: If decay process fails
            DatabaseError: If database operations fail
        """
        if not agent_id:
            raise MemoryConsolidationError("Agent ID is required for memory decay")
        
        log_operation_start(self.logger, "apply_decay", agent_id=agent_id, strategy=strategy)
        
        try:
            results = {
                'agent_id': agent_id,
                'strategy_applied': strategy,
                'timestamp': datetime.now().isoformat(),
                'memories_processed': 0,
                'memories_decayed': 0,
                'memories_compressed': 0,
                'memories_deleted': 0,
                'details': {}
            }
            
            if strategy == 'all' or strategy == 'timestamp':
                timestamp_results = self._apply_timestamp_decay(agent_id)
                results['details']['timestamp_decay'] = timestamp_results
                results['memories_decayed'] += timestamp_results.get('decayed_count', 0)
            
            if strategy == 'all' or strategy == 'lru':
                lru_results = self._apply_lru_decay(agent_id)
                results['details']['lru_decay'] = lru_results
                results['memories_deleted'] += lru_results.get('deleted_count', 0)
            
            if strategy == 'all' or strategy == 'relevance':
                relevance_results = self._apply_relevance_decay(agent_id)
                results['details']['relevance_decay'] = relevance_results
                results['memories_decayed'] += relevance_results.get('decayed_count', 0)
            
            if strategy == 'all' or strategy == 'compression':
                compression_results = self._apply_compression_decay(agent_id)
                results['details']['compression_decay'] = compression_results
                results['memories_compressed'] += compression_results.get('compressed_count', 0)
            
            # Update total processed count
            results['memories_processed'] = self._count_agent_memories(agent_id)
            
            self.logger.info(f"Applied {strategy} decay to {agent_id}: "
                           f"{results['memories_decayed']} decayed, "
                           f"{results['memories_compressed']} compressed, "
                           f"{results['memories_deleted']} deleted")
            
            log_operation_end(self.logger, "apply_decay", success=True, agent_id=agent_id)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to apply decay to {agent_id}: {e}")
            log_operation_end(self.logger, "apply_decay", success=False, agent_id=agent_id)
            raise MemoryConsolidationError(f"Memory decay failed: {e}")

    def _apply_timestamp_decay(self, agent_id: str) -> Dict[str, Any]:
        """Apply time-based decay to memories"""
        try:
            config = self.DECAY_STRATEGIES['timestamp_based']
            cutoff_date = datetime.now() - timedelta(days=config['max_age_days'])
            
            # Get memories older than cutoff
            old_memories = self.db.query("""
                SELECT memory_id, relevance_score, created_at FROM working_memory 
                WHERE agent_id = %s AND created_at < %s
            """, (agent_id, cutoff_date))
            
            decayed_count = 0
            for memory in old_memories:
                # Calculate age-based decay
                days_old = (datetime.now() - memory['created_at']).days
                decay_factor = min(1.0, days_old * config['decay_rate'] / 7)  # Weekly decay
                new_relevance = memory['relevance_score'] * (1 - decay_factor)
                
                # Update relevance score
                self.db.execute("""
                    UPDATE working_memory 
                    SET relevance_score = %s 
                    WHERE memory_id = %s
                """, (new_relevance, memory['memory_id']))
                
                decayed_count += 1
            
            return {
                'strategy': 'timestamp_based',
                'decayed_count': decayed_count,
                'cutoff_date': cutoff_date.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Timestamp decay failed for {agent_id}: {e}")
            return {'strategy': 'timestamp_based', 'decayed_count': 0, 'error': str(e)}
    
    def _apply_lru_decay(self, agent_id: str) -> Dict[str, Any]:
        """Apply Least Recently Used decay"""
        try:
            config = self.DECAY_STRATEGIES['lru_based']
            
            # Count current memories
            memory_count = self.db.query("""
                SELECT COUNT(*) as count FROM working_memory WHERE agent_id = %s
            """, (agent_id,))[0]['count']
            
            deleted_count = 0
            if memory_count > config['max_memories']:
                # Delete oldest unused memories
                excess = memory_count - config['max_memories']
                
                deleted_count = self.db.execute("""
                    DELETE FROM working_memory 
                    WHERE memory_id IN (
                        SELECT memory_id FROM working_memory 
                        WHERE agent_id = %s 
                        ORDER BY last_accessed ASC, created_at ASC
                        LIMIT %s
                    )
                """, (agent_id, excess))
            
            # Also decay memories not accessed recently
            access_cutoff = datetime.now() - timedelta(days=config['access_threshold'])
            unaccessed = self.db.query("""
                SELECT memory_id FROM working_memory 
                WHERE agent_id = %s AND last_accessed < %s
            """, (agent_id, access_cutoff))
            
            for memory in unaccessed:
                self.db.execute("""
                    UPDATE working_memory 
                    SET relevance_score = relevance_score * 0.8 
                    WHERE memory_id = %s
                """, (memory['memory_id'],))
            
            return {
                'strategy': 'lru_based',
                'deleted_count': deleted_count,
                'unaccessed_decayed': len(unaccessed)
            }
            
        except Exception as e:
            self.logger.error(f"LRU decay failed for {agent_id}: {e}")
            return {'strategy': 'lru_based', 'deleted_count': 0, 'error': str(e)}
    
    def _apply_relevance_decay(self, agent_id: str) -> Dict[str, Any]:
        """Apply relevance-based decay with emotional boosting"""
        try:
            config = self.DECAY_STRATEGIES['relevance_based']
            
            # Get low-relevance memories
            low_relevance = self.db.query("""
                SELECT memory_id, relevance_score, emotional_weight 
                FROM working_memory 
                WHERE agent_id = %s AND relevance_score < %s
            """, (agent_id, config['min_relevance']))
            
            decayed_count = 0
            for memory in low_relevance:
                # Check if emotionally significant
                emotional_weight = memory.get('emotional_weight', 0.0)
                
                if config['boost_emotional'] and emotional_weight > 0.7:
                    # Preserve emotionally significant memories
                    continue
                
                # Further decay low-relevance memories
                new_relevance = memory['relevance_score'] * 0.5
                
                if new_relevance < 0.1:
                    # Delete if relevance becomes too low
                    self.db.execute("""
                        DELETE FROM working_memory WHERE memory_id = %s
                    """, (memory['memory_id'],))
                else:
                    # Just reduce relevance
                    self.db.execute("""
                        UPDATE working_memory 
                        SET relevance_score = %s 
                        WHERE memory_id = %s
                    """, (new_relevance, memory['memory_id']))
                
                decayed_count += 1
            
            return {
                'strategy': 'relevance_based',
                'decayed_count': decayed_count,
                'threshold': config['min_relevance']
            }
            
        except Exception as e:
            self.logger.error(f"Relevance decay failed for {agent_id}: {e}")
            return {'strategy': 'relevance_based', 'decayed_count': 0, 'error': str(e)}

    def _apply_compression_decay(self, agent_id: str) -> Dict[str, Any]:
        """Apply compression to old detailed memories"""
        try:
            config = self.DECAY_STRATEGIES['compression']
            compress_date = datetime.now() - timedelta(days=config['compress_after_days'])
            
            # Get detailed memories older than compression threshold
            detailed_memories = self.db.query("""
                SELECT memory_id, content, summary FROM working_memory 
                WHERE agent_id = %s AND created_at < %s AND summary IS NULL
            """, (agent_id, compress_date))
            
            compressed_count = 0
            for memory in detailed_memories:
                # Create compressed summary (simplified implementation)
                content = memory['content']
                summary = self._compress_memory_content(content, config['summary_ratio'])
                
                # Update with compressed version
                self.db.execute("""
                    UPDATE working_memory 
                    SET summary = %s, compression_applied = TRUE 
                    WHERE memory_id = %s
                """, (summary, memory['memory_id']))
                
                compressed_count += 1
            
            return {
                'strategy': 'compression',
                'compressed_count': compressed_count,
                'compression_threshold_days': config['compress_after_days']
            }
            
        except Exception as e:
            self.logger.error(f"Compression decay failed for {agent_id}: {e}")
            return {'strategy': 'compression', 'compressed_count': 0, 'error': str(e)}
    
    def _compress_memory_content(self, content: str, ratio: float) -> str:
        """Compress memory content to specified ratio"""
        # Simple implementation - take first portion and add summary
        words = content.split()
        keep_words = int(len(words) * ratio)
        
        if keep_words < len(words):
            compressed = ' '.join(words[:keep_words])
            return f"{compressed}... [compressed from {len(words)} to {keep_words} words]"
        
        return content
    
    def _count_agent_memories(self, agent_id: str) -> int:
        """Count total memories for agent"""
        try:
            result = self.db.query("""
                SELECT COUNT(*) as count FROM working_memory WHERE agent_id = %s
            """, (agent_id,))
            return result[0]['count'] if result else 0
        except Exception:
            return 0
    
    def get_decay_statistics(self, agent_id: str = None) -> Dict[str, Any]:
        """Get memory decay statistics"""
        try:
            if agent_id:
                # Agent-specific stats
                stats = self.db.query("""
                    SELECT 
                        COUNT(*) as total_memories,
                        AVG(relevance_score) as avg_relevance,
                        COUNT(CASE WHEN compression_applied THEN 1 END) as compressed_memories,
                        MIN(created_at) as oldest_memory,
                        MAX(last_accessed) as last_access
                    FROM working_memory 
                    WHERE agent_id = %s
                """, (agent_id,))
            else:
                # System-wide stats
                stats = self.db.query("""
                    SELECT 
                        COUNT(*) as total_memories,
                        AVG(relevance_score) as avg_relevance,
                        COUNT(CASE WHEN compression_applied THEN 1 END) as compressed_memories,
                        COUNT(DISTINCT agent_id) as agents_with_memories
                    FROM working_memory
                """)
            
            return {
                'agent_id': agent_id,
                'statistics': stats[0] if stats else {},
                'decay_config': self.DECAY_STRATEGIES,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get decay statistics: {e}")
            raise DatabaseError(f"Statistics retrieval failed: {e}")
    
    def emergency_cleanup(self, agent_id: str = None, force: bool = False) -> Dict[str, Any]:
        """Emergency memory cleanup when system is overloaded"""
        if not force:
            raise MemoryConsolidationError("Emergency cleanup requires force=True confirmation")
        
        log_operation_start(self.logger, "emergency_cleanup", agent_id=agent_id, force=force)
        
        try:
            if agent_id:
                # Agent-specific cleanup
                deleted = self.db.execute("""
                    DELETE FROM working_memory 
                    WHERE agent_id = %s AND relevance_score < 0.2
                """, (agent_id,))
            else:
                # System-wide cleanup
                deleted = self.db.execute("""
                    DELETE FROM working_memory 
                    WHERE relevance_score < 0.1 OR created_at < %s
                """, (datetime.now() - timedelta(days=60),))
            
            result = {
                'cleanup_type': 'emergency',
                'agent_id': agent_id,
                'memories_deleted': deleted,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.warning(f"Emergency cleanup completed: {deleted} memories deleted")
            log_operation_end(self.logger, "emergency_cleanup", success=True, agent_id=agent_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Emergency cleanup failed: {e}")
            log_operation_end(self.logger, "emergency_cleanup", success=False, agent_id=agent_id)
            raise DatabaseError(f"Emergency cleanup failed: {e}")
