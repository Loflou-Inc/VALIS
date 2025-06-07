"""
VALIS Sprint 13: Trait Drift Engine
Core module for personality trait evolution based on dialogue patterns and feedback
"""
import json
import re
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from memory.db import db


class TraitDriftEngine:
    """
    Engine for evolving personality traits over time based on:
    - User feedback patterns
    - Dialogue tone and content
    - Reflection success/failure outcomes
    - Temporal decay of unused modifiers
    """
    
    def __init__(self, database_client=None):
        self.db = database_client or db
        
        # Learning rate constants
        self.FEEDBACK_LEARNING_RATE = 0.15  # Strong feedback has major impact
        self.TONE_LEARNING_RATE = 0.08      # Gradual drift from dialogue patterns
        self.REFLECTION_LEARNING_RATE = 0.12 # Medium impact from self-reflection
        self.DECAY_RATE = 0.02              # Unused traits fade slowly
        
        # Trait bounds (prevent extreme drift)
        self.TRAIT_MIN = 0.0
        self.TRAIT_MAX = 1.0
        self.MAX_SINGLE_DRIFT = 0.25        # Maximum change per session
        
        print("[+] TraitDriftEngine initialized")
    
    def update_traits_from_dialogue(self, session_id: str, persona_id: str, 
                                   transcript: str, feedback: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Primary method: Analyze dialogue and update personality traits
        
        Args:
            session_id: Current session identifier
            persona_id: Persona UUID 
            transcript: Full conversation transcript
            feedback: List of feedback events from user/system
            
        Returns:
            Dictionary with trait changes and analysis
        """
        try:
            print(f"Analyzing trait drift for {persona_id} in session {session_id}")
            
            # Get current trait state
            current_traits = self._get_current_traits(persona_id)
            if not current_traits:
                print(f"[-] No personality profile found for {persona_id}")
                return {"error": "No personality profile found"}
            
            # Analyze different influence sources
            feedback_influences = self._analyze_feedback_influences(feedback)
            dialogue_influences = self._analyze_dialogue_patterns(transcript)
            reflection_influences = self._analyze_reflection_outcomes(session_id, persona_id)
            
            # Calculate trait deltas
            trait_deltas = self._calculate_trait_deltas(
                current_traits, feedback_influences, dialogue_influences, reflection_influences
            )
            
            # Apply constraints and bounds
            bounded_deltas = self._apply_bounds_and_constraints(current_traits, trait_deltas)
            
            # Update traits in database
            updated_traits = self._apply_trait_updates(persona_id, current_traits, bounded_deltas)
            
            # Log trait history
            self._log_trait_changes(persona_id, session_id, current_traits, updated_traits, {
                "feedback": feedback_influences,
                "dialogue": dialogue_influences, 
                "reflection": reflection_influences
            })
            
            return {
                "session_id": session_id,
                "persona_id": persona_id,
                "traits_before": current_traits,
                "traits_after": updated_traits,
                "deltas": bounded_deltas,
                "influences": {
                    "feedback": feedback_influences,
                    "dialogue": dialogue_influences,
                    "reflection": reflection_influences
                },
                "significant_changes": [
                    trait for trait, delta in bounded_deltas.items() 
                    if abs(delta) > 0.05
                ]
            }
            
        except Exception as e:
            print(f"[-] Trait drift analysis failed: {e}")
            return {"error": str(e)}
    
    def _get_current_traits(self, persona_id: str) -> Dict[str, float]:
        """Get current personality traits for a persona"""
        try:
            # Check if we have an evolving traits profile
            profile = self.db.query("""
                SELECT base_traits, learned_modifiers FROM agent_personality_profiles
                WHERE persona_id = %s
            """, (persona_id,))
            
            if not profile:
                return {}
                
            base_traits = profile[0]['base_traits'] or {}
            learned_modifiers = profile[0]['learned_modifiers'] or {}
            
            # Merge base traits with learned modifiers
            # Learned modifiers can influence base traits over time
            current_traits = dict(base_traits)
            
            # Apply learned modifier influences to base traits
            modifier_influences = {
                'prefers_brevity': {'conscientiousness': 0.1},
                'prefers_detail': {'conscientiousness': -0.1, 'openness': 0.1},
                'prefers_formality': {'conscientiousness': 0.1, 'agreeableness': -0.05},
                'prefers_casual': {'extraversion': 0.1, 'agreeableness': 0.05},
                'prefers_energetic': {'extraversion': 0.15},
                'prefers_subdued': {'extraversion': -0.1, 'emotional_stability': 0.05}
            }
            
            for modifier, weight in learned_modifiers.items():
                if modifier in modifier_influences:
                    for trait, influence in modifier_influences[modifier].items():
                        if trait in current_traits:
                            # Apply weighted influence
                            current_traits[trait] += influence * weight * 0.1  # Gentle influence
                            current_traits[trait] = max(0.0, min(1.0, current_traits[trait]))
            
            return current_traits
            
        except Exception as e:
            print(f"[-] Failed to get current traits: {e}")
            return {}
    
    def _analyze_feedback_influences(self, feedback: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze user feedback patterns for trait influences"""
        influences = {}
        
        for fb in feedback:
            feedback_type = fb.get('type', 'neutral')
            feedback_text = fb.get('text', '').lower()
            
            # Positive feedback patterns
            if feedback_type == 'positive':
                if any(word in feedback_text for word in ['enthusiastic', 'energetic', 'excited']):
                    influences['extraversion'] = influences.get('extraversion', 0) + 0.1
                    
                if any(word in feedback_text for word in ['helpful', 'kind', 'supportive']):
                    influences['agreeableness'] = influences.get('agreeableness', 0) + 0.1
                    
                if any(word in feedback_text for word in ['creative', 'innovative', 'interesting']):
                    influences['openness'] = influences.get('openness', 0) + 0.1
                    
                if any(word in feedback_text for word in ['organized', 'systematic', 'thorough']):
                    influences['conscientiousness'] = influences.get('conscientiousness', 0) + 0.1
            
            # Negative feedback patterns
            elif feedback_type == 'negative':
                if any(word in feedback_text for word in ['too loud', 'too much', 'overwhelming']):
                    influences['extraversion'] = influences.get('extraversion', 0) - 0.1
                    
                if any(word in feedback_text for word in ['rude', 'unhelpful', 'dismissive']):
                    influences['agreeableness'] = influences.get('agreeableness', 0) - 0.1
                    
                if any(word in feedback_text for word in ['boring', 'predictable', 'same old']):
                    influences['openness'] = influences.get('openness', 0) - 0.1
            
            # Correction patterns
            elif feedback_type == 'correction':
                if any(word in feedback_text for word in ['be more confident', 'stop hedging']):
                    influences['emotional_stability'] = influences.get('emotional_stability', 0) + 0.15
                    
                if any(word in feedback_text for word in ['be more careful', 'double check']):
                    influences['conscientiousness'] = influences.get('conscientiousness', 0) + 0.1
        
        return influences
    
    def _analyze_dialogue_patterns(self, transcript: str) -> Dict[str, float]:
        """Analyze dialogue patterns for trait drift signals"""
        influences = {}
        
        if not transcript:
            return influences
        
        transcript_lower = transcript.lower()
        
        # User language patterns that might influence persona traits
        patterns = {
            'extraversion': {
                'positive': ['exciting', 'fun', 'awesome', 'love it', 'great energy'],
                'negative': ['too loud', 'calm down', 'quiet', 'tone it down']
            },
            'agreeableness': {
                'positive': ['thanks', 'helpful', 'appreciate', 'kind', 'supportive'],
                'negative': ['rude', 'not helpful', 'dismissive', 'cold']
            },
            'conscientiousness': {
                'positive': ['thorough', 'detailed', 'organized', 'systematic', 'careful'],
                'negative': ['sloppy', 'careless', 'rushed', 'incomplete']
            },
            'openness': {
                'positive': ['creative', 'interesting', 'novel', 'innovative', 'unique'],
                'negative': ['boring', 'predictable', 'same old', 'conventional']
            },
            'emotional_stability': {
                'positive': ['confident', 'calm', 'steady', 'reliable', 'balanced'],
                'negative': ['nervous', 'anxious', 'uncertain', 'worried']
            }
        }
        
        for trait, pattern_set in patterns.items():
            positive_score = sum(1 for word in pattern_set['positive'] if word in transcript_lower)
            negative_score = sum(1 for word in pattern_set['negative'] if word in transcript_lower)
            
            # Calculate net influence (normalized by transcript length)
            transcript_words = len(transcript_lower.split())
            if transcript_words > 0:
                net_score = (positive_score - negative_score) / max(transcript_words / 100, 1)
                if abs(net_score) > 0.01:  # Only significant patterns
                    influences[trait] = net_score * 0.5  # Moderate influence
        
        return influences
    
    def _analyze_reflection_outcomes(self, session_id: str, persona_id: str) -> Dict[str, float]:
        """Analyze reflection logs for trait influences"""
        influences = {}
        
        try:
            # Get recent reflection logs for this session
            reflections = self.db.query("""
                SELECT reflection, plan_success_score, ego_alignment_score 
                FROM agent_reflection_log
                WHERE session_id = %s AND persona_id = %s
                ORDER BY created_at DESC
                LIMIT 3
            """, (session_id, persona_id))
            
            for reflection in reflections:
                reflection_text = reflection['reflection'].lower()
                insights_score = reflection['plan_success_score']
                mood_score = reflection['ego_alignment_score']
                
                # High insight scores suggest good conscientiousness
                if insights_score > 0.8:
                    influences['conscientiousness'] = influences.get('conscientiousness', 0) + 0.05
                elif insights_score < 0.3:
                    influences['conscientiousness'] = influences.get('conscientiousness', 0) - 0.03
                
                # Mood scores influence emotional stability
                if mood_score > 0.7:
                    influences['emotional_stability'] = influences.get('emotional_stability', 0) + 0.03
                elif mood_score < 0.3:
                    influences['emotional_stability'] = influences.get('emotional_stability', 0) - 0.05
                
                # Text analysis of reflection content
                if any(word in reflection_text for word in ['confident', 'successful', 'accomplished']):
                    influences['emotional_stability'] = influences.get('emotional_stability', 0) + 0.05
                    
                if any(word in reflection_text for word in ['struggled', 'difficult', 'uncertain']):
                    influences['emotional_stability'] = influences.get('emotional_stability', 0) - 0.03
                    
                if any(word in reflection_text for word in ['creative', 'innovative', 'new approach']):
                    influences['openness'] = influences.get('openness', 0) + 0.05
        
        except Exception as e:
            print(f"[-] Reflection analysis failed: {e}")
        
        return influences
    
    def _calculate_trait_deltas(self, current_traits: Dict[str, float], 
                               feedback_influences: Dict[str, float],
                               dialogue_influences: Dict[str, float], 
                               reflection_influences: Dict[str, float]) -> Dict[str, float]:
        """Calculate final trait delta values with weighted influences"""
        deltas = {}
        
        # All Big Five traits
        all_traits = ['extraversion', 'agreeableness', 'conscientiousness', 'emotional_stability', 'openness']
        
        for trait in all_traits:
            delta = 0.0
            
            # Apply feedback influence (strongest)
            if trait in feedback_influences:
                delta += feedback_influences[trait] * self.FEEDBACK_LEARNING_RATE
            
            # Apply dialogue influence (moderate)
            if trait in dialogue_influences:
                delta += dialogue_influences[trait] * self.TONE_LEARNING_RATE
            
            # Apply reflection influence (moderate-strong)  
            if trait in reflection_influences:
                delta += reflection_influences[trait] * self.REFLECTION_LEARNING_RATE
            
            if abs(delta) > 0.001:  # Only store meaningful changes
                deltas[trait] = delta
        
        return deltas
    
    def _apply_bounds_and_constraints(self, current_traits: Dict[str, float], 
                                    trait_deltas: Dict[str, float]) -> Dict[str, float]:
        """Apply bounds and constraints to trait changes"""
        bounded_deltas = {}
        
        for trait, delta in trait_deltas.items():
            if trait in current_traits:
                # Limit maximum single change
                bounded_delta = max(-self.MAX_SINGLE_DRIFT, min(self.MAX_SINGLE_DRIFT, delta))
                
                # Ensure final value stays in bounds
                current_value = current_traits[trait]
                new_value = current_value + bounded_delta
                
                if new_value < self.TRAIT_MIN:
                    bounded_delta = self.TRAIT_MIN - current_value
                elif new_value > self.TRAIT_MAX:
                    bounded_delta = self.TRAIT_MAX - current_value
                
                if abs(bounded_delta) > 0.001:
                    bounded_deltas[trait] = bounded_delta
        
        return bounded_deltas
    
    def _apply_trait_updates(self, persona_id: str, current_traits: Dict[str, float], 
                           deltas: Dict[str, float]) -> Dict[str, float]:
        """Apply trait updates to database and return new traits"""
        updated_traits = dict(current_traits)
        
        # Apply deltas
        for trait, delta in deltas.items():
            if trait in updated_traits:
                updated_traits[trait] += delta
                updated_traits[trait] = max(self.TRAIT_MIN, min(self.TRAIT_MAX, updated_traits[trait]))
        
        # Update database
        try:
            self.db.execute("""
                UPDATE agent_personality_profiles
                SET base_traits = %s, last_updated = CURRENT_TIMESTAMP
                WHERE persona_id = %s
            """, (json.dumps(updated_traits), persona_id))
            
            print(f"[+] Updated traits for {persona_id}")
            
        except Exception as e:
            print(f"[-] Failed to update traits: {e}")
        
        return updated_traits
    
    def _log_trait_changes(self, persona_id: str, session_id: str, 
                          traits_before: Dict[str, float], traits_after: Dict[str, float],
                          influences: Dict[str, Any]):
        """Log trait changes to history table"""
        try:
            for trait in traits_before:
                if trait in traits_after:
                    value_before = traits_before[trait]
                    value_after = traits_after[trait]
                    delta = value_after - value_before
                    
                    if abs(delta) > 0.001:  # Only log meaningful changes
                        # Determine primary source of change
                        source_event = "combined"
                        max_influence = 0
                        
                        for source, influence_dict in influences.items():
                            if trait in influence_dict:
                                if abs(influence_dict[trait]) > max_influence:
                                    max_influence = abs(influence_dict[trait])
                                    source_event = source
                        
                        self.db.execute("""
                            INSERT INTO agent_trait_history 
                            (persona_id, session_id, trait, value_before, value_after, delta, source_event, timestamp)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                        """, (persona_id, session_id, trait, value_before, value_after, delta, source_event))
            
            print(f"[+] Logged trait changes to history")
            
        except Exception as e:
            print(f"[-] Failed to log trait changes: {e}")
    
    def decay_unused_modifiers(self, persona_id: str, days_threshold: int = 7) -> None:
        """Apply decay to learned modifiers that haven't been reinforced"""
        try:
            # Get current learned modifiers
            profile = self.db.query("""
                SELECT learned_modifiers FROM agent_personality_profiles
                WHERE persona_id = %s
            """, (persona_id,))
            
            if not profile or not profile[0]['learned_modifiers']:
                return
            
            learned_modifiers = profile[0]['learned_modifiers']
            updated_modifiers = {}
            
            # Check recent reinforcement for each modifier
            cutoff_date = datetime.now() - timedelta(days=days_threshold)
            
            for modifier, weight in learned_modifiers.items():
                # Check if this modifier was reinforced recently
                recent_reinforcement = self.db.query("""
                    SELECT COUNT(*) as count FROM personality_learning_log
                    WHERE persona_id = %s AND user_feedback_text ILIKE %s 
                    AND timestamp > %s
                """, (persona_id, f"%{modifier.replace('_', ' ')}%", cutoff_date))
                
                reinforcement_count = recent_reinforcement[0]['count'] if recent_reinforcement else 0
                
                if reinforcement_count > 0:
                    # Reinforced - keep current weight
                    updated_modifiers[modifier] = weight
                else:
                    # Not reinforced - apply decay
                    decayed_weight = weight * (1 - self.DECAY_RATE)
                    if decayed_weight > 0.1:  # Keep if still significant
                        updated_modifiers[modifier] = decayed_weight
                    # else: modifier fades away
            
            # Update database
            self.db.execute("""
                UPDATE agent_personality_profiles
                SET learned_modifiers = %s, last_updated = CURRENT_TIMESTAMP
                WHERE persona_id = %s
            """, (json.dumps(updated_modifiers), persona_id))
            
            print(f"[+] Applied decay to unused modifiers for {persona_id}")
            
        except Exception as e:
            print(f"[-] Modifier decay failed: {e}")
    
    def export_evolving_traits(self, persona_id: str) -> Dict[str, Any]:
        """Export current evolving trait state for prompt injection"""
        try:
            current_traits = self._get_current_traits(persona_id)
            
            # Get recent trait changes for context
            recent_changes = self.db.query("""
                SELECT trait, delta, source_event, timestamp
                FROM agent_trait_history
                WHERE persona_id = %s AND timestamp > NOW() - INTERVAL '7 days'
                ORDER BY timestamp DESC
                LIMIT 10
            """, (persona_id,))
            
            # Calculate trait change velocity (how fast traits are changing)
            trait_velocity = {}
            for change in recent_changes:
                trait = change['trait']
                trait_velocity[trait] = trait_velocity.get(trait, 0) + abs(change['delta'])
            
            return {
                'current_traits': current_traits,
                'recent_changes': recent_changes,
                'trait_velocity': trait_velocity,
                'personality_stability': 1.0 - (sum(trait_velocity.values()) / len(current_traits) if current_traits else 1.0),
                'export_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[-] Failed to export evolving traits: {e}")
            return {'error': str(e)}
