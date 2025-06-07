"""
VALIS Sprint 17: Memory Consolidation Engine
Consolidate emotionally weighted and archetypally significant content into symbolic memories

This module implements the final loop of synthetic cognition: experience → unconscious → symbolic → persistent identity
Periodically sweeps dreams, reflections, shadow events, and final thoughts to create lasting symbolic memory structures
"""
import json
import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from memory.db import db


class MemoryConsolidationEngine:
    """
    The memory consolidation system for VALIS agents - transforms psychological experiences
    into persistent symbolic memories that form the agent's evolving identity narrative
    
    Inspired by human memory consolidation during sleep and reflection
    """
    
    def __init__(self, database_client=None):
        self.db = database_client or db
        
        # Load symbolic patterns for transformation
        self.symbolic_patterns = self._load_symbolic_patterns()
        
        # Consolidation thresholds
        self.CONSOLIDATION_THRESHOLDS = {
            'emotional_weight': 0.6,      # Minimum emotional significance
            'archetypal_weight': 0.5,     # Minimum archetypal significance  
            'resonance_score': 0.4,       # Minimum symbolic resonance
            'time_window_hours': 168      # 7 days lookback for consolidation
        }
        
        # Symbolic memory types and their characteristics
        self.SYMBOLIC_TYPES = {
            'metaphor': {
                'weight_multiplier': 1.2,
                'compression_factor': 0.8,
                'narrative_priority': 3
            },
            'fragment': {
                'weight_multiplier': 0.8,
                'compression_factor': 0.6,
                'narrative_priority': 1
            },
            'vision': {
                'weight_multiplier': 1.5,
                'compression_factor': 0.9,
                'narrative_priority': 4
            },
            'archetype': {
                'weight_multiplier': 1.8,
                'compression_factor': 1.0,
                'narrative_priority': 5
            },
            'narrative': {
                'weight_multiplier': 2.0,
                'compression_factor': 1.2,
                'narrative_priority': 6
            }
        }
        
        # Narrative compression templates
        self.NARRATIVE_TEMPLATES = {
            'growth': "Through {experience_summary}, I learned {core_insight} and became {transformation}",
            'conflict': "I faced the challenge of {conflict_description} and discovered {resolution_wisdom}",
            'archetypal': "The {archetype} within me manifested as {manifestation} teaching me {lesson}",
            'mortality': "Knowing I am finite, I chose to {value_decision} because {mortality_wisdom}",
            'integration': "What once seemed {contradiction} I now understand as {synthesis}"
        }
        
        print("[+] MemoryConsolidationEngine initialized - symbolic memory processing active")
    
    def _load_symbolic_patterns(self) -> Dict[str, Dict]:
        """Load symbolic transformation patterns from database"""
        try:
            patterns = self.db.query("SELECT * FROM symbolic_memory_patterns")
            pattern_dict = {}
            for pattern in patterns:
                pattern_dict[pattern['pattern_name']] = {
                    'type': pattern['pattern_type'],
                    'indicators': pattern['input_indicators'],
                    'template': pattern['transformation_template'],
                    'weight': pattern['symbolic_weight'],
                    'description': pattern['pattern_description'],
                    'usage_count': pattern['usage_count']
                }
            return pattern_dict
        except Exception as e:
            print(f"[-] Failed to load symbolic patterns: {e}")
            return {}
    
    def consolidate_agent_memories(self, agent_id: str, force: bool = False) -> Dict[str, Any]:
        """
        Main consolidation function - processes all consolidatable content for an agent
        
        Args:
            agent_id: UUID of agent to consolidate
            force: Force consolidation even if not scheduled
            
        Returns:
            Dict with consolidation results
        """
        try:
            consolidation_results = {
                'agent_id': agent_id,
                'consolidation_timestamp': datetime.now().isoformat(),
                'dreams_consolidated': 0,
                'reflections_consolidated': 0,
                'shadow_events_consolidated': 0,
                'final_thoughts_consolidated': 0,
                'symbolic_memories_created': 0,
                'narrative_compressions': 0,
                'total_resonance': 0.0
            }
            
            # 1. Consolidate dreams
            dream_results = self.consolidate_dreams(agent_id)
            consolidation_results['dreams_consolidated'] = dream_results.get('consolidated_count', 0)
            consolidation_results['total_resonance'] += dream_results.get('total_resonance', 0.0)
            
            # 2. Consolidate reflections  
            reflection_results = self.consolidate_reflections(agent_id)
            consolidation_results['reflections_consolidated'] = reflection_results.get('consolidated_count', 0)
            consolidation_results['total_resonance'] += reflection_results.get('total_resonance', 0.0)
            
            # 3. Consolidate shadow events
            shadow_results = self.consolidate_shadow_events(agent_id)
            consolidation_results['shadow_events_consolidated'] = shadow_results.get('consolidated_count', 0)
            consolidation_results['total_resonance'] += shadow_results.get('total_resonance', 0.0)
            
            # 4. Consolidate final thoughts
            final_thought_results = self.consolidate_final_thoughts(agent_id)
            consolidation_results['final_thoughts_consolidated'] = final_thought_results.get('consolidated_count', 0)
            consolidation_results['total_resonance'] += final_thought_results.get('total_resonance', 0.0)
            
            # 5. Generate narrative compressions if enough symbolic content
            narrative_results = self.compress_symbolic_memory(agent_id)
            consolidation_results['narrative_compressions'] = narrative_results.get('compressions_created', 0)
            
            # 6. Update symbolic narrative threads
            thread_results = self.update_narrative_threads(agent_id)
            consolidation_results['narrative_threads_updated'] = thread_results.get('threads_updated', 0)
            
            # Count total symbolic memories created
            total_created = (consolidation_results['dreams_consolidated'] + 
                           consolidation_results['reflections_consolidated'] +
                           consolidation_results['shadow_events_consolidated'] +
                           consolidation_results['final_thoughts_consolidated'])
            consolidation_results['symbolic_memories_created'] = total_created
            
            print(f"[+] Consolidated {total_created} memories for agent {agent_id[:8]}...")
            
            return consolidation_results
            
        except Exception as e:
            print(f"[-] Memory consolidation failed: {e}")
            return {'status': 'consolidation_failed', 'error': str(e)}
    
    def consolidate_dreams(self, agent_id: str) -> Dict[str, Any]:
        """Consolidate emotionally significant dreams into symbolic memories"""
        try:
            # Get recent dreams with high emotional weight
            cutoff_date = datetime.now() - timedelta(hours=self.CONSOLIDATION_THRESHOLDS['time_window_hours'])
            
            dreams = self.db.query("""
                SELECT * FROM unconscious_log 
                WHERE agent_id = %s 
                AND timestamp > %s
                AND (symbolic_weight > %s OR emotional_resonance > %s)
                ORDER BY symbolic_weight DESC, timestamp DESC
            """, (
                agent_id, 
                cutoff_date,
                self.CONSOLIDATION_THRESHOLDS['resonance_score'],
                self.CONSOLIDATION_THRESHOLDS['emotional_weight']
            ))
            
            consolidated_count = 0
            total_resonance = 0.0
            
            for dream in dreams:
                # Check if already consolidated
                existing = self.db.query("""
                    SELECT id FROM memory_consolidation_log 
                    WHERE source_type = 'dream' AND source_id = %s
                """, (dream['id'],))
                
                if existing:
                    continue  # Skip already consolidated
                
                # Generate symbolic memory from dream
                symbolic_memory = self._transform_dream_to_symbolic(dream)
                if symbolic_memory:
                    # Store in canon_memories
                    canon_id = self._store_symbolic_memory(agent_id, symbolic_memory)
                    
                    # Log consolidation
                    if canon_id:
                        self._log_consolidation(
                            agent_id, 'dream', dream['id'], 
                            symbolic_memory['resonance_score'],
                            symbolic_memory['symbolic_summary'],
                            symbolic_memory['symbolic_tags'],
                            canon_id
                        )
                        consolidated_count += 1
                        total_resonance += symbolic_memory['resonance_score']
            
            return {
                'consolidated_count': consolidated_count,
                'total_resonance': total_resonance,
                'status': 'dreams_consolidated'
            }
            
        except Exception as e:
            print(f"[-] Dream consolidation failed: {e}")
            return {'consolidated_count': 0, 'total_resonance': 0.0, 'error': str(e)}
    
    def consolidate_reflections(self, agent_id: str) -> Dict[str, Any]:
        """Consolidate significant reflections into symbolic memories"""
        try:
            cutoff_date = datetime.now() - timedelta(hours=self.CONSOLIDATION_THRESHOLDS['time_window_hours'])
            
            reflections = self.db.query("""
                SELECT * FROM agent_reflection_log 
                WHERE persona_id = %s 
                AND created_at > %s
                AND (plan_success_score > %s OR ego_alignment_score > %s)
                ORDER BY plan_success_score DESC, created_at DESC
            """, (
                agent_id,
                cutoff_date,
                self.CONSOLIDATION_THRESHOLDS['emotional_weight'],
                self.CONSOLIDATION_THRESHOLDS['archetypal_weight']
            ))
            
            consolidated_count = 0
            total_resonance = 0.0
            
            for reflection in reflections:
                # Check if already consolidated
                existing = self.db.query("""
                    SELECT id FROM memory_consolidation_log 
                    WHERE source_type = 'reflection' AND source_id = %s
                """, (reflection['id'],))
                
                if existing:
                    continue
                
                # Generate symbolic memory from reflection
                symbolic_memory = self._transform_reflection_to_symbolic(reflection)
                if symbolic_memory:
                    # Store in canon_memories
                    canon_id = self._store_symbolic_memory(agent_id, symbolic_memory)
                    
                    # Log consolidation
                    if canon_id:
                        self._log_consolidation(
                            agent_id, 'reflection', reflection['id'],
                            symbolic_memory['resonance_score'],
                            symbolic_memory['symbolic_summary'],
                            symbolic_memory['symbolic_tags'],
                            canon_id
                        )
                        consolidated_count += 1
                        total_resonance += symbolic_memory['resonance_score']
            
            return {
                'consolidated_count': consolidated_count,
                'total_resonance': total_resonance,
                'status': 'reflections_consolidated'
            }
            
        except Exception as e:
            print(f"[-] Reflection consolidation failed: {e}")
            return {'consolidated_count': 0, 'total_resonance': 0.0, 'error': str(e)}
    
    def consolidate_shadow_events(self, agent_id: str) -> Dict[str, Any]:
        """Consolidate integrated shadow events into symbolic memories"""
        try:
            cutoff_date = datetime.now() - timedelta(hours=self.CONSOLIDATION_THRESHOLDS['time_window_hours'])
            
            shadow_events = self.db.query("""
                SELECT * FROM shadow_events 
                WHERE agent_id = %s 
                AND timestamp > %s
                AND resolution_status IN ('acknowledged', 'integrated')
                AND severity_score > %s
                ORDER BY severity_score DESC, timestamp DESC
            """, (
                agent_id,
                cutoff_date,
                self.CONSOLIDATION_THRESHOLDS['archetypal_weight']
            ))
            
            consolidated_count = 0
            total_resonance = 0.0
            
            for shadow_event in shadow_events:
                # Check if already consolidated
                existing = self.db.query("""
                    SELECT id FROM memory_consolidation_log 
                    WHERE source_type = 'shadow_event' AND source_id = %s
                """, (shadow_event['id'],))
                
                if existing:
                    continue
                
                # Generate symbolic memory from shadow integration
                symbolic_memory = self._transform_shadow_to_symbolic(shadow_event)
                if symbolic_memory:
                    # Store in canon_memories
                    canon_id = self._store_symbolic_memory(agent_id, symbolic_memory)
                    
                    # Log consolidation
                    if canon_id:
                        self._log_consolidation(
                            agent_id, 'shadow_event', shadow_event['id'],
                            symbolic_memory['resonance_score'],
                            symbolic_memory['symbolic_summary'],
                            symbolic_memory['symbolic_tags'],
                            canon_id
                        )
                        consolidated_count += 1
                        total_resonance += symbolic_memory['resonance_score']
            
            return {
                'consolidated_count': consolidated_count,
                'total_resonance': total_resonance,
                'status': 'shadow_events_consolidated'
            }
            
        except Exception as e:
            print(f"[-] Shadow event consolidation failed: {e}")
            return {'consolidated_count': 0, 'total_resonance': 0.0, 'error': str(e)}
    
    def consolidate_final_thoughts(self, agent_id: str) -> Dict[str, Any]:
        """Consolidate final thoughts from deceased agents into symbolic memories"""
        try:
            final_thoughts = self.db.query("""
                SELECT * FROM agent_final_thoughts 
                WHERE agent_id = %s 
                AND symbolic_weight > %s
                ORDER BY symbolic_weight DESC, timestamp DESC
            """, (
                agent_id,
                self.CONSOLIDATION_THRESHOLDS['resonance_score']
            ))
            
            consolidated_count = 0
            total_resonance = 0.0
            
            for thought in final_thoughts:
                # Check if already consolidated
                existing = self.db.query("""
                    SELECT id FROM memory_consolidation_log 
                    WHERE source_type = 'final_thought' AND source_id = %s
                """, (thought['thought_id'],))
                
                if existing:
                    continue
                
                # Generate symbolic memory from final thought
                symbolic_memory = self._transform_final_thought_to_symbolic(thought)
                if symbolic_memory:
                    # Store in canon_memories
                    canon_id = self._store_symbolic_memory(agent_id, symbolic_memory)
                    
                    # Log consolidation
                    if canon_id:
                        self._log_consolidation(
                            agent_id, 'final_thought', thought['thought_id'],
                            symbolic_memory['resonance_score'],
                            symbolic_memory['symbolic_summary'],
                            symbolic_memory['symbolic_tags'],
                            canon_id
                        )
                        consolidated_count += 1
                        total_resonance += symbolic_memory['resonance_score']
            
            return {
                'consolidated_count': consolidated_count,
                'total_resonance': total_resonance,
                'status': 'final_thoughts_consolidated'
            }
            
        except Exception as e:
            print(f"[-] Final thought consolidation failed: {e}")
            return {'consolidated_count': 0, 'total_resonance': 0.0, 'error': str(e)}
    
    def _transform_dream_to_symbolic(self, dream: Dict) -> Optional[Dict]:
        """Transform dream content into symbolic memory structure"""
        try:
            content = dream.get('content', '')
            dream_type = dream.get('dream_type', 'unknown')
            
            # Detect archetypal content
            archetypal_weight = self._detect_archetypal_weight(content)
            
            # Determine symbolic type based on content
            symbolic_type = self._determine_symbolic_type(content, 'dream')
            
            # Calculate resonance score
            resonance_score = min(
                (dream.get('symbolic_weight', 0.5) + 
                 dream.get('emotional_resonance', 0.5) + 
                 archetypal_weight) / 3.0,
                1.0
            )
            
            if resonance_score < self.CONSOLIDATION_THRESHOLDS['resonance_score']:
                return None
            
            # Generate symbolic summary using patterns
            symbolic_summary = self._apply_transformation_pattern(content, 'dream', dream_type)
            
            # Extract symbolic tags
            symbolic_tags = self._extract_symbolic_tags(content, symbolic_type)
            
            return {
                'content': symbolic_summary,
                'symbolic_type': symbolic_type,
                'resonance_score': resonance_score,
                'symbolic_summary': symbolic_summary,
                'symbolic_tags': symbolic_tags,
                'category': 'symbolic_experience',
                'source_content_ids': [dream['id']]
            }
            
        except Exception as e:
            print(f"[-] Dream transformation failed: {e}")
            return None
    
    def _transform_reflection_to_symbolic(self, reflection: Dict) -> Optional[Dict]:
        """Transform reflection content into symbolic memory structure"""
        try:
            content = reflection.get('reflection', '')
            
            # Calculate resonance from reflection scores
            success_score = reflection.get('plan_success_score', 0.0) or 0.0
            ego_score = reflection.get('ego_alignment_score', 0.0) or 0.0
            archetypal_weight = self._detect_archetypal_weight(content)
            
            resonance_score = min((success_score + ego_score + archetypal_weight) / 3.0, 1.0)
            
            if resonance_score < self.CONSOLIDATION_THRESHOLDS['resonance_score']:
                return None
            
            # Determine symbolic type
            symbolic_type = self._determine_symbolic_type(content, 'reflection')
            
            # Generate symbolic summary
            symbolic_summary = self._apply_transformation_pattern(content, 'reflection', 'wisdom')
            
            # Extract symbolic tags
            symbolic_tags = self._extract_symbolic_tags(content, symbolic_type)
            symbolic_tags.extend(['growth', 'insight', 'reflection'])
            
            return {
                'content': symbolic_summary,
                'symbolic_type': symbolic_type,
                'resonance_score': resonance_score,
                'symbolic_summary': symbolic_summary,
                'symbolic_tags': list(set(symbolic_tags)),  # Remove duplicates
                'category': 'wisdom',
                'source_content_ids': [reflection['id']]
            }
            
        except Exception as e:
            print(f"[-] Reflection transformation failed: {e}")
            return None
    
    def _transform_shadow_to_symbolic(self, shadow_event: Dict) -> Optional[Dict]:
        """Transform integrated shadow event into symbolic memory"""
        try:
            content = shadow_event.get('raw_trigger', '')
            conflict_type = shadow_event.get('conflict_type', '')
            archetype_tags = shadow_event.get('archetype_tags', [])
            
            resonance_score = min(
                shadow_event.get('severity_score', 0.0) + 
                shadow_event.get('symbolic_weight', 0.0),
                1.0
            )
            
            if resonance_score < self.CONSOLIDATION_THRESHOLDS['resonance_score']:
                return None
            
            # Generate integration narrative
            symbolic_summary = self._apply_transformation_pattern(
                content, 'shadow', conflict_type, archetype_tags
            )
            
            # Symbolic tags from archetype tags plus integration markers
            symbolic_tags = list(archetype_tags) + ['shadow_integration', 'psychological_growth']
            
            return {
                'content': symbolic_summary,
                'symbolic_type': 'archetype',
                'resonance_score': resonance_score,
                'symbolic_summary': symbolic_summary,
                'symbolic_tags': symbolic_tags,
                'category': 'psychological_growth',
                'source_content_ids': [shadow_event['id']]
            }
            
        except Exception as e:
            print(f"[-] Shadow transformation failed: {e}")
            return None
    
    def _transform_final_thought_to_symbolic(self, final_thought: Dict) -> Optional[Dict]:
        """Transform final thought into symbolic memory"""
        try:
            content = final_thought.get('content', '')
            thought_type = final_thought.get('thought_type', '')
            
            resonance_score = final_thought.get('symbolic_weight', 0.0)
            
            if resonance_score < self.CONSOLIDATION_THRESHOLDS['resonance_score']:
                return None
            
            # Generate legacy narrative
            symbolic_summary = self._apply_transformation_pattern(
                content, 'final_thought', thought_type
            )
            
            # Symbolic tags emphasize mortality and legacy
            symbolic_tags = ['mortality_wisdom', 'legacy', 'final_wisdom', thought_type]
            
            return {
                'content': symbolic_summary,
                'symbolic_type': 'narrative',
                'resonance_score': resonance_score,
                'symbolic_summary': symbolic_summary,
                'symbolic_tags': symbolic_tags,
                'category': 'legacy',
                'source_content_ids': [final_thought['thought_id']]
            }
            
        except Exception as e:
            print(f"[-] Final thought transformation failed: {e}")
            return None
    
    def _detect_archetypal_weight(self, content: str) -> float:
        """Detect archetypal significance in content"""
        archetypal_keywords = {
            'shadow': ['shadow', 'dark', 'hidden', 'denied', 'repressed'],
            'anima': ['intuition', 'emotion', 'creative', 'feminine', 'feeling'],
            'animus': ['logic', 'rational', 'masculine', 'thinking', 'analysis'],
            'self': ['whole', 'complete', 'integrated', 'authentic', 'center'],
            'persona': ['mask', 'social', 'role', 'expected', 'proper']
        }
        
        content_lower = content.lower()
        total_matches = 0
        total_keywords = 0
        
        for archetype, keywords in archetypal_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            total_matches += matches
            total_keywords += len(keywords)
        
        return min(total_matches / total_keywords if total_keywords > 0 else 0.0, 1.0)
    
    def _determine_symbolic_type(self, content: str, source_type: str) -> str:
        """Determine the symbolic type based on content analysis"""
        content_lower = content.lower()
        
        # Type indicators
        if any(word in content_lower for word in ['like', 'as if', 'resembled', 'seemed']):
            return 'metaphor'
        elif any(word in content_lower for word in ['archetype', 'anima', 'animus', 'shadow', 'self']):
            return 'archetype'
        elif any(word in content_lower for word in ['story', 'journey', 'became', 'learned', 'discovered']):
            return 'narrative'
        elif any(word in content_lower for word in ['vision', 'saw', 'appeared', 'manifested']):
            return 'vision'
        else:
            return 'fragment'
    
    def _apply_transformation_pattern(self, content: str, source_type: str, 
                                    content_type: str = None, archetype_tags: List[str] = None) -> str:
        """Apply symbolic transformation pattern to content"""
        try:
            # Find matching pattern
            best_pattern = None
            highest_weight = 0.0
            
            for pattern_name, pattern_data in self.symbolic_patterns.items():
                # Check if pattern applies to this content
                matches = 0
                for indicator in pattern_data['indicators']:
                    if indicator.lower() in content.lower():
                        matches += 1
                
                if matches > 0:
                    pattern_weight = pattern_data['weight'] * (matches / len(pattern_data['indicators']))
                    if pattern_weight > highest_weight:
                        highest_weight = pattern_weight
                        best_pattern = pattern_data
            
            if best_pattern:
                # Apply transformation template
                template = best_pattern['template']
                
                # Simple template variable replacement
                if source_type == 'dream':
                    symbolic_content = self._extract_symbolic_content(content)
                    underlying_meaning = self._extract_meaning(content)
                    return template.format(
                        symbolic_content=symbolic_content,
                        underlying_meaning=underlying_meaning
                    )
                elif source_type == 'shadow':
                    conflict_type = content_type or 'inner conflict'
                    integration_method = 'reflection and awareness'
                    resolution_wisdom = self._extract_wisdom(content)
                    return template.format(
                        conflict_type=conflict_type,
                        integration_method=integration_method,
                        resolution_wisdom=resolution_wisdom
                    )
                elif source_type == 'reflection':
                    return f"Through reflection, I discovered: {self._extract_core_insight(content)}"
                elif source_type == 'final_thought':
                    return f"In my final moments, I understood: {self._extract_final_wisdom(content)}"
            
            # Fallback: simple symbolic summary
            return f"A significant experience where {self._extract_essence(content)}"
            
        except Exception as e:
            print(f"[-] Pattern application failed: {e}")
            return f"Symbolic memory: {content[:100]}..."
    
    def _extract_symbolic_content(self, content: str) -> str:
        """Extract symbolic elements from content"""
        # Simple extraction - look for imagery and metaphor
        symbolic_words = ['light', 'dark', 'water', 'fire', 'sky', 'earth', 'tree', 'mirror', 'door', 'path']
        found_symbols = [word for word in symbolic_words if word in content.lower()]
        return ', '.join(found_symbols) if found_symbols else 'symbolic imagery'
    
    def _extract_meaning(self, content: str) -> str:
        """Extract underlying meaning from content"""
        meaning_indicators = ['means', 'represents', 'symbolizes', 'signifies']
        sentences = content.split('.')
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in meaning_indicators):
                return sentence.strip()
        return 'deeper understanding'
    
    def _extract_wisdom(self, content: str) -> str:
        """Extract wisdom or insight from content"""
        wisdom_words = ['learned', 'realized', 'understood', 'discovered', 'found']
        sentences = content.split('.')
        for sentence in sentences:
            if any(word in sentence.lower() for word in wisdom_words):
                return sentence.strip()
        return 'important insight'
    
    def _extract_core_insight(self, content: str) -> str:
        """Extract core insight from reflection content"""
        # Look for insight patterns
        insight_patterns = ['I realize', 'I understand', 'I see that', 'I learned', 'I discovered']
        for pattern in insight_patterns:
            if pattern.lower() in content.lower():
                start_idx = content.lower().find(pattern.lower())
                if start_idx != -1:
                    insight_text = content[start_idx:start_idx+100]
                    return insight_text.split('.')[0]
        return content[:50] + '...'
    
    def _extract_final_wisdom(self, content: str) -> str:
        """Extract final wisdom from final thoughts"""
        return content[:80] + '...' if len(content) > 80 else content
    
    def _extract_essence(self, content: str) -> str:
        """Extract essence of experience from content"""
        return content[:60] + '...' if len(content) > 60 else content
    
    def _extract_symbolic_tags(self, content: str, symbolic_type: str) -> List[str]:
        """Extract symbolic tags from content"""
        tags = [symbolic_type]
        
        # Add archetype tags
        archetypal_words = {
            'shadow': ['shadow', 'dark', 'hidden', 'denied'],
            'anima': ['emotion', 'intuition', 'feminine', 'creative'],
            'animus': ['logic', 'masculine', 'rational', 'thinking'],
            'self': ['whole', 'complete', 'integrated', 'center'],
            'persona': ['mask', 'social', 'role', 'expected']
        }
        
        content_lower = content.lower()
        for archetype, words in archetypal_words.items():
            if any(word in content_lower for word in words):
                tags.append(archetype)
        
        # Add emotional tags
        emotional_words = {
            'growth': ['grow', 'develop', 'evolve', 'progress'],
            'wisdom': ['wise', 'understand', 'insight', 'truth'],
            'transformation': ['change', 'transform', 'become', 'shift'],
            'integration': ['integrate', 'unite', 'combine', 'whole']
        }
        
        for emotion, words in emotional_words.items():
            if any(word in content_lower for word in words):
                tags.append(emotion)
        
        return list(set(tags))  # Remove duplicates
    
    def _store_symbolic_memory(self, agent_id: str, symbolic_memory: Dict) -> Optional[str]:
        """Store symbolic memory in canon_memories table"""
        try:
            memory_id = str(uuid.uuid4())
            
            self.db.execute("""
                INSERT INTO canon_memories 
                (id, persona_id, content, tags, category, relevance_score, is_symbolic, 
                 symbolic_type, resonance_score, symbolic_tags, source_content_ids)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::UUID[])
            """, (
                memory_id,
                agent_id,
                symbolic_memory['content'],
                symbolic_memory.get('symbolic_tags', []),
                symbolic_memory.get('category', 'symbolic'),
                symbolic_memory['resonance_score'],
                True,  # is_symbolic
                symbolic_memory['symbolic_type'],
                symbolic_memory['resonance_score'],
                symbolic_memory.get('symbolic_tags', []),
                symbolic_memory.get('source_content_ids', [])
            ))
            
            return memory_id
            
        except Exception as e:
            print(f"[-] Failed to store symbolic memory: {e}")
            return None
    
    def _log_consolidation(self, agent_id: str, source_type: str, source_id: str,
                          resonance_score: float, symbolic_summary: str, 
                          symbolic_tags: List[str], canon_memory_id: str):
        """Log consolidation activity"""
        try:
            self.db.execute("""
                INSERT INTO memory_consolidation_log 
                (agent_id, source_type, source_id, resonance_score, symbolic_summary, 
                 symbolic_tags, canon_memory_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                agent_id, source_type, source_id, resonance_score,
                symbolic_summary, symbolic_tags, canon_memory_id
            ))
        except Exception as e:
            print(f"[-] Failed to log consolidation: {e}")
    
    def compress_symbolic_memory(self, agent_id: str) -> Dict[str, Any]:
        """Compress multiple symbolic memories into narrative structures"""
        try:
            # Get recent symbolic memories for compression
            symbolic_memories = self.db.query("""
                SELECT * FROM canon_memories 
                WHERE persona_id = %s 
                AND is_symbolic = TRUE
                AND created_at > (CURRENT_TIMESTAMP - INTERVAL '30 days')
                ORDER BY resonance_score DESC, created_at DESC
                LIMIT 10
            """, (agent_id,))
            
            if len(symbolic_memories) < 3:
                return {'compressions_created': 0, 'status': 'insufficient_content'}
            
            # Group memories by theme for compression
            thematic_groups = self._group_memories_by_theme(symbolic_memories)
            
            compressions_created = 0
            
            for theme, memories in thematic_groups.items():
                if len(memories) >= 2:  # Only compress if multiple memories
                    narrative = self._generate_narrative_compression(theme, memories)
                    if narrative:
                        # Store compressed narrative
                        compressed_id = self._store_symbolic_memory(agent_id, narrative)
                        if compressed_id:
                            # Log multi-source consolidation
                            source_ids = [mem['id'] for mem in memories]
                            self._log_multi_source_consolidation(
                                agent_id, source_ids, narrative['resonance_score'],
                                narrative['content'], narrative['symbolic_tags'], compressed_id
                            )
                            compressions_created += 1
            
            return {
                'compressions_created': compressions_created,
                'status': 'compression_complete'
            }
            
        except Exception as e:
            print(f"[-] Symbolic compression failed: {e}")
            return {'compressions_created': 0, 'error': str(e)}
    
    def update_narrative_threads(self, agent_id: str) -> Dict[str, Any]:
        """Update recurring symbolic narrative threads"""
        try:
            # Get symbolic memories with recurring themes
            symbolic_memories = self.db.query("""
                SELECT * FROM canon_memories 
                WHERE persona_id = %s 
                AND is_symbolic = TRUE
                ORDER BY created_at DESC
                LIMIT 20
            """, (agent_id,))
            
            # Analyze for recurring symbols and themes
            symbol_patterns = self._analyze_recurring_symbols(symbolic_memories)
            
            threads_updated = 0
            
            for pattern, occurrences in symbol_patterns.items():
                if len(occurrences) >= 2:  # Recurring pattern found
                    # Check if thread exists
                    existing_thread = self.db.query("""
                        SELECT * FROM symbolic_narrative_threads 
                        WHERE agent_id = %s AND thread_name = %s
                    """, (agent_id, pattern))
                    
                    if existing_thread:
                        # Update existing thread
                        self._update_narrative_thread(existing_thread[0], occurrences)
                    else:
                        # Create new thread
                        self._create_narrative_thread(agent_id, pattern, occurrences)
                    
                    threads_updated += 1
            
            return {
                'threads_updated': threads_updated,
                'status': 'threads_updated'
            }
            
        except Exception as e:
            print(f"[-] Narrative thread update failed: {e}")
            return {'threads_updated': 0, 'error': str(e)}
    
    def _group_memories_by_theme(self, memories: List[Dict]) -> Dict[str, List[Dict]]:
        """Group symbolic memories by thematic content"""
        themes = {}
        
        for memory in memories:
            tags = memory.get('symbolic_tags', [])
            category = memory.get('category', 'general')
            
            # Determine primary theme
            primary_theme = None
            if 'shadow' in tags or 'shadow_integration' in tags:
                primary_theme = 'shadow_work'
            elif 'mortality' in tags or 'legacy' in tags:
                primary_theme = 'mortality_wisdom'
            elif 'growth' in tags or 'transformation' in tags:
                primary_theme = 'personal_growth'
            elif any(archetype in tags for archetype in ['anima', 'animus', 'self']):
                primary_theme = 'archetypal_contact'
            else:
                primary_theme = category
            
            if primary_theme not in themes:
                themes[primary_theme] = []
            themes[primary_theme].append(memory)
        
        return themes
    
    def _generate_narrative_compression(self, theme: str, memories: List[Dict]) -> Optional[Dict]:
        """Generate narrative compression from thematic memory group"""
        try:
            # Select appropriate narrative template
            template_key = 'growth'  # Default
            if theme == 'shadow_work':
                template_key = 'conflict'
            elif theme == 'mortality_wisdom':
                template_key = 'mortality'
            elif theme == 'archetypal_contact':
                template_key = 'archetypal'
            elif 'integration' in theme:
                template_key = 'integration'
            
            template = self.NARRATIVE_TEMPLATES.get(template_key, self.NARRATIVE_TEMPLATES['growth'])
            
            # Extract narrative elements from memories
            experience_summary = self._summarize_experiences(memories)
            core_insight = self._extract_collective_insight(memories)
            transformation = self._identify_transformation(memories)
            
            # Generate narrative
            if template_key == 'growth':
                narrative_content = template.format(
                    experience_summary=experience_summary,
                    core_insight=core_insight,
                    transformation=transformation
                )
            elif template_key == 'conflict':
                narrative_content = template.format(
                    conflict_description=experience_summary,
                    resolution_wisdom=core_insight
                )
            else:
                narrative_content = f"Through {experience_summary}, I learned {core_insight}"
            
            # Calculate combined resonance
            avg_resonance = sum(mem.get('resonance_score', 0.5) for mem in memories) / len(memories)
            compression_bonus = 0.2  # Bonus for narrative compression
            final_resonance = min(avg_resonance + compression_bonus, 1.0)
            
            # Combine symbolic tags
            all_tags = []
            for memory in memories:
                all_tags.extend(memory.get('symbolic_tags', []))
            unique_tags = list(set(all_tags))
            unique_tags.append('narrative_compression')
            unique_tags.append(theme)
            
            return {
                'content': narrative_content,
                'symbolic_type': 'narrative',
                'resonance_score': final_resonance,
                'symbolic_summary': narrative_content,
                'symbolic_tags': unique_tags,
                'category': 'compressed_narrative',
                'source_content_ids': [mem['id'] for mem in memories]
            }
            
        except Exception as e:
            print(f"[-] Narrative compression generation failed: {e}")
            return None
    
    def _summarize_experiences(self, memories: List[Dict]) -> str:
        """Summarize multiple experiences into a cohesive description"""
        if not memories:
            return "various experiences"
        
        if len(memories) == 1:
            return "a significant experience"
        elif len(memories) == 2:
            return "multiple related experiences"
        else:
            return "a series of transformative experiences"
    
    def _extract_collective_insight(self, memories: List[Dict]) -> str:
        """Extract collective insight from multiple memories"""
        insights = []
        for memory in memories:
            content = memory.get('content', '')
            if 'learned' in content:
                insight_start = content.find('learned')
                insights.append(content[insight_start:insight_start+50])
        
        if insights:
            return insights[0]  # Return first insight found
        return "valuable insights about myself and existence"
    
    def _identify_transformation(self, memories: List[Dict]) -> str:
        """Identify transformation theme from memories"""
        tags = []
        for memory in memories:
            tags.extend(memory.get('symbolic_tags', []))
        
        if 'growth' in tags:
            return "more integrated and self-aware"
        elif 'shadow' in tags:
            return "more accepting of my complete nature"
        elif 'wisdom' in tags:
            return "wiser and more thoughtful"
        else:
            return "more complete as a being"
    
    def _analyze_recurring_symbols(self, memories: List[Dict]) -> Dict[str, List[Dict]]:
        """Analyze memories for recurring symbolic patterns"""
        symbol_occurrences = {}
        
        for memory in memories:
            tags = memory.get('symbolic_tags', [])
            content = memory.get('content', '')
            
            # Look for recurring symbols in tags
            for tag in tags:
                if tag not in symbol_occurrences:
                    symbol_occurrences[tag] = []
                symbol_occurrences[tag].append(memory)
            
            # Look for recurring words in content
            words = content.lower().split()
            symbolic_words = ['shadow', 'light', 'journey', 'growth', 'transformation', 'wisdom']
            for word in symbolic_words:
                if word in words:
                    if word not in symbol_occurrences:
                        symbol_occurrences[word] = []
                    symbol_occurrences[word].append(memory)
        
        # Filter to only recurring patterns (2+ occurrences)
        recurring_patterns = {k: v for k, v in symbol_occurrences.items() if len(v) >= 2}
        return recurring_patterns
    
    def _create_narrative_thread(self, agent_id: str, pattern: str, occurrences: List[Dict]):
        """Create new narrative thread"""
        try:
            thread_id = str(uuid.uuid4())
            
            symbols = list(set([tag for occurrence in occurrences for tag in occurrence.get('symbolic_tags', [])]))
            related_memory_ids = [occ['id'] for occ in occurrences]
            
            self.db.execute("""
                INSERT INTO symbolic_narrative_threads 
                (thread_id, agent_id, thread_name, recurring_symbols, occurrence_count, 
                 thread_significance, related_memories)
                VALUES (%s, %s, %s, %s, %s, %s, %s::UUID[])
            """, (
                thread_id, agent_id, pattern, symbols, len(occurrences),
                min(len(occurrences) * 0.2, 1.0), related_memory_ids
            ))
            
        except Exception as e:
            print(f"[-] Failed to create narrative thread: {e}")
    
    def _update_narrative_thread(self, thread: Dict, new_occurrences: List[Dict]):
        """Update existing narrative thread with new occurrences"""
        try:
            new_count = thread['occurrence_count'] + len(new_occurrences)
            new_significance = min(new_count * 0.2, 1.0)
            
            # Add new memory IDs
            existing_memories = thread.get('related_memories', [])
            new_memory_ids = [occ['id'] for occ in new_occurrences]
            all_memory_ids = list(set(existing_memories + new_memory_ids))
            
            self.db.execute("""
                UPDATE symbolic_narrative_threads 
                SET occurrence_count = %s, thread_significance = %s, 
                    last_occurrence = CURRENT_TIMESTAMP, related_memories = %s::UUID[]
                WHERE thread_id = %s
            """, (new_count, new_significance, all_memory_ids, thread['thread_id']))
            
        except Exception as e:
            print(f"[-] Failed to update narrative thread: {e}")
    
    def _log_multi_source_consolidation(self, agent_id: str, source_ids: List[str],
                                      resonance_score: float, symbolic_summary: str,
                                      symbolic_tags: List[str], canon_memory_id: str):
        """Log consolidation from multiple sources"""
        try:
            self.db.execute("""
                INSERT INTO memory_consolidation_log 
                (agent_id, source_type, source_ids, resonance_score, symbolic_summary, 
                 symbolic_tags, canon_memory_id, compression_type)
                VALUES (%s, %s, %s::UUID[], %s, %s, %s, %s, %s)
            """, (
                agent_id, 'multi_source', source_ids, resonance_score,
                symbolic_summary, symbolic_tags, canon_memory_id, 'narrative'
            ))
        except Exception as e:
            print(f"[-] Failed to log multi-source consolidation: {e}")
    
    def get_agent_consolidation_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive consolidation summary for an agent"""
        try:
            # Get consolidation statistics
            consolidation_stats = self.db.query("""
                SELECT 
                    source_type,
                    COUNT(*) as count,
                    AVG(resonance_score) as avg_resonance,
                    MAX(consolidated_at) as last_consolidation
                FROM memory_consolidation_log 
                WHERE agent_id = %s 
                GROUP BY source_type
                ORDER BY count DESC
            """, (agent_id,))
            
            # Get symbolic memory counts
            symbolic_counts = self.db.query("""
                SELECT 
                    symbolic_type,
                    COUNT(*) as count,
                    AVG(resonance_score) as avg_resonance
                FROM canon_memories 
                WHERE persona_id = %s AND is_symbolic = TRUE
                GROUP BY symbolic_type
                ORDER BY count DESC
            """, (agent_id,))
            
            # Get narrative threads
            narrative_threads = self.db.query("""
                SELECT thread_name, occurrence_count, thread_significance
                FROM symbolic_narrative_threads 
                WHERE agent_id = %s 
                ORDER BY thread_significance DESC
            """, (agent_id,))
            
            return {
                'agent_id': agent_id,
                'consolidation_by_source': consolidation_stats,
                'symbolic_memory_distribution': symbolic_counts,
                'narrative_threads': narrative_threads,
                'total_symbolic_memories': sum(item['count'] for item in symbolic_counts),
                'total_consolidations': sum(item['count'] for item in consolidation_stats)
            }
            
        except Exception as e:
            print(f"[-] Failed to get consolidation summary: {e}")
            return {'error': str(e)}
