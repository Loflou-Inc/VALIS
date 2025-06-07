"""
VALIS Synthetic Cognition Layer - AgentSelfModel
Persistent ego state and behavioral alignment tracking
"""
import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class AgentSelfModel:
    """Manages agent self-awareness, ego state, and behavioral alignment"""
    
    def __init__(self, db_client):
        """Initialize with database client"""
        self.db = db_client
        
    def evaluate_alignment(self, transcript: str, traits: dict, persona_id: str) -> float:
        """
        Evaluate how well agent behavior aligns with expected traits
        
        Args:
            transcript: Recent conversation or action transcript
            traits: Expected personality traits and behaviors
            persona_id: UUID of the persona being evaluated
            
        Returns:
            float: Alignment score between 0.0 and 1.0
        """
        try:
            import re
            
            if not transcript or not traits:
                return 0.5  # Default neutral score
                
            score_factors = []
            transcript_lower = transcript.lower()
            
            # Enhanced alignment scoring with regex word boundaries
            for trait_name, trait_value in traits.items():
                if isinstance(trait_value, str):
                    trait_keywords = trait_value.lower().split()
                    trait_score = 0.0
                    
                    for keyword in trait_keywords:
                        matches = 0
                        
                        # Method 1: Exact word boundary match
                        exact_pattern = r'\b' + re.escape(keyword) + r'\b'
                        exact_matches = len(re.findall(exact_pattern, transcript_lower))
                        
                        # Method 2: Partial prefix match (allows for word variations)
                        partial_pattern = r'\b' + re.escape(keyword)
                        partial_matches = len(re.findall(partial_pattern, transcript_lower))
                        
                        # Method 3: Root word matching (handle "understand" -> "understanding")
                        root_matches = 0
                        if len(keyword) > 4:  # Only for longer words
                            # Try removing common suffixes
                            roots_to_try = [
                                keyword[:-3] if keyword.endswith('ing') else None,  # understanding -> understand
                                keyword[:-3] if keyword.endswith('ive') else None,  # supportive -> support
                                keyword[:-3] if keyword.endswith('ful') else None,  # helpful -> help
                                keyword[:-2] if keyword.endswith('ed') else None,   # helped -> help
                            ]
                            
                            for root in roots_to_try:
                                if root and len(root) >= 3:
                                    root_pattern = r'\b' + re.escape(root) + r'\b'
                                    root_matches += len(re.findall(root_pattern, transcript_lower))
                        
                        # Use the highest match count from all methods
                        matches = max(exact_matches, partial_matches, root_matches)
                        
                        if matches > 0:
                            # Score based on frequency - more generous scoring
                            keyword_score = min(matches * 0.4 + 0.4, 1.0)  # Base score of 0.4 + bonus for matches
                            trait_score += keyword_score
                    
                    # Normalize trait score by number of keywords - be more generous
                    if trait_keywords:
                        normalized_score = trait_score / len(trait_keywords)
                        # Boost scores that show any alignment
                        if normalized_score > 0.05:
                            normalized_score = min(normalized_score * 1.3, 1.0)
                        score_factors.append(normalized_score)
                
                elif isinstance(trait_value, (int, float)):
                    # Handle numeric trait values (confidence, assertiveness levels)
                    if 'confident' in transcript_lower and trait_name == 'confidence':
                        score_factors.append(min(trait_value + 0.2, 1.0))
                    elif 'uncertain' in transcript_lower and trait_name == 'confidence':
                        score_factors.append(max(trait_value - 0.3, 0.0))
            
            # Calculate weighted average with bias towards consistent behavior
            if score_factors:
                base_score = sum(score_factors) / len(score_factors)
                
                # Bonus for consistent high scores across traits
                if len([s for s in score_factors if s > 0.7]) > len(score_factors) * 0.6:
                    alignment_score = min(base_score + 0.1, 1.0)
                else:
                    alignment_score = base_score
            else:
                alignment_score = 0.5  # Neutral if no traits to evaluate
                
            # Log the evaluation
            logger.info(f"Alignment evaluation for {persona_id}: {alignment_score:.3f} (factors: {len(score_factors)})")
            
            return alignment_score
            
        except Exception as e:
            logger.error(f"Error evaluating alignment for {persona_id}: {e}")
            return 0.5  # Default to neutral on error
    
    def update_profile(self, persona_id: str, alignment_score: float, notes: str = "") -> None:
        """
        Update agent self profile with new alignment score and state
        
        Args:
            persona_id: UUID of the persona
            alignment_score: Latest alignment evaluation score
            notes: Optional notes about the evaluation
        """
        try:
            # Check if profile exists
            existing = self.db.query("""
                SELECT * FROM agent_self_profiles WHERE persona_id = %s
            """, (persona_id,))
            
            if existing:
                # Update existing profile
                self.db.execute("""
                    UPDATE agent_self_profiles 
                    SET last_alignment_score = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE persona_id = %s
                """, (alignment_score, persona_id))
                logger.info(f"Updated self profile for {persona_id}: score={alignment_score:.3f}")
            else:
                # Create new profile with default traits
                default_traits = {
                    "confidence": 0.5,
                    "assertiveness": 0.5,
                    "warmth": 0.5,
                    "analytical": 0.5
                }
                
                self.db.execute("""
                    INSERT INTO agent_self_profiles (persona_id, traits, last_alignment_score)
                    VALUES (%s, %s, %s)
                """, (persona_id, json.dumps(default_traits), alignment_score))
                logger.info(f"Created new self profile for {persona_id}: score={alignment_score:.3f}")
                
        except Exception as e:
            logger.error(f"Error updating self profile for {persona_id}: {e}")
    
    def export_state_blob(self, persona_id: str) -> dict:
        """
        Export current self state for prompt injection
        
        Args:
            persona_id: UUID of the persona
            
        Returns:
            dict: State blob containing self-awareness data for prompts
        """
        try:
            # Get current self profile
            profile = self.db.query("""
                SELECT * FROM agent_self_profiles WHERE persona_id = %s
            """, (persona_id,))
            
            if not profile:
                # Return default state if no profile exists
                return {
                    "confidence": 0.5,
                    "alignment_score": 0.5,
                    "self_awareness": "I am learning about my own behavior patterns."
                }
            
            profile_data = profile[0]
            traits = json.loads(profile_data['traits']) if profile_data['traits'] else {}
            alignment = profile_data['last_alignment_score']
            working_state = json.loads(profile_data['working_self_state']) if profile_data['working_self_state'] else {}
            
            # Build state blob for prompt injection
            confidence_value = 0.5  # Default
            if isinstance(traits.get("confidence"), (int, float)):
                confidence_value = traits["confidence"]
            elif "confidence" in traits and isinstance(traits["confidence"], str):
                # Extract confidence from text traits - use alignment score as proxy
                confidence_value = alignment if alignment else 0.5
            
            state_blob = {
                "confidence": confidence_value,
                "alignment_score": alignment,
                "working_state": working_state,
                "self_awareness": self._generate_self_awareness_text(alignment, traits)
            }
            
            logger.debug(f"Exported state blob for {persona_id}: {state_blob}")
            return state_blob
            
        except Exception as e:
            logger.error(f"Error exporting state blob for {persona_id}: {e}")
            return {"confidence": 0.5, "alignment_score": 0.5, "self_awareness": "Processing self-awareness..."}
    
    def _generate_self_awareness_text(self, alignment: float, traits: dict) -> str:
        """Generate natural language self-awareness statement"""
        if alignment > 0.8:
            return "I feel confident and aligned with my core personality."
        elif alignment > 0.6:
            return "I'm generally acting in line with my nature, with some room for improvement."
        elif alignment > 0.4:
            return "I'm somewhat uncertain about how well I'm expressing my personality."
        else:
            return "I'm having difficulty maintaining consistency with my intended personality."
