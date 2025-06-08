"""
LongTermMemoryArchive - Sprint 2.2 Implementation
Manages canonical memory storage, retrieval, and symbolic encoding
Real implementation for persistent agent knowledge
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import uuid

from memory.db import db
from core.logging_config import get_valis_logger, log_operation_start, log_operation_end
from core.exceptions import MemoryConsolidationError, DatabaseError


class LongTermMemoryArchive:
    """
    Manages canonical long-term memory storage and retrieval for VALIS agents
    Handles symbolic encoding, memory consolidation, and knowledge persistence
    """
    
    def __init__(self, database_client=None):
        self.db = database_client or db
        self.logger = get_valis_logger()
        
        # Archive configuration
        self.MEMORY_TYPES = {
            'factual': {
                'priority': 1,
                'retention_indefinite': True,
                'requires_validation': True
            },
            'experiential': {
                'priority': 2,
                'retention_days': 365,
                'symbolic_encoding': True
            },
            'emotional': {
                'priority': 3,
                'retention_days': 180,
                'emotional_weight_threshold': 0.6
            },
            'procedural': {
                'priority': 1,
                'retention_indefinite': True,
                'skill_based': True
            },
            'symbolic': {
                'priority': 4,
                'retention_indefinite': True,
                'archetypal': True
            }
        }
        
        self.CONSOLIDATION_THRESHOLDS = {
            'emotional_weight': 0.6,
            'symbolic_resonance': 0.4,
            'factual_confidence': 0.8,
            'access_frequency': 3
        }
        
        self.logger.info("LongTermMemoryArchive initialized")
    
    def store_canonical_memory(self, agent_id: str, content: str, 
                              memory_type: str = 'experiential',
                              metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store memory in canonical long-term archive
        
        Args:
            agent_id: UUID of the agent
            content: Memory content to store
            memory_type: Type of memory ('factual', 'experiential', 'emotional', 'procedural', 'symbolic')
            metadata: Additional memory metadata
            
        Returns:
            Memory ID of stored memory
            
        Raises:
            MemoryConsolidationError: If storage fails
            DatabaseError: If database operations fail
        """
        if not agent_id or not content:
            raise MemoryConsolidationError("Agent ID and content are required for memory storage")
        
        if memory_type not in self.MEMORY_TYPES:
            raise MemoryConsolidationError(f"Invalid memory type: {memory_type}")
        
        log_operation_start(self.logger, "store_canonical_memory", 
                           agent_id=agent_id, memory_type=memory_type)
        
        try:
            memory_id = str(uuid.uuid4())
            config = self.MEMORY_TYPES[memory_type]
            metadata = metadata or {}
            
            # Determine retention policy
            retention_date = None
            if not config.get('retention_indefinite', False):
                retention_days = config.get('retention_days', 365)
                retention_date = datetime.now() + timedelta(days=retention_days)
            
            # Calculate initial relevance score
            relevance_score = self._calculate_relevance_score(content, memory_type, metadata)
            
            # Apply symbolic encoding if needed
            symbolic_content = None
            if config.get('symbolic_encoding', False):
                symbolic_content = self._apply_symbolic_encoding(content, metadata)
            
            # Store in canonical memory
            self.db.execute("""
                INSERT INTO canon_memories (
                    memory_id, agent_id, content, memory_type, relevance_score,
                    symbolic_content, metadata, retention_date, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                memory_id, agent_id, content, memory_type, relevance_score,
                symbolic_content, json.dumps(metadata), retention_date, datetime.now()
            ))
            
            # Create emotional weight entry if applicable
            emotional_weight = metadata.get('emotional_weight', 0.0)
            if emotional_weight > 0:
                self.db.execute("""
                    INSERT INTO canon_memory_emotion_map (memory_id, emotion_type, weight)
                    VALUES (%s, %s, %s)
                """, (memory_id, metadata.get('emotion_type', 'neutral'), emotional_weight))
            
            self.logger.info(f"Stored canonical memory {memory_id} for {agent_id} "
                           f"(type: {memory_type}, relevance: {relevance_score:.3f})")
            
            log_operation_end(self.logger, "store_canonical_memory", success=True, 
                             agent_id=agent_id, memory_id=memory_id)
            
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Failed to store canonical memory for {agent_id}: {e}")
            log_operation_end(self.logger, "store_canonical_memory", success=False, agent_id=agent_id)
            raise MemoryConsolidationError(f"Canonical memory storage failed: {e}")

    def retrieve_memories(self, agent_id: str, 
                         memory_type: Optional[str] = None,
                         query: Optional[str] = None,
                         emotional_bias: Optional[str] = None,
                         limit: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieve memories from canonical archive with filtering
        
        Args:
            agent_id: UUID of the agent
            memory_type: Filter by memory type
            query: Text query for content search
            emotional_bias: Emotional bias for retrieval
            limit: Maximum number of memories to return
            
        Returns:
            List of matching memories with metadata
            
        Raises:
            DatabaseError: If database operations fail
        """
        if not agent_id:
            raise MemoryConsolidationError("Agent ID is required for memory retrieval")
        
        try:
            # Build query based on filters
            query_parts = ["SELECT * FROM canon_memories WHERE agent_id = %s"]
            params = [agent_id]
            
            if memory_type:
                query_parts.append("AND memory_type = %s")
                params.append(memory_type)
            
            if query:
                query_parts.append("AND (content ILIKE %s OR symbolic_content ILIKE %s)")
                params.extend([f"%{query}%", f"%{query}%"])
            
            # Apply emotional bias if specified
            if emotional_bias:
                query_parts.append("""
                    AND memory_id IN (
                        SELECT memory_id FROM canon_memory_emotion_map 
                        WHERE emotion_type = %s AND weight > %s
                    )
                """)
                params.extend([emotional_bias, self.CONSOLIDATION_THRESHOLDS['emotional_weight']])
            
            query_parts.append("ORDER BY relevance_score DESC, created_at DESC LIMIT %s")
            params.append(limit)
            
            final_query = " ".join(query_parts)
            memories = self.db.query(final_query, params)
            
            # Enrich with emotional data
            enriched_memories = []
            for memory in memories:
                emotion_data = self.db.query("""
                    SELECT emotion_type, weight FROM canon_memory_emotion_map 
                    WHERE memory_id = %s
                """, (memory['memory_id'],))
                
                memory['emotions'] = emotion_data
                enriched_memories.append(memory)
            
            self.logger.debug(f"Retrieved {len(enriched_memories)} memories for {agent_id}")
            return enriched_memories
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve memories for {agent_id}: {e}")
            raise DatabaseError(f"Memory retrieval failed: {e}")
    
    def consolidate_from_working_memory(self, agent_id: str, 
                                      source_memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolidate working memories into canonical long-term storage
        
        Args:
            agent_id: UUID of the agent
            source_memories: List of working memories to consolidate
            
        Returns:
            Consolidation results
            
        Raises:
            MemoryConsolidationError: If consolidation fails
        """
        log_operation_start(self.logger, "consolidate_from_working_memory", 
                           agent_id=agent_id, source_count=len(source_memories))
        
        try:
            consolidated_count = 0
            symbolic_count = 0
            emotional_count = 0
            
            for memory in source_memories:
                # Determine if memory meets consolidation thresholds
                emotional_weight = memory.get('emotional_weight', 0.0)
                relevance_score = memory.get('relevance_score', 0.0)
                access_count = memory.get('access_count', 0)
                
                should_consolidate = (
                    emotional_weight >= self.CONSOLIDATION_THRESHOLDS['emotional_weight'] or
                    relevance_score >= self.CONSOLIDATION_THRESHOLDS['symbolic_resonance'] or
                    access_count >= self.CONSOLIDATION_THRESHOLDS['access_frequency']
                )
                
                if should_consolidate:
                    # Determine memory type based on content analysis
                    memory_type = self._classify_memory_type(memory['content'], memory)
                    
                    # Create metadata from working memory
                    metadata = {
                        'source': 'working_memory',
                        'original_id': memory['memory_id'],
                        'emotional_weight': emotional_weight,
                        'access_count': access_count,
                        'consolidation_date': datetime.now().isoformat()
                    }
                    
                    # Store in canonical archive
                    canonical_id = self.store_canonical_memory(
                        agent_id, 
                        memory['content'], 
                        memory_type, 
                        metadata
                    )
                    
                    consolidated_count += 1
                    
                    if memory_type == 'symbolic':
                        symbolic_count += 1
                    if emotional_weight > 0:
                        emotional_count += 1
            
            result = {
                'agent_id': agent_id,
                'source_memories': len(source_memories),
                'consolidated_count': consolidated_count,
                'symbolic_memories': symbolic_count,
                'emotional_memories': emotional_count,
                'consolidation_rate': consolidated_count / len(source_memories) if source_memories else 0,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Consolidated {consolidated_count}/{len(source_memories)} "
                           f"working memories for {agent_id}")
            
            log_operation_end(self.logger, "consolidate_from_working_memory", success=True, 
                             agent_id=agent_id, consolidated=consolidated_count)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to consolidate memories for {agent_id}: {e}")
            log_operation_end(self.logger, "consolidate_from_working_memory", success=False, 
                             agent_id=agent_id)
            raise MemoryConsolidationError(f"Memory consolidation failed: {e}")

    def get_memory_statistics(self, agent_id: str = None) -> Dict[str, Any]:
        """Get comprehensive memory archive statistics"""
        try:
            if agent_id:
                # Agent-specific statistics
                stats = self.db.query("""
                    SELECT 
                        COUNT(*) as total_memories,
                        COUNT(CASE WHEN memory_type = 'factual' THEN 1 END) as factual_memories,
                        COUNT(CASE WHEN memory_type = 'experiential' THEN 1 END) as experiential_memories,
                        COUNT(CASE WHEN memory_type = 'emotional' THEN 1 END) as emotional_memories,
                        COUNT(CASE WHEN memory_type = 'symbolic' THEN 1 END) as symbolic_memories,
                        AVG(relevance_score) as avg_relevance,
                        MIN(created_at) as oldest_memory,
                        MAX(created_at) as newest_memory
                    FROM canon_memories 
                    WHERE agent_id = %s
                """, (agent_id,))
            else:
                # System-wide statistics
                stats = self.db.query("""
                    SELECT 
                        COUNT(*) as total_memories,
                        COUNT(DISTINCT agent_id) as agents_with_memories,
                        COUNT(CASE WHEN memory_type = 'factual' THEN 1 END) as factual_memories,
                        COUNT(CASE WHEN memory_type = 'experiential' THEN 1 END) as experiential_memories,
                        COUNT(CASE WHEN memory_type = 'emotional' THEN 1 END) as emotional_memories,
                        COUNT(CASE WHEN memory_type = 'symbolic' THEN 1 END) as symbolic_memories,
                        AVG(relevance_score) as avg_relevance
                    FROM canon_memories
                """)
            
            return {
                'agent_id': agent_id,
                'statistics': stats[0] if stats else {},
                'memory_types': self.MEMORY_TYPES,
                'consolidation_thresholds': self.CONSOLIDATION_THRESHOLDS,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get memory statistics: {e}")
            raise DatabaseError(f"Statistics retrieval failed: {e}")
    
    # Helper methods
    
    def _calculate_relevance_score(self, content: str, memory_type: str, 
                                 metadata: Dict[str, Any]) -> float:
        """Calculate relevance score for memory based on content and metadata"""
        base_score = 0.5
        
        # Type-based scoring
        type_config = self.MEMORY_TYPES.get(memory_type, {})
        priority = type_config.get('priority', 3)
        base_score += (4 - priority) * 0.1  # Higher priority = higher base score
        
        # Content length factor (optimal around 50-200 words)
        word_count = len(content.split())
        if 50 <= word_count <= 200:
            base_score += 0.1
        elif word_count < 20:
            base_score -= 0.1
        
        # Emotional weight factor
        emotional_weight = metadata.get('emotional_weight', 0.0)
        base_score += emotional_weight * 0.3
        
        # Symbolic resonance factor
        symbolic_weight = metadata.get('symbolic_weight', 0.0)
        base_score += symbolic_weight * 0.2
        
        # Access frequency factor
        access_count = metadata.get('access_count', 0)
        base_score += min(0.2, access_count * 0.05)
        
        return max(0.0, min(1.0, base_score))
    
    def _apply_symbolic_encoding(self, content: str, metadata: Dict[str, Any]) -> str:
        """Apply symbolic encoding to transform literal content into symbolic representation"""
        # Simplified symbolic encoding implementation
        # In a full implementation, this would use AI models for metaphor generation
        
        symbols = {
            'journey': ['travel', 'path', 'road', 'adventure', 'journey'],
            'growth': ['learn', 'develop', 'improve', 'evolve', 'growth'],
            'conflict': ['fight', 'struggle', 'oppose', 'resist'],
            'harmony': ['peace', 'balance', 'accord', 'unity'],
            'transformation': ['change', 'transform', 'shift', 'become']
        }
        
        content_lower = content.lower()
        symbolic_content = content
        
        for symbol, keywords in symbols.items():
            if any(keyword in content_lower for keyword in keywords):
                symbolic_content += f" [SYMBOLIC: {symbol}]"
        
        # Add emotional symbolism
        emotional_weight = metadata.get('emotional_weight', 0.0)
        if emotional_weight > 0.7:
            symbolic_content += " [SYMBOLIC: intensity]"
        
        return symbolic_content
    
    def _classify_memory_type(self, content: str, metadata: Dict[str, Any]) -> str:
        """Classify memory type based on content analysis"""
        content_lower = content.lower()
        
        # Check for factual indicators
        factual_indicators = ['fact', 'true', 'data', 'statistic', 'proven', 'research']
        if any(indicator in content_lower for indicator in factual_indicators):
            return 'factual'
        
        # Check for procedural indicators
        procedural_indicators = ['how to', 'step', 'process', 'method', 'procedure']
        if any(indicator in content_lower for indicator in procedural_indicators):
            return 'procedural'
        
        # Check for emotional content
        emotional_weight = metadata.get('emotional_weight', 0.0)
        if emotional_weight > self.CONSOLIDATION_THRESHOLDS['emotional_weight']:
            return 'emotional'
        
        # Check for symbolic content
        symbolic_indicators = ['dream', 'symbol', 'metaphor', 'archetype', 'meaning']
        if any(indicator in content_lower for indicator in symbolic_indicators):
            return 'symbolic'
        
        # Default to experiential
        return 'experiential'
    
    def cleanup_expired_memories(self, agent_id: str = None) -> Dict[str, Any]:
        """Clean up expired memories based on retention policies"""
        log_operation_start(self.logger, "cleanup_expired_memories", agent_id=agent_id)
        
        try:
            current_time = datetime.now()
            
            # Build cleanup query
            if agent_id:
                deleted = self.db.execute("""
                    DELETE FROM canon_memories 
                    WHERE agent_id = %s AND retention_date IS NOT NULL AND retention_date < %s
                """, (agent_id, current_time))
            else:
                deleted = self.db.execute("""
                    DELETE FROM canon_memories 
                    WHERE retention_date IS NOT NULL AND retention_date < %s
                """, (current_time,))
            
            result = {
                'agent_id': agent_id,
                'expired_memories_deleted': deleted,
                'cleanup_timestamp': current_time.isoformat()
            }
            
            self.logger.info(f"Cleaned up {deleted} expired memories" + 
                           (f" for {agent_id}" if agent_id else " system-wide"))
            
            log_operation_end(self.logger, "cleanup_expired_memories", success=True, 
                             agent_id=agent_id, deleted=deleted)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired memories: {e}")
            log_operation_end(self.logger, "cleanup_expired_memories", success=False, agent_id=agent_id)
            raise DatabaseError(f"Memory cleanup failed: {e}")
