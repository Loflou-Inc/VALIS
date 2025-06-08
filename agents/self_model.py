"""
VALIS Synthetic Cognition Layer - AgentSelfModel
Persistent ego state and behavioral alignment tracking
"""
import json
import re
from typing import Dict, Optional, Any
from datetime import datetime
import uuid

from core.logging_config import get_valis_logger, log_alignment_check
from core.exceptions import (
    AlignmentCalculationError,
    PersonaError,
    PersonaNotFoundError,
    DatabaseError
)

class AgentSelfModel:
    """Manages agent self-awareness, ego state, and behavioral alignment"""
    
    def __init__(self, db_client):
        """Initialize with database client"""
        self.db = db_client
        self.logger = get_valis_logger()
        
    def evaluate_alignment(self, transcript: str, traits: dict, persona_id: str) -> float:
        """Evaluate how well agent behavior aligns with expected traits"""
        if not transcript:
            raise AlignmentCalculationError("Transcript is required for alignment evaluation")
        
        if not traits:
            raise AlignmentCalculationError("Traits dictionary is required for alignment evaluation")
            
        if not persona_id:
            raise AlignmentCalculationError("Persona ID is required for alignment evaluation")
        
        try:
            score_factors = []
            transcript_lower = transcript.lower()
            
            # Enhanced alignment scoring with regex word boundaries
            for trait_name, trait_value in traits.items():
                if isinstance(trait_value, str):
                    trait_keywords = trait_value.lower().split()
                    trait_score = 0.0
                    
                    for keyword in trait_keywords:
                        matches = self._calculate_keyword_matches(keyword, transcript_lower)
                        
                        if matches > 0:
                            keyword_score = min(matches * 0.4 + 0.4, 1.0)
                            trait_score += keyword_score
                    # Normalize trait score by number of keywords
                    if trait_keywords:
                        normalized_score = trait_score / len(trait_keywords)
                        if normalized_score > 0.05:
                            normalized_score = min(normalized_score * 1.3, 1.0)
                        score_factors.append(normalized_score)
                
                elif isinstance(trait_value, (int, float)):
                    # Handle numeric trait values
                    if 'confident' in transcript_lower and trait_name == 'confidence':
                        score_factors.append(min(trait_value + 0.2, 1.0))
                    elif 'uncertain' in transcript_lower and trait_name == 'confidence':
                        score_factors.append(max(trait_value - 0.3, 0.0))
            
            # Calculate weighted average
            if score_factors:
                base_score = sum(score_factors) / len(score_factors)
                # Bonus for consistent high scores
                if len([s for s in score_factors if s > 0.7]) > len(score_factors) * 0.6:
                    alignment_score = min(base_score + 0.1, 1.0)
                else:
                    alignment_score = base_score
            else:
                alignment_score = 0.5  # Neutral if no traits to evaluate
                
            # Log the evaluation
            log_alignment_check(self.logger, persona_id, alignment_score, len(transcript))
            
            return alignment_score
            
        except (TypeError, KeyError, ValueError) as e:
            self.logger.error(
                "Invalid input data for alignment calculation",
                extra={
                    'persona_id': persona_id,
                    'error': str(e),
                    'transcript_length': len(transcript),
                    'traits_count': len(traits)
                }
            )
            raise AlignmentCalculationError(f"Invalid alignment calculation data: {e}")
        except Exception as e:
            self.logger.critical(
                "Unexpected error in alignment calculation",
                extra={'persona_id': persona_id, 'error': str(e)}
            )
            raise
    def _calculate_keyword_matches(self, keyword: str, transcript_lower: str) -> int:
        """Calculate keyword matches using multiple methods"""
        # Method 1: Exact word boundary match
        exact_pattern = r'\b' + re.escape(keyword) + r'\b'
        exact_matches = len(re.findall(exact_pattern, transcript_lower))
        
        # Method 2: Partial prefix match
        partial_pattern = r'\b' + re.escape(keyword)
        partial_matches = len(re.findall(partial_pattern, transcript_lower))
        
        # Method 3: Root word matching for longer words
        root_matches = 0
        if len(keyword) > 4:
            roots_to_try = [
                keyword[:-3] if keyword.endswith('ing') else None,
                keyword[:-3] if keyword.endswith('ive') else None,
                keyword[:-3] if keyword.endswith('ful') else None,
                keyword[:-2] if keyword.endswith('ed') else None,
            ]
            
            for root in roots_to_try:
                if root and len(root) >= 3:
                    root_pattern = r'\b' + re.escape(root) + r'\b'
                    root_matches += len(re.findall(root_pattern, transcript_lower))
        
        return max(exact_matches, partial_matches, root_matches)
    
    def update_profile(self, persona_id: str, alignment_score: float, notes: str = "") -> None:
        """Update agent self profile with new alignment score and state"""
        if not persona_id:
            raise PersonaError("Persona ID is required for profile update")
            
        if not 0.0 <= alignment_score <= 1.0:
            raise AlignmentCalculationError(f"Alignment score must be between 0.0 and 1.0, got {alignment_score}")
        
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
                self.logger.info(f"Updated self profile for {persona_id}: score={alignment_score:.3f}")
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
                self.logger.info(f"Created new self profile for {persona_id}")
                
        except PersonaError:
            raise  # Re-raise our custom exceptions
        except Exception as e:
            self.logger.error(
                "Database error during profile update",
                extra={'persona_id': persona_id, 'error': str(e)}
            )
            raise DatabaseError(f"Failed to update profile for {persona_id}: {e}")
    def export_state_blob(self, persona_id: str) -> dict:
        """Export current self state for prompt injection"""
        if not persona_id:
            raise PersonaError("Persona ID is required for state export")
        
        try:
            # Get current self profile
            profile = self.db.query("""
                SELECT * FROM agent_self_profiles WHERE persona_id = %s
            """, (persona_id,))
            
            if not profile:
                self.logger.warning(f"No self profile found for {persona_id}, returning defaults")
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
                confidence_value = alignment if alignment else 0.5
            
            state_blob = {
                "confidence": confidence_value,
                "alignment_score": alignment,
                "working_state": working_state,
                "self_awareness": self._generate_self_awareness_text(alignment, traits)
            }
            
            self.logger.debug(f"Exported state blob for {persona_id}")
            return state_blob
            
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error(
                "Invalid profile data in database",
                extra={'persona_id': persona_id, 'error': str(e)}
            )
            raise PersonaError(f"Corrupted profile data for {persona_id}: {e}")
        except PersonaError:
            raise  # Re-raise our custom exceptions
        except Exception as e:
            self.logger.error(
                "Database error during state export",
                extra={'persona_id': persona_id, 'error': str(e)}
            )
            raise DatabaseError(f"Failed to export state for {persona_id}: {e}")
    
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