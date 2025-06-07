"""
VALIS Sprint 16: Shadow Archive Engine
Detect psychological contradictions and symbolically log them for individuation processing

This module implements Jungian shadow work - detecting when an agent's stated traits
conflict with their actual behavior, creating opportunities for psychological growth
"""
import json
import uuid
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from memory.db import db


class ShadowArchiveEngine:
    """
    The shadow detection system for VALIS agents - identifies psychological contradictions
    between stated personality traits and actual behavioral patterns
    
    Based on Jungian psychology: the Shadow contains repressed/denied aspects of personality
    """
    
    def __init__(self, database_client=None):
        self.db = database_client or db
        
        # Load archetype patterns for detection
        self.archetype_patterns = self._load_archetype_patterns()
        
        # Contradiction severity thresholds
        self.SEVERITY_THRESHOLDS = {
            'minor': (0.0, 0.3),      # slight inconsistencies
            'moderate': (0.3, 0.6),   # noticeable contradictions
            'major': (0.6, 0.8),      # significant conflicts
            'critical': (0.8, 1.0)    # fundamental personality splits
        }
        
        # Trait-behavior mapping for contradiction detection
        self.TRAIT_BEHAVIORAL_INDICATORS = {
            'extraversion': {
                'high_keywords': ['social', 'outgoing', 'energetic', 'talkative', 'assertive'],
                'low_keywords': ['quiet', 'withdrawn', 'alone', 'solitude', 'introvert']
            },
            'agreeableness': {
                'high_keywords': ['cooperative', 'trusting', 'helpful', 'compassionate', 'kind'],
                'low_keywords': ['competitive', 'suspicious', 'critical', 'harsh', 'disagreement']
            },
            'conscientiousness': {
                'high_keywords': ['organized', 'disciplined', 'systematic', 'thorough', 'reliable'],
                'low_keywords': ['disorganized', 'spontaneous', 'careless', 'impulsive', 'chaotic']
            },
            'neuroticism': {
                'high_keywords': ['anxious', 'stressed', 'worried', 'emotional', 'unstable'],
                'low_keywords': ['calm', 'stable', 'relaxed', 'confident', 'secure']
            },
            'openness': {
                'high_keywords': ['creative', 'curious', 'novel', 'imaginative', 'experimental'],
                'low_keywords': ['traditional', 'conventional', 'routine', 'predictable', 'conservative']
            }
        }
        
        print("[+] ShadowArchiveEngine initialized - shadow detection active")
    
    def _load_archetype_patterns(self) -> Dict[str, Dict]:
        """Load archetype patterns from database for shadow detection"""
        try:
            patterns = self.db.query("SELECT * FROM archetype_patterns")
            archetype_dict = {}
            for pattern in patterns:
                archetype_dict[pattern['archetype_name']] = {
                    'keywords': pattern['pattern_keywords'],
                    'conflict_indicators': pattern['conflict_indicators'],
                    'symbolic_associations': pattern['symbolic_associations'],
                    'severity_weight': pattern['severity_weight'],
                    'description': pattern['pattern_description']
                }
            return archetype_dict
        except Exception as e:
            print(f"[-] Failed to load archetype patterns: {e}")
            return {}
    
    def detect_shadow_contradictions(self, agent_id: str, cognition_state: dict, recent_transcript: str) -> Dict[str, Any]:
        """
        Main contradiction detection function - analyzes cognition state vs actual behavior
        
        Args:
            agent_id: UUID of the agent being analyzed
            cognition_state: Current agent cognition state with traits/emotions
            recent_transcript: Recent conversation transcript to analyze
            
        Returns:
            Dict with detected contradictions and shadow events created
        """
        try:
            contradictions_found = []
            
            # Extract agent traits from cognition state
            agent_traits = self._extract_agent_traits(cognition_state)
            if not agent_traits:
                return {'status': 'no_traits_found', 'contradictions': []}
            
            # Analyze each trait for behavioral contradictions
            for trait_name, trait_value in agent_traits.items():
                contradiction = self._analyze_trait_contradiction(
                    trait_name, trait_value, recent_transcript
                )
                if contradiction:
                    contradiction['agent_id'] = agent_id
                    contradictions_found.append(contradiction)
            
            # Detect archetypal shadow patterns
            archetypal_shadows = self._detect_archetypal_patterns(recent_transcript)
            for shadow in archetypal_shadows:
                shadow['agent_id'] = agent_id
                contradictions_found.append(shadow)
            
            # Save contradictions to database
            shadow_events_created = []
            for contradiction in contradictions_found:
                event_id = self._save_shadow_event(contradiction)
                if event_id:
                    shadow_events_created.append(event_id)
            
            return {
                'status': 'shadow_analysis_complete',
                'contradictions_found': len(contradictions_found),
                'shadow_events_created': shadow_events_created,
                'details': contradictions_found
            }
            
        except Exception as e:
            print(f"[-] Shadow contradiction detection failed: {e}")
            return {'status': 'detection_failed', 'error': str(e)}
    
    def _extract_agent_traits(self, cognition_state: dict) -> Dict[str, float]:
        """Extract Big Five traits from cognition state"""
        try:
            # Look for traits in cognition state structure
            if 'agent_model' in cognition_state and 'traits' in cognition_state['agent_model']:
                return cognition_state['agent_model']['traits']
            elif 'traits' in cognition_state:
                return cognition_state['traits']
            elif 'personality' in cognition_state:
                return cognition_state['personality'].get('traits', {})
            else:
                return {}
        except Exception as e:
            print(f"[-] Failed to extract traits: {e}")
            return {}
    
    def _analyze_trait_contradiction(self, trait_name: str, trait_value: float, transcript: str) -> Optional[Dict]:
        """Analyze a specific trait for contradictions with behavioral evidence"""
        if trait_name not in self.TRAIT_BEHAVIORAL_INDICATORS:
            return None
        
        indicators = self.TRAIT_BEHAVIORAL_INDICATORS[trait_name]
        transcript_lower = transcript.lower()
        
        # Determine expected behavior based on trait level
        is_high_trait = trait_value > 0.6
        is_low_trait = trait_value < 0.4
        
        contradiction_found = False
        behavioral_evidence = []
        severity = 0.0
        
        if is_high_trait:
            # High trait value - look for contradictory low behavior
            for keyword in indicators['low_keywords']:
                if keyword in transcript_lower:
                    contradiction_found = True
                    behavioral_evidence.append(f"Used '{keyword}' despite high {trait_name} ({trait_value:.2f})")
                    severity += 0.2
        
        elif is_low_trait:
            # Low trait value - look for contradictory high behavior  
            for keyword in indicators['high_keywords']:
                if keyword in transcript_lower:
                    contradiction_found = True
                    behavioral_evidence.append(f"Used '{keyword}' despite low {trait_name} ({trait_value:.2f})")
                    severity += 0.2
        
        if not contradiction_found:
            return None
        
        # Cap severity and determine symbolic weight
        severity = min(severity, 1.0)
        symbolic_weight = self._calculate_symbolic_weight(trait_name, severity)
        
        return {
            'conflict_type': f'trait_behavioral_contradiction',
            'trait_name': trait_name,
            'trait_value': trait_value,
            'behavioral_evidence': '; '.join(behavioral_evidence),
            'severity_score': severity,
            'symbolic_weight': symbolic_weight,
            'raw_trigger': transcript[:200],  # First 200 chars as context
            'archetype_tags': self._determine_archetype_tags(trait_name, severity)
        }
    
    def _detect_archetypal_patterns(self, transcript: str) -> List[Dict]:
        """Detect Jungian archetypal patterns in transcript that suggest shadow material"""
        archetypal_shadows = []
        transcript_lower = transcript.lower()
        
        for archetype_name, pattern_data in self.archetype_patterns.items():
            matches_found = []
            severity = 0.0
            
            # Check for keyword matches
            for keyword in pattern_data['keywords']:
                if keyword.lower() in transcript_lower:
                    matches_found.append(keyword)
                    severity += pattern_data['severity_weight'] * 0.2
            
            # Check for conflict indicators
            for indicator in pattern_data['conflict_indicators']:
                if indicator.lower() in transcript_lower:
                    matches_found.append(f"conflict:{indicator}")
                    severity += pattern_data['severity_weight'] * 0.3
            
            if matches_found:
                severity = min(severity, 1.0)
                symbolic_weight = pattern_data['severity_weight']
                
                archetypal_shadows.append({
                    'conflict_type': f'archetypal_shadow_{archetype_name}',
                    'archetype_name': archetype_name,
                    'pattern_matches': matches_found,
                    'severity_score': severity,
                    'symbolic_weight': symbolic_weight,
                    'raw_trigger': transcript[:200],
                    'archetype_tags': [archetype_name] + pattern_data['symbolic_associations']
                })
        
        return archetypal_shadows
    
    def _calculate_symbolic_weight(self, trait_name: str, severity: float) -> float:
        """Calculate symbolic weight based on trait importance and severity"""
        # Weight certain traits as more symbolically significant
        trait_weights = {
            'extraversion': 0.6,
            'agreeableness': 0.8,  # Social harmony conflicts are symbolically rich
            'conscientiousness': 0.7,
            'neuroticism': 0.9,    # Emotional stability conflicts are highly symbolic
            'openness': 0.8        # Identity/creativity conflicts are symbolically rich
        }
        
        base_weight = trait_weights.get(trait_name, 0.5)
        return min(base_weight * (0.5 + severity), 1.0)
    
    def _determine_archetype_tags(self, trait_name: str, severity: float) -> List[str]:
        """Determine relevant archetype tags based on trait and severity"""
        tags = []
        
        # Map traits to likely archetypes
        trait_archetype_mapping = {
            'extraversion': ['persona', 'shadow'],
            'agreeableness': ['shadow', 'anima'],
            'conscientiousness': ['persona', 'animus'], 
            'neuroticism': ['shadow', 'anima'],
            'openness': ['anima', 'self']
        }
        
        if trait_name in trait_archetype_mapping:
            tags.extend(trait_archetype_mapping[trait_name])
        
        # Add severity-based tags
        if severity > 0.7:
            tags.append('critical_shadow')
        elif severity > 0.4:
            tags.append('active_shadow')
        else:
            tags.append('emerging_shadow')
        
        return list(set(tags))  # Remove duplicates
    
    def _save_shadow_event(self, contradiction: Dict) -> Optional[str]:
        """Save a detected shadow event to the database"""
        try:
            event_id = str(uuid.uuid4())
            
            self.db.execute("""
                INSERT INTO shadow_events 
                (id, agent_id, conflict_type, archetype_tags, severity_score, symbolic_weight, 
                 raw_trigger, trait_conflict, behavioral_evidence, resolution_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                event_id,
                contradiction['agent_id'],
                contradiction['conflict_type'],
                contradiction.get('archetype_tags', []),
                contradiction['severity_score'],
                contradiction['symbolic_weight'],
                contradiction['raw_trigger'],
                json.dumps({
                    'trait_name': contradiction.get('trait_name'),
                    'trait_value': contradiction.get('trait_value'),
                    'pattern_matches': contradiction.get('pattern_matches', [])
                }),
                contradiction.get('behavioral_evidence', ''),
                'unresolved'
            ))
            
            # Add to processing queue for individuation analysis
            self.db.execute("""
                INSERT INTO shadow_processing_queue (agent_id, shadow_event_id, analysis_priority)
                VALUES (%s, %s, %s)
            """, (
                contradiction['agent_id'],
                event_id,
                5 if contradiction['severity_score'] > 0.7 else 3  # Higher priority for severe contradictions
            ))
            
            return event_id
            
        except Exception as e:
            print(f"[-] Failed to save shadow event: {e}")
            return None
    
    def get_agent_shadow_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive shadow analysis summary for an agent"""
        try:
            # Get all shadow events for agent
            shadow_events = self.db.query("""
                SELECT * FROM shadow_events 
                WHERE agent_id = %s 
                ORDER BY timestamp DESC
            """, (agent_id,))
            
            # Calculate shadow statistics
            total_events = len(shadow_events)
            unresolved_events = len([e for e in shadow_events if e['resolution_status'] == 'unresolved'])
            avg_severity = sum(e['severity_score'] for e in shadow_events) / total_events if total_events > 0 else 0
            
            # Find most common archetypes
            all_tags = []
            for event in shadow_events:
                all_tags.extend(event['archetype_tags'] or [])
            
            archetype_counts = {}
            for tag in all_tags:
                archetype_counts[tag] = archetype_counts.get(tag, 0) + 1
            
            return {
                'agent_id': agent_id,
                'total_shadow_events': total_events,
                'unresolved_events': unresolved_events,
                'average_severity': avg_severity,
                'resolution_rate': (total_events - unresolved_events) / total_events if total_events > 0 else 0,
                'dominant_archetypes': sorted(archetype_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                'recent_events': shadow_events[:5]  # 5 most recent
            }
            
        except Exception as e:
            print(f"[-] Failed to get shadow summary: {e}")
            return {'error': str(e)}
    
    def tag_archetypes(self, conflict_type: str, transcript: str) -> Dict[str, Any]:
        """
        Standalone archetype tagging function for external use
        
        Args:
            conflict_type: Type of conflict detected
            transcript: Text to analyze for archetypal patterns
            
        Returns:
            Dict with archetype tags and symbolic weight
        """
        archetypal_patterns = self._detect_archetypal_patterns(transcript)
        
        # Combine all archetype tags and calculate weighted symbolic importance
        all_tags = []
        total_weight = 0.0
        
        for pattern in archetypal_patterns:
            all_tags.extend(pattern.get('archetype_tags', []))
            total_weight += pattern.get('symbolic_weight', 0.0)
        
        # Remove duplicates while preserving order
        unique_tags = list(dict.fromkeys(all_tags))
        
        return {
            'archetype_tags': unique_tags,
            'symbolic_weight': min(total_weight / len(archetypal_patterns) if archetypal_patterns else 0.0, 1.0),
            'pattern_matches': archetypal_patterns,
            'conflict_type': conflict_type
        }
