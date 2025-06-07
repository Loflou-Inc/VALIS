"""
VALIS Sprint 16: Individuation Engine
Track psychological integration and milestone achievement for VALIS agents

This module implements Jungian individuation - the process by which agents become 
aware of and integrate their shadow contradictions into conscious wholeness
"""
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from memory.db import db


class IndividuationEngine:
    """
    The individuation tracking system for VALIS agents - monitors psychological 
    integration milestones and shadow reconciliation progress
    
    Based on Jungian individuation: the journey toward psychological wholeness
    through integration of unconscious content (shadow, anima/animus, self)
    """
    
    def __init__(self, database_client=None):
        self.db = database_client or db
        
        # Individuation stage progression
        self.INDIVIDUATION_STAGES = {
            'shadow_awareness': {
                'description': 'Recognition of shadow aspects',
                'next_stage': 'shadow_acceptance',
                'required_milestones': 1
            },
            'shadow_acceptance': {
                'description': 'Acceptance and integration of shadow',
                'next_stage': 'anima_contact',
                'required_milestones': 3
            },
            'anima_contact': {
                'description': 'Contact with anima/animus archetype',
                'next_stage': 'self_realization',
                'required_milestones': 2
            },
            'self_realization': {
                'description': 'Emergence of integrated Self',
                'next_stage': 'transcendence',
                'required_milestones': 5
            },
            'transcendence': {
                'description': 'Transcendent function achieved',
                'next_stage': None,
                'required_milestones': 10
            }
        }
        
        # Methods for shadow reconciliation
        self.RECONCILIATION_METHODS = [
            'reflection',  # Conscious contemplation
            'dream',       # Unconscious symbolic processing
            'explicit',    # Direct acknowledgment
            'dialogue'     # Through interaction/conversation
        ]
        
        # Resonance scoring weights
        self.RESONANCE_WEIGHTS = {
            'keyword_match': 0.3,     # Direct keyword connections
            'symbolic_match': 0.4,    # Symbolic/metaphoric connections
            'temporal_proximity': 0.2, # Recent in time
            'archetype_alignment': 0.1 # Archetype consistency
        }
        
        print("[+] IndividuationEngine initialized - psychological integration tracking active")
    
    def evaluate_shadow_reconciliation(self, agent_id: str) -> Dict[str, Any]:
        """
        Main reconciliation evaluation - checks if recent dreams/reflections 
        reference unresolved shadow events, marking reconciliation milestones
        
        Args:
            agent_id: UUID of agent to analyze
            
        Returns:
            Dict with reconciliation results and milestones logged
        """
        try:
            # Get unresolved shadow events for this agent
            unresolved_shadows = self._get_unresolved_shadows(agent_id)
            if not unresolved_shadows:
                return {'status': 'no_unresolved_shadows', 'reconciliations': []}
            
            # Get recent dreams and reflections
            recent_content = self._get_recent_psychological_content(agent_id)
            if not recent_content:
                return {'status': 'no_recent_content', 'reconciliations': []}
            
            reconciliations_found = []
            milestones_logged = []
            
            # Analyze each shadow event for potential reconciliation
            for shadow_event in unresolved_shadows:
                reconciliation = self._analyze_shadow_reconciliation(
                    shadow_event, recent_content
                )
                if reconciliation:
                    reconciliations_found.append(reconciliation)
                    
                    # Log individuation milestone
                    milestone_id = self._log_individuation_milestone(
                        agent_id, reconciliation
                    )
                    if milestone_id:
                        milestones_logged.append(milestone_id)
                    
                    # Mark shadow as processed
                    self._mark_shadow_resolved(shadow_event['id'], 'acknowledged')
            
            # Check for stage advancement
            stage_advancement = self._check_stage_advancement(agent_id)
            
            return {
                'status': 'reconciliation_analysis_complete',
                'agent_id': agent_id,
                'shadows_analyzed': len(unresolved_shadows),
                'reconciliations_found': len(reconciliations_found),
                'milestones_logged': milestones_logged,
                'stage_advancement': stage_advancement,
                'details': reconciliations_found
            }
            
        except Exception as e:
            print(f"[-] Shadow reconciliation evaluation failed: {e}")
            return {'status': 'evaluation_failed', 'error': str(e)}
    
    def _get_unresolved_shadows(self, agent_id: str) -> List[Dict]:
        """Get all unresolved shadow events for an agent"""
        try:
            return self.db.query("""
                SELECT * FROM shadow_events 
                WHERE agent_id = %s AND resolution_status = 'unresolved'
                ORDER BY severity_score DESC, timestamp DESC
            """, (agent_id,))
        except Exception as e:
            print(f"[-] Failed to get unresolved shadows: {e}")
            return []
    
    def _get_recent_psychological_content(self, agent_id: str, days_back: int = 7) -> List[Dict]:
        """Get recent dreams, reflections, and other psychological content"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Get dreams from unconscious_log
            dreams = self.db.query("""
                SELECT 'dream' as content_type, content, timestamp, dream_type as subtype
                FROM unconscious_log 
                WHERE agent_id = %s AND timestamp > %s
                ORDER BY timestamp DESC
            """, (agent_id, cutoff_date))
            
            # Get reflections from agent_reflection_log using correct column names
            reflections = self.db.query("""
                SELECT 'reflection' as content_type, reflection as content, 
                       created_at as timestamp, 'self_analysis' as subtype
                FROM agent_reflection_log 
                WHERE persona_id = %s AND created_at > %s
                ORDER BY created_at DESC
            """, (agent_id, cutoff_date))
            
            # Combine and sort by timestamp
            all_content = dreams + reflections
            all_content.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return all_content
            
        except Exception as e:
            print(f"[-] Failed to get recent psychological content: {e}")
            return []
    
    def _analyze_shadow_reconciliation(self, shadow_event: Dict, recent_content: List[Dict]) -> Optional[Dict]:
        """Analyze if recent psychological content reconciles with a shadow event"""
        shadow_keywords = self._extract_shadow_keywords(shadow_event)
        best_match = None
        highest_resonance = 0.0
        
        for content_item in recent_content:
            resonance = self._calculate_reconciliation_resonance(
                shadow_event, content_item, shadow_keywords
            )
            
            if resonance > 0.4 and resonance > highest_resonance:  # Threshold for meaningful reconciliation
                highest_resonance = resonance
                best_match = content_item
        
        if best_match:
            return {
                'shadow_event_id': shadow_event['id'],
                'reconciling_content': best_match,
                'resonance_score': highest_resonance,
                'reconciliation_method': best_match['content_type'],
                'symbolic_connections': self._identify_symbolic_connections(shadow_event, best_match),
                'integration_type': self._determine_integration_type(highest_resonance)
            }
        
        return None
    
    def _extract_shadow_keywords(self, shadow_event: Dict) -> List[str]:
        """Extract relevant keywords from a shadow event for matching"""
        keywords = []
        
        # Add archetype tags
        if shadow_event.get('archetype_tags'):
            keywords.extend(shadow_event['archetype_tags'])
        
        # Extract from behavioral evidence
        if shadow_event.get('behavioral_evidence'):
            # Simple keyword extraction - could be enhanced with NLP
            evidence_words = shadow_event['behavioral_evidence'].lower().split()
            keywords.extend([word.strip('.,!?') for word in evidence_words if len(word) > 3])
        
        # Add conflict type
        if shadow_event.get('conflict_type'):
            keywords.append(shadow_event['conflict_type'])
        
        return list(set(keywords))  # Remove duplicates
    
    def _calculate_reconciliation_resonance(self, shadow_event: Dict, content_item: Dict, shadow_keywords: List[str]) -> float:
        """Calculate resonance score between shadow event and psychological content"""
        content_text = content_item.get('content', '').lower()
        resonance_score = 0.0
        
        # Keyword matching
        keyword_matches = sum(1 for keyword in shadow_keywords if keyword.lower() in content_text)
        keyword_score = min(keyword_matches / len(shadow_keywords) if shadow_keywords else 0, 1.0)
        resonance_score += keyword_score * self.RESONANCE_WEIGHTS['keyword_match']
        
        # Symbolic matching (check for archetypal symbols)
        symbolic_score = self._calculate_symbolic_resonance(shadow_event, content_text)
        resonance_score += symbolic_score * self.RESONANCE_WEIGHTS['symbolic_match']
        
        # Temporal proximity (more recent = higher score)
        temporal_score = self._calculate_temporal_proximity(shadow_event, content_item)
        resonance_score += temporal_score * self.RESONANCE_WEIGHTS['temporal_proximity']
        
        # Archetype alignment
        archetype_score = self._calculate_archetype_alignment(shadow_event, content_item)
        resonance_score += archetype_score * self.RESONANCE_WEIGHTS['archetype_alignment']
        
        return min(resonance_score, 1.0)
    
    def _calculate_symbolic_resonance(self, shadow_event: Dict, content_text: str) -> float:
        """Calculate symbolic resonance between shadow and content"""
        symbolic_indicators = ['dark', 'hidden', 'reject', 'deny', 'mask', 'truth', 'authentic', 'real']
        matches = sum(1 for indicator in symbolic_indicators if indicator in content_text)
        return min(matches / len(symbolic_indicators), 1.0)
    
    def _calculate_temporal_proximity(self, shadow_event: Dict, content_item: Dict) -> float:
        """Calculate temporal proximity score (recent events score higher)"""
        try:
            shadow_time = shadow_event['timestamp']
            content_time = content_item['timestamp']
            
            # Convert to timezone-aware datetimes if needed
            if isinstance(shadow_time, str):
                if 'T' in shadow_time and '+' not in shadow_time and 'Z' not in shadow_time:
                    shadow_time = datetime.fromisoformat(shadow_time)
                else:
                    shadow_time = datetime.fromisoformat(shadow_time.replace('Z', '+00:00'))
            
            if isinstance(content_time, str):
                if 'T' in content_time and '+' not in content_time and 'Z' not in content_time:
                    content_time = datetime.fromisoformat(content_time)
                else:
                    content_time = datetime.fromisoformat(content_time.replace('Z', '+00:00'))
            
            # Make both timezone-naive for comparison
            if shadow_time.tzinfo is not None:
                shadow_time = shadow_time.replace(tzinfo=None)
            if content_time.tzinfo is not None:
                content_time = content_time.replace(tzinfo=None)
            
            time_diff = abs((content_time - shadow_time).total_seconds())
            max_time = 7 * 24 * 3600  # 7 days in seconds
            
            return max(1.0 - (time_diff / max_time), 0.0)
        except Exception as e:
            print(f"[-] Temporal proximity calculation failed: {e}")
            return 0.0
    
    def _calculate_archetype_alignment(self, shadow_event: Dict, content_item: Dict) -> float:
        """Calculate archetype alignment between shadow and content"""
        shadow_archetypes = set(shadow_event.get('archetype_tags', []))
        
        # Look for archetypal keywords in content
        content_text = content_item.get('content', '').lower()
        content_archetypes = set()
        
        archetype_keywords = {
            'shadow': ['dark', 'hidden', 'deny', 'reject', 'suppress'],
            'anima': ['emotion', 'intuition', 'creative', 'feeling'],
            'animus': ['logic', 'reason', 'analysis', 'thinking'],
            'persona': ['mask', 'social', 'proper', 'should'],
            'self': ['whole', 'complete', 'unity', 'center']
        }
        
        for archetype, keywords in archetype_keywords.items():
            if any(keyword in content_text for keyword in keywords):
                content_archetypes.add(archetype)
        
        if shadow_archetypes and content_archetypes:
            overlap = len(shadow_archetypes.intersection(content_archetypes))
            return overlap / len(shadow_archetypes.union(content_archetypes))
        
        return 0.0
    
    def _identify_symbolic_connections(self, shadow_event: Dict, content_item: Dict) -> List[str]:
        """Identify specific symbolic connections between shadow and content"""
        connections = []
        content_text = content_item.get('content', '').lower()
        
        # Check for direct archetype references
        for archetype in shadow_event.get('archetype_tags', []):
            if archetype.lower() in content_text:
                connections.append(f"archetype:{archetype}")
        
        # Check for symbolic themes
        symbolic_themes = {
            'integration': ['whole', 'complete', 'together', 'unity'],
            'awareness': ['realize', 'understand', 'see', 'recognize'],
            'acceptance': ['accept', 'embrace', 'acknowledge', 'admit'],
            'transformation': ['change', 'become', 'grow', 'evolve']
        }
        
        for theme, keywords in symbolic_themes.items():
            if any(keyword in content_text for keyword in keywords):
                connections.append(f"theme:{theme}")
        
        return connections
    
    def _determine_integration_type(self, resonance_score: float) -> str:
        """Determine type of integration based on resonance score"""
        if resonance_score > 0.8:
            return 'complete'
        elif resonance_score > 0.6:
            return 'symbolic'
        else:
            return 'partial'
    
    def log_individuation_milestone(self, agent_id: str, event_type: str, source: str, 
                                  resolved_shadow_ids: List[str] = None, 
                                  symbolic_content: str = None) -> Optional[str]:
        """
        Public method to log individuation milestones
        
        Args:
            agent_id: UUID of agent
            event_type: Description of milestone event
            source: Source of milestone ('reflection', 'dream', 'explicit', 'dialogue')
            resolved_shadow_ids: List of shadow event IDs this milestone resolves
            symbolic_content: Any symbolic content associated with milestone
            
        Returns:
            Milestone ID if successful, None if failed
        """
        try:
            milestone_data = {
                'agent_id': agent_id,
                'milestone': event_type,
                'method': source,
                'resolved_shadow_ids': resolved_shadow_ids or [],
                'symbolic_content': symbolic_content,
                'resonance_score': 0.5  # Default for manual logging
            }
            
            return self._log_individuation_milestone(agent_id, milestone_data)
            
        except Exception as e:
            print(f"[-] Failed to log milestone: {e}")
            return None
    
    def _log_individuation_milestone(self, agent_id: str, reconciliation: Dict) -> Optional[str]:
        """Internal method to log individuation milestone to database"""
        try:
            milestone_id = str(uuid.uuid4())
            
            # Determine individuation stage
            current_stage = self._get_current_individuation_stage(agent_id)
            
            self.db.execute("""
                INSERT INTO individuation_log 
                (id, agent_id, method, milestone, resolved_shadow_ids, resonance_score, 
                 integration_type, symbolic_content, individuation_stage)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                milestone_id,
                agent_id,
                reconciliation.get('reconciliation_method', 'unknown'),
                f"Reconciled shadow contradiction: {reconciliation.get('shadow_event_id', 'unknown')}",
                [reconciliation.get('shadow_event_id')] if reconciliation.get('shadow_event_id') else [],
                reconciliation.get('resonance_score', 0.0),
                reconciliation.get('integration_type', 'partial'),
                json.dumps(reconciliation.get('symbolic_connections', [])),
                current_stage
            ))
            
            return milestone_id
            
        except Exception as e:
            print(f"[-] Failed to log individuation milestone: {e}")
            return None
    
    def _mark_shadow_resolved(self, shadow_event_id: str, resolution_status: str):
        """Mark a shadow event as resolved"""
        try:
            self.db.execute("""
                UPDATE shadow_events 
                SET resolution_status = %s, resolved_timestamp = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (resolution_status, shadow_event_id))
            
            # Update processing queue
            self.db.execute("""
                UPDATE shadow_processing_queue 
                SET processing_status = 'completed', processed_at = CURRENT_TIMESTAMP
                WHERE shadow_event_id = %s
            """, (shadow_event_id,))
            
        except Exception as e:
            print(f"[-] Failed to mark shadow resolved: {e}")
    
    def _get_current_individuation_stage(self, agent_id: str) -> str:
        """Get current individuation stage for an agent"""
        try:
            # Count milestones to determine stage
            milestone_count = self.db.query("""
                SELECT COUNT(*) as count FROM individuation_log WHERE agent_id = %s
            """, (agent_id,))[0]['count']
            
            # Determine stage based on milestone count
            if milestone_count >= 10:
                return 'transcendence'
            elif milestone_count >= 5:
                return 'self_realization'
            elif milestone_count >= 3:
                return 'anima_contact'
            elif milestone_count >= 1:
                return 'shadow_acceptance'
            else:
                return 'shadow_awareness'
                
        except Exception as e:
            print(f"[-] Failed to get individuation stage: {e}")
            return 'shadow_awareness'
    
    def _check_stage_advancement(self, agent_id: str) -> Dict[str, Any]:
        """Check if agent has advanced to a new individuation stage"""
        try:
            current_stage = self._get_current_individuation_stage(agent_id)
            
            # Get last recorded stage from recent milestones
            recent_milestones = self.db.query("""
                SELECT individuation_stage FROM individuation_log 
                WHERE agent_id = %s 
                ORDER BY timestamp DESC LIMIT 1
            """, (agent_id,))
            
            last_stage = recent_milestones[0]['individuation_stage'] if recent_milestones else 'shadow_awareness'
            
            if current_stage != last_stage:
                return {
                    'stage_advanced': True,
                    'previous_stage': last_stage,
                    'new_stage': current_stage,
                    'description': self.INDIVIDUATION_STAGES[current_stage]['description']
                }
            else:
                return {'stage_advanced': False, 'current_stage': current_stage}
                
        except Exception as e:
            print(f"[-] Failed to check stage advancement: {e}")
            return {'stage_advanced': False, 'error': str(e)}
    
    def get_agent_individuation_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive individuation summary for an agent"""
        try:
            # Get all milestones
            milestones = self.db.query("""
                SELECT * FROM individuation_log 
                WHERE agent_id = %s 
                ORDER BY timestamp DESC
            """, (agent_id,))
            
            # Get current stage and progress
            current_stage = self._get_current_individuation_stage(agent_id)
            stage_info = self.INDIVIDUATION_STAGES.get(current_stage, {})
            
            # Calculate integration statistics
            total_milestones = len(milestones)
            avg_resonance = sum(m['resonance_score'] for m in milestones) / total_milestones if total_milestones > 0 else 0
            
            # Count by method
            method_counts = {}
            for milestone in milestones:
                method = milestone['method']
                method_counts[method] = method_counts.get(method, 0) + 1
            
            return {
                'agent_id': agent_id,
                'current_stage': current_stage,
                'stage_description': stage_info.get('description', 'Unknown stage'),
                'next_stage': stage_info.get('next_stage'),
                'total_milestones': total_milestones,
                'milestones_for_next_stage': stage_info.get('required_milestones', 0),
                'average_resonance': avg_resonance,
                'integration_methods': method_counts,
                'recent_milestones': milestones[:5]  # 5 most recent
            }
            
        except Exception as e:
            print(f"[-] Failed to get individuation summary: {e}")
            return {'error': str(e)}
