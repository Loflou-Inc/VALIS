"""
VALIS Sprint 12/13: Personality Expression Engine with Trait Evolution
Core module for dynamic personality expression and trait drift over time
"""
import json
import re
import random
from typing import Dict, List, Any, Optional, Tuple
from memory.db import db
from agents.trait_drift import TraitDriftEngine


class PersonalityEngine:
    """
    Core personality expression engine that modulates agent responses 
    based on persona traits, emotional state, and learned user preferences
    """
    
    def __init__(self, database_client=None):
        self.db = database_client or db
        self._tone_cache = {}
        self._load_tone_templates()
        
        # Initialize trait drift engine for personality evolution
        self.trait_drift_engine = TraitDriftEngine(self.db)
    
    def _load_tone_templates(self):
        """Load personality tone templates from database"""
        try:
            templates = self.db.query("SELECT * FROM personality_tone_templates")
            for template in templates:
                self._tone_cache[template['tone_id']] = {
                    'name': template['tone_name'],
                    'config': template['base_config'],
                    'trait_weights': template['trait_weights'],
                    'context': template['usage_context']
                }
            print(f"[+] Loaded {len(self._tone_cache)} personality tones")
        except Exception as e:
            print(f"[-] Failed to load tone templates: {e}")
            self._tone_cache = {}
    
    def inject_personality(self, prompt_block: str, persona: Dict[str, Any], 
                          mood_state: Dict[str, Any], self_state: Dict[str, Any]) -> str:
        """
        Primary method: Inject personality expression into a prompt block
        
        Args:
            prompt_block: The base prompt/response to modify
            persona: Persona profile with traits
            mood_state: Current emotional state from AgentEmotionModel
            self_state: Ego state from AgentSelfModel
            
        Returns:
            Modified prompt with personality injection
        """
        try:
            # Extract traits and state info
            base_traits = self._extract_traits(persona)
            current_mood = mood_state.get('mood', 'neutral')
            confidence = self_state.get('confidence', 0.5)
            alignment_score = self_state.get('alignment_score', 0.5)
            
            # Select appropriate tone based on traits, mood, and confidence
            selected_tone = self._select_tone(base_traits, current_mood, confidence)
            
            # Apply personality modulation
            modified_prompt = self._apply_tone_modulation(
                prompt_block, selected_tone, base_traits, mood_state, confidence
            )
            
            return modified_prompt
            
        except Exception as e:
            print(f"[-] Personality injection failed: {e}")
            return prompt_block  # Fallback to original
    
    def _extract_traits(self, persona: Dict[str, Any]) -> Dict[str, float]:
        """Extract and normalize personality traits from persona (now with evolution support)"""
        traits = {}
        
        # First check if we have evolving traits from trait drift
        persona_id = persona.get('id')
        if persona_id:
            try:
                evolving_profile = self.db.query("""
                    SELECT base_traits, evolving_traits FROM agent_personality_profiles
                    WHERE persona_id = %s
                """, (persona_id,))
                
                if evolving_profile:
                    base_traits = evolving_profile[0]['base_traits'] or {}
                    evolving_traits = evolving_profile[0]['evolving_traits'] or {}
                    
                    # Use evolving traits if available, fall back to base traits
                    if evolving_traits:
                        traits = dict(evolving_traits)
                        print(f"[+] Using evolving traits for {persona_id}")
                    else:
                        traits = dict(base_traits)
                        print(f"[+] Using base traits for {persona_id}")
                    
                    # Ensure we have all Big Five traits
                    defaults = {
                        'extraversion': 0.5,
                        'agreeableness': 0.5, 
                        'conscientiousness': 0.5,
                        'emotional_stability': 0.5,
                        'openness': 0.5
                    }
                    
                    for trait, default_val in defaults.items():
                        if trait not in traits:
                            traits[trait] = default_val
                    
                    return traits
                    
            except Exception as e:
                print(f"[-] Failed to get evolving traits: {e}")
        
        # Fallback to original trait extraction logic
        persona_traits = persona.get('traits', {})
        if isinstance(persona_traits, str):
            try:
                persona_traits = json.loads(persona_traits)
            except json.JSONDecodeError:
                persona_traits = {}
        
        # Map common trait patterns to Big Five + additional
        trait_mapping = {
            'confidence': 'extraversion',
            'confident': 'extraversion', 
            'analytical': 'openness',
            'logical': 'conscientiousness',
            'systematic': 'conscientiousness',
            'empathetic': 'agreeableness',
            'caring': 'agreeableness',
            'creative': 'openness',
            'organized': 'conscientiousness',
            'calm': 'emotional_stability'
        }
        
        # Process persona traits
        for trait_key, trait_desc in persona_traits.items():
            if isinstance(trait_desc, str):
                # Parse descriptive traits like "confident assured"
                words = trait_desc.lower().split()
                for word in words:
                    if word in trait_mapping:
                        canonical_trait = trait_mapping[word]
                        traits[canonical_trait] = traits.get(canonical_trait, 0.0) + 0.3
            else:
                # Direct numeric traits
                traits[trait_key] = float(trait_desc)
        
        # Normalize values to 0-1 range
        for trait in traits:
            traits[trait] = min(1.0, max(0.0, traits[trait]))
        
        # Set defaults for missing Big Five traits
        defaults = {
            'extraversion': 0.5,
            'agreeableness': 0.5, 
            'conscientiousness': 0.5,
            'emotional_stability': 0.5,
            'openness': 0.5
        }
        
        for trait, default_val in defaults.items():
            if trait not in traits:
                traits[trait] = default_val
        
        return traits
    
    def _select_tone(self, traits: Dict[str, float], mood: str, confidence: float) -> str:
        """Select the most appropriate tone based on current state"""
        if not self._tone_cache:
            return 'confident'  # Default fallback
        
        best_tone = 'confident'
        best_score = 0.0
        
        # Calculate compatibility score for each tone
        for tone_id, tone_data in self._tone_cache.items():
            score = 0.0
            trait_weights = tone_data['trait_weights']
            
            # Score based on trait alignment
            for trait, weight in trait_weights.items():
                if trait in traits:
                    score += traits[trait] * weight
            
            # Mood modifiers
            mood_modifiers = {
                'happy': {'playful': 0.3, 'confident': 0.2},
                'excited': {'playful': 0.4, 'curious': 0.3},
                'focused': {'analytical': 0.4, 'confident': 0.2},
                'calm': {'empathetic': 0.3, 'analytical': 0.2},
                'anxious': {'empathetic': 0.3},
                'frustrated': {'analytical': 0.2},
                'neutral': {}  # No mood bias
            }
            
            if mood in mood_modifiers and tone_id in mood_modifiers[mood]:
                score += mood_modifiers[mood][tone_id]
            
            # Confidence modifiers
            if confidence > 0.7:
                if tone_id == 'confident':
                    score += 0.2
            elif confidence < 0.3:
                if tone_id == 'empathetic':
                    score += 0.2
            
            if score > best_score:
                best_score = score
                best_tone = tone_id
        
        return best_tone
    
    def _apply_tone_modulation(self, prompt: str, tone_id: str, traits: Dict[str, float], 
                             mood_state: Dict[str, Any], confidence: float) -> str:
        """Apply the selected tone's modulation to the prompt"""
        if tone_id not in self._tone_cache:
            return prompt
        
        tone_config = self._tone_cache[tone_id]['config']
        
        # Parse tone configuration
        prefix = tone_config.get('prefix', '')
        suffix = tone_config.get('suffix', '')
        modifiers = tone_config.get('modifiers', [])
        
        # Apply modifiers to the content
        modified_content = self._apply_modifiers(prompt, modifiers, traits, confidence)
        
        # Construct final response
        final_response = ""
        
        if prefix and not self._already_has_greeting(modified_content):
            final_response = f"{prefix} {modified_content}"
        else:
            final_response = modified_content
        
        if suffix and not self._already_has_question(final_response):
            final_response = f"{final_response} {suffix}"
        
        return final_response.strip()
    
    def _apply_modifiers(self, content: str, modifiers: List[str], 
                        traits: Dict[str, float], confidence: float) -> str:
        """Apply specific modifiers to content based on trait weights"""
        modified = content
        
        for modifier in modifiers:
            if modifier == "use exclamation" and traits.get('extraversion', 0.5) > 0.6:
                # Add excitement for extraverted personalities
                modified = re.sub(r'\.(\s+|$)', r'!\1', modified, count=1)
                
            elif modifier == "avoid hedging" and confidence > 0.7:
                # Remove uncertainty language for confident personas
                hedging_words = ['maybe', 'perhaps', 'possibly', 'might', 'could be']
                for hedge in hedging_words:
                    modified = re.sub(rf'\b{hedge}\b', '', modified, flags=re.IGNORECASE)
                    
            elif modifier == "hedge statements" and confidence < 0.4:
                # Add uncertainty for low-confidence states
                modified = re.sub(r'\b(is|are)\b', r'seems to be', modified, count=1)
                
            elif modifier == "use logical structure" and traits.get('conscientiousness', 0.5) > 0.6:
                # Add structure words for organized personalities
                if not re.search(r'\b(first|second|then|next|finally)\b', modified, re.IGNORECASE):
                    modified = f"Let me break this down: {modified}"
                    
            elif modifier == "acknowledge emotions" and traits.get('agreeableness', 0.5) > 0.7:
                # Add empathetic language
                if not re.search(r'\b(understand|feel|emotions?)\b', modified, re.IGNORECASE):
                    modified = f"I can understand this situation. {modified}"
                    
            elif modifier == "ask questions" and traits.get('openness', 0.5) > 0.7:
                # Add curiosity for open personalities
                if not modified.endswith('?'):
                    modified = f"{modified} What are your thoughts on this?"
        
        return modified.strip()
    
    def _already_has_greeting(self, content: str) -> bool:
        """Check if content already has a greeting/opener"""
        greetings = ['hello', 'hi', 'hey', 'absolutely', 'great', 'excellent', 'interesting']
        first_words = content.lower().split()[:3]
        return any(greeting in ' '.join(first_words) for greeting in greetings)
    
    def _already_has_question(self, content: str) -> bool:
        """Check if content already ends with a question"""
        return content.strip().endswith('?')
    
    def learn_preference(self, user_input: str, user_feedback: str, 
                        session_id: str, persona_id: str) -> Dict[str, Any]:
        """
        Learn from user feedback to adjust personality expression
        
        Args:
            user_input: Original user message
            user_feedback: User's response/correction
            session_id: Current session ID
            persona_id: Persona UUID
            
        Returns:
            Dictionary with learning insights
        """
        try:
            # Classify feedback type
            feedback_type = self._classify_feedback(user_feedback)
            
            # Extract preference signals
            preferences = self._extract_preferences(user_input, user_feedback)
            
            # Log the learning interaction
            self._log_learning_interaction(
                session_id, persona_id, user_input, user_feedback, 
                feedback_type, preferences
            )
            
            # Update learned modifiers if significant pattern detected
            if preferences:
                self._update_learned_modifiers(persona_id, preferences)
            
            return {
                'feedback_type': feedback_type,
                'preferences_detected': preferences,
                'learning_weight': self._calculate_learning_weight(feedback_type)
            }
            
        except Exception as e:
            print(f"[-] Learning preference failed: {e}")
            return {'error': str(e)}
    
    def _classify_feedback(self, feedback: str) -> str:
        """Classify user feedback as positive, negative, neutral, or correction"""
        feedback_lower = feedback.lower()
        
        positive_indicators = ['good', 'great', 'perfect', 'excellent', 'love', 'like', 'thanks']
        negative_indicators = ['bad', 'wrong', 'terrible', 'hate', 'dislike', 'stop']
        correction_indicators = ['actually', 'no', 'instead', 'rather', 'should', 'better']
        
        if any(word in feedback_lower for word in positive_indicators):
            return 'positive'
        elif any(word in feedback_lower for word in negative_indicators):
            return 'negative'
        elif any(word in feedback_lower for word in correction_indicators):
            return 'correction'
        else:
            return 'neutral'
    
    def _extract_preferences(self, user_input: str, feedback: str) -> Dict[str, float]:
        """Extract personality preferences from user feedback"""
        preferences = {}
        
        feedback_lower = feedback.lower()
        
        # Detect style preferences
        if 'short' in feedback_lower or 'brief' in feedback_lower or 'concise' in feedback_lower:
            preferences['prefers_brevity'] = 0.8
            
        elif 'long' in feedback_lower or 'detail' in feedback_lower or 'explain' in feedback_lower:
            preferences['prefers_detail'] = 0.8
            
        if 'formal' in feedback_lower or 'professional' in feedback_lower:
            preferences['prefers_formality'] = 0.8
            
        elif 'casual' in feedback_lower or 'friendly' in feedback_lower:
            preferences['prefers_casual'] = 0.8
            
        if 'quiet' in feedback_lower or 'calm' in feedback_lower:
            preferences['prefers_subdued'] = 0.7
            
        elif 'enthusiastic' in feedback_lower or 'excited' in feedback_lower:
            preferences['prefers_energetic'] = 0.8
        
        return preferences
    
    def _log_learning_interaction(self, session_id: str, persona_id: str, 
                                 user_input: str, user_feedback: str,
                                 feedback_type: str, preferences: Dict[str, float]):
        """Log learning interaction to database"""
        try:
            self.db.execute("""
                INSERT INTO personality_learning_log 
                (session_id, persona_id, user_input, personality_response, 
                 user_feedback_type, user_feedback_text, learning_weight, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                session_id, persona_id, user_input, 
                json.dumps(preferences), feedback_type, user_feedback,
                self._calculate_learning_weight(feedback_type)
            ))
        except Exception as e:
            print(f"[-] Failed to log learning interaction: {e}")
    
    def _update_learned_modifiers(self, persona_id: str, preferences: Dict[str, float]):
        """Update learned personality modifiers for a persona"""
        try:
            # Get current learned modifiers
            current = self.db.query("""
                SELECT learned_modifiers FROM agent_personality_profiles 
                WHERE persona_id = %s
            """, (persona_id,))
            
            if current:
                learned_mods = current[0]['learned_modifiers'] or {}
            else:
                # Create new personality profile
                self.db.execute("""
                    INSERT INTO agent_personality_profiles (persona_id, base_traits, learned_modifiers)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (persona_id) DO NOTHING
                """, (persona_id, json.dumps({}), json.dumps({})))
                learned_mods = {}
            
            # Update with new preferences (weighted averaging)
            for pref, weight in preferences.items():
                if pref in learned_mods:
                    # Average with existing preference
                    learned_mods[pref] = (learned_mods[pref] + weight) / 2
                else:
                    learned_mods[pref] = weight
            
            # Update database
            self.db.execute("""
                UPDATE agent_personality_profiles 
                SET learned_modifiers = %s, last_updated = CURRENT_TIMESTAMP
                WHERE persona_id = %s
            """, (json.dumps(learned_mods), persona_id))
            
        except Exception as e:
            print(f"[-] Failed to update learned modifiers: {e}")
    
    def _calculate_learning_weight(self, feedback_type: str) -> float:
        """Calculate learning weight based on feedback type"""
        weights = {
            'positive': 0.6,
            'negative': 0.8,
            'correction': 1.0,
            'neutral': 0.2
        }
        return weights.get(feedback_type, 0.5)
    
    def get_personality_state(self, persona_id: str, session_id: str) -> Dict[str, Any]:
        """Get current personality state for a session"""
        try:
            # Get base traits
            profile = self.db.query("""
                SELECT base_traits, learned_modifiers FROM agent_personality_profiles
                WHERE persona_id = %s
            """, (persona_id,))
            
            # Get session state
            session_state = self.db.query("""
                SELECT * FROM personality_session_state WHERE session_id = %s
            """, (session_id,))
            
            return {
                'base_traits': profile[0]['base_traits'] if profile else {},
                'learned_modifiers': profile[0]['learned_modifiers'] if profile else {},
                'session_state': session_state[0] if session_state else None,
                'available_tones': list(self._tone_cache.keys())
            }
            
        except Exception as e:
            print(f"[-] Failed to get personality state: {e}")
            return {'error': str(e)}
    def evolve_personality_from_session(self, session_id: str, persona_id: str, 
                                       transcript: str, feedback_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Trigger personality evolution based on session interaction
        Called after session completion with reflection data
        
        Args:
            session_id: Session identifier
            persona_id: Persona UUID
            transcript: Full session transcript
            feedback_list: User feedback events
            
        Returns:
            Evolution analysis results
        """
        try:
            print(f"[+] Triggering personality evolution for {persona_id} session {session_id}")
            
            # Use TraitDriftEngine to analyze and update traits
            evolution_result = self.trait_drift_engine.update_traits_from_dialogue(
                session_id, persona_id, transcript, feedback_list
            )
            
            # Apply decay to unused modifiers periodically
            if random.random() < 0.3:  # 30% chance to run decay
                self.trait_drift_engine.decay_unused_modifiers(persona_id)
            
            return evolution_result
            
        except Exception as e:
            print(f"[-] Personality evolution failed: {e}")
            return {"error": str(e)}
    
    def get_evolving_personality_state(self, persona_id: str) -> Dict[str, Any]:
        """Get current evolving personality state for analytics/debugging"""
        try:
            return self.trait_drift_engine.export_evolving_traits(persona_id)
        except Exception as e:
            print(f"[-] Failed to get evolving personality state: {e}")
            return {"error": str(e)}
