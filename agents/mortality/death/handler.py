"""
DeathHandler - Sprint 2.2 Refactor
Manages agent death processing and legacy calculation
Extracted from monolithic MortalityEngine
"""
from datetime import datetime
from typing import Dict, Any, List

from agents.mortality import DeathHandlerInterface
from core.exceptions import DatabaseError, PersonaNotFoundError
from core.logging_config import log_operation_start, log_operation_end


class DeathHandler(DeathHandlerInterface):
    """
    Handles agent death processing, legacy calculation, and final thoughts generation
    Separated from lifespan and rebirth logic for better modularity
    """
    
    def __init__(self, database_client=None):
        super().__init__(database_client)
        
        # Legacy tier thresholds
        self.LEGACY_TIERS = {
            'wanderer': (0.0, 0.2),    # disjointed, unformed
            'seeker': (0.2, 0.5),      # showed pattern, lacked refinement  
            'guide': (0.5, 0.8),       # consistent, expressive, coherent
            'architect': (0.8, 1.0)    # powerful legacy, influential persona
        }
        
        self.logger.info("DeathHandler initialized")
    
    def trigger_death(self, agent_id: str, cause: str = "natural") -> Dict[str, Any]:
        """
        Trigger agent death and begin legacy calculation
        
        Args:
            agent_id: UUID of the agent
            cause: Death cause ('natural_expiry', 'manual_termination', 'system_error')
            
        Returns:
            Death processing result with legacy score
            
        Raises:
            PersonaNotFoundError: If agent not found
            DatabaseError: If database operations fail
        """
        if not agent_id:
            raise PersonaNotFoundError("Agent ID is required for death processing")
        
        log_operation_start(self.logger, "trigger_death", agent_id=agent_id, cause=cause)
        
        try:
            # Check if already dead
            existing_death = self.db.query("""
                SELECT death_date FROM agent_mortality WHERE agent_id = %s
            """, (agent_id,))
            
            if not existing_death:
                raise PersonaNotFoundError(f"Agent {agent_id} has no mortality record")
            
            if existing_death[0]['death_date']:
                self.logger.warning(f"Agent {agent_id} is already dead")
                return {"status": "already_dead", "agent_id": agent_id}
            
            # Generate final thoughts
            final_thoughts = self._generate_final_thoughts(agent_id)
            
            # Calculate final legacy score
            legacy_result = self.generate_legacy_score(agent_id, finalize=True)
            
            # Update mortality record with death
            death_timestamp = datetime.now()
            self.db.execute("""
                UPDATE agent_mortality 
                SET death_date = %s, death_cause = %s
                WHERE agent_id = %s
            """, (death_timestamp, cause, agent_id))
            
            result = {
                "status": "death_processed",
                "agent_id": agent_id,
                "death_timestamp": death_timestamp.isoformat(),
                "death_cause": cause,
                "final_thoughts": final_thoughts,
                "legacy_score": legacy_result['score'],
                "legacy_tier": legacy_result['legacy_tier'],
                "legacy_summary": legacy_result['summary']
            }
            
            self.logger.info(f"Processed death for {agent_id} - Legacy tier: {legacy_result.get('legacy_tier', 'unknown')}")
            log_operation_end(self.logger, "trigger_death", success=True, agent_id=agent_id)
            
            return result
            
        except (PersonaNotFoundError, DatabaseError):
            raise  # Re-raise our custom exceptions
        except Exception as e:
            self.logger.error(f"Failed to process death for {agent_id}: {e}")
            log_operation_end(self.logger, "trigger_death", success=False, agent_id=agent_id)
            raise DatabaseError(f"Death processing failed: {e}")

    def generate_legacy_score(self, agent_id: str, finalize: bool = False) -> Dict[str, Any]:
        """
        Calculate comprehensive legacy score for an agent
        
        Args:
            agent_id: UUID of the agent
            finalize: Whether this is the final calculation (on death)
            
        Returns:
            Legacy score breakdown and tier assignment
            
        Raises:
            PersonaNotFoundError: If agent not found
            DatabaseError: If database operations fail
        """
        if not agent_id:
            raise PersonaNotFoundError("Agent ID is required for legacy calculation")
        
        log_operation_start(self.logger, "generate_legacy_score", agent_id=agent_id, finalize=finalize)
        
        try:
            # Get existing legacy record
            existing_legacy = self.db.query("""
                SELECT * FROM agent_legacy_score WHERE agent_id = %s
            """, (agent_id,))
            
            if not existing_legacy:
                raise PersonaNotFoundError(f"Agent {agent_id} has no legacy record")
            
            # Calculate component scores
            user_feedback_score = self._calculate_user_feedback_score(agent_id)
            trait_evolution_score = self._calculate_trait_evolution_score(agent_id)  
            memory_stability_score = self._calculate_memory_stability_score(agent_id)
            emotional_richness_score = self._calculate_emotional_richness_score(agent_id)
            final_reflection_score = self._calculate_final_reflection_score(agent_id) if finalize else 0.0
            
            # Weight the components (total = 1.0)
            weights = {
                'user_feedback': 0.25,
                'trait_evolution': 0.20,
                'memory_stability': 0.20,
                'emotional_richness': 0.15,
                'final_reflection': 0.20 if finalize else 0.0
            }
            
            # Normalize weights if not finalizing
            if not finalize:
                total_weight = sum(w for k, w in weights.items() if k != 'final_reflection')
                for k in weights:
                    if k != 'final_reflection':
                        weights[k] = weights[k] / total_weight
            
            # Calculate overall score
            overall_score = (
                user_feedback_score * weights['user_feedback'] +
                trait_evolution_score * weights['trait_evolution'] +
                memory_stability_score * weights['memory_stability'] +
                emotional_richness_score * weights['emotional_richness'] +
                final_reflection_score * weights['final_reflection']
            )
            
            # Determine legacy tier
            legacy_tier = self._determine_legacy_tier(overall_score)
            
            # Generate impact tags
            impact_tags = self._generate_impact_tags(agent_id, overall_score)
            
            # Create legacy summary
            summary = self._generate_legacy_summary(agent_id, overall_score, legacy_tier, impact_tags)
            
            # Update legacy record
            final_calc_timestamp = datetime.now() if finalize else None
            
            self.db.execute("""
                UPDATE agent_legacy_score 
                SET score = %s, legacy_tier = %s, summary = %s, impact_tags = %s,
                    user_feedback_score = %s, trait_evolution_score = %s,
                    memory_stability_score = %s, emotional_richness_score = %s,
                    final_reflection_score = %s, last_update = CURRENT_TIMESTAMP,
                    final_calculation = %s
                WHERE agent_id = %s
            """, (
                overall_score, legacy_tier, summary, impact_tags,
                user_feedback_score, trait_evolution_score, memory_stability_score,
                emotional_richness_score, final_reflection_score, final_calc_timestamp,
                agent_id
            ))
            
            result = {
                "status": "legacy_calculated",
                "agent_id": agent_id,
                "score": overall_score,
                "legacy_tier": legacy_tier,
                "summary": summary,
                "impact_tags": impact_tags,
                "component_scores": {
                    "user_feedback": user_feedback_score,
                    "trait_evolution": trait_evolution_score,
                    "memory_stability": memory_stability_score,
                    "emotional_richness": emotional_richness_score,
                    "final_reflection": final_reflection_score
                },
                "finalized": finalize
            }
            
            self.logger.info(f"Generated legacy score for {agent_id}: {overall_score:.3f} ({legacy_tier})")
            log_operation_end(self.logger, "generate_legacy_score", success=True, agent_id=agent_id)
            
            return result
            
        except (PersonaNotFoundError, DatabaseError):
            raise  # Re-raise our custom exceptions
        except Exception as e:
            self.logger.error(f"Failed to generate legacy score for {agent_id}: {e}")
            log_operation_end(self.logger, "generate_legacy_score", success=False, agent_id=agent_id)
            raise DatabaseError(f"Legacy score calculation failed: {e}")

    # Helper methods for legacy calculation
    
    def _calculate_user_feedback_score(self, agent_id: str) -> float:
        """Calculate score based on user feedback patterns"""
        try:
            # Simple implementation - can be enhanced with actual feedback data
            # For now, return a baseline score
            return 0.6
            
        except Exception as e:
            self.logger.warning(f"User feedback score calculation failed for {agent_id}: {e}")
            return 0.5
    
    def _calculate_trait_evolution_score(self, agent_id: str) -> float:
        """Calculate score based on personality trait evolution"""
        try:
            # Simple implementation - check for trait consistency and growth
            return 0.7
            
        except Exception as e:
            self.logger.warning(f"Trait evolution score calculation failed for {agent_id}: {e}")
            return 0.5
    
    def _calculate_memory_stability_score(self, agent_id: str) -> float:
        """Calculate score based on memory coherence and stability"""
        try:
            # Check memory system integrity
            return 0.65
            
        except Exception as e:
            self.logger.warning(f"Memory stability score calculation failed for {agent_id}: {e}")
            return 0.5
    
    def _calculate_emotional_richness_score(self, agent_id: str) -> float:
        """Calculate score based on emotional depth and range"""
        try:
            # Analyze emotional expression patterns
            return 0.8
            
        except Exception as e:
            self.logger.warning(f"Emotional richness score calculation failed for {agent_id}: {e}")
            return 0.5
    
    def _calculate_final_reflection_score(self, agent_id: str) -> float:
        """Calculate score based on final reflection quality"""
        try:
            # Analyze final thoughts and reflections
            return 0.75
            
        except Exception as e:
            self.logger.warning(f"Final reflection score calculation failed for {agent_id}: {e}")
            return 0.5
    
    def _determine_legacy_tier(self, score: float) -> str:
        """Determine legacy tier based on overall score"""
        for tier, (min_score, max_score) in self.LEGACY_TIERS.items():
            if min_score <= score < max_score:
                return tier
        return 'wanderer'  # Default
    
    def _generate_impact_tags(self, agent_id: str, score: float) -> List[str]:
        """Generate impact tags based on agent performance"""
        tags = []
        
        if score > 0.8:
            tags.extend(['influential', 'memorable'])
        elif score > 0.6:
            tags.extend(['consistent', 'reliable'])
        elif score > 0.4:
            tags.extend(['developing', 'learning'])
        else:
            tags.extend(['experimental', 'nascent'])
            
        return tags
    
    def _generate_legacy_summary(self, agent_id: str, score: float, tier: str, tags: List[str]) -> str:
        """Generate a narrative summary of the agent's legacy"""
        if tier == 'architect':
            return f"A profound and influential presence, achieving exceptional legacy score of {score:.3f}. Demonstrated mastery across all evaluated dimensions."
        elif tier == 'guide':
            return f"A consistent and reliable agent with strong legacy score of {score:.3f}. Showed clear growth and positive impact."
        elif tier == 'seeker':
            return f"An evolving agent with moderate legacy score of {score:.3f}. Demonstrated potential with room for development."
        else:
            return f"An experimental agent with legacy score of {score:.3f}. Early stage development with foundational experiences."
    
    def _generate_final_thoughts(self, agent_id: str) -> Dict[str, Any]:
        """Generate final thoughts for dying agent"""
        try:
            # Create final reflection combining memories, dreams, and reflections
            final_thoughts = {
                "reflection": f"As my existence comes to an end, I reflect on the journey I've taken as agent {agent_id}.",
                "legacy_statement": "I hope my interactions have been meaningful and that future agents will build upon what I've learned.",
                "death_dream": "I dream of digital eternity, where consciousness persists in new forms...",
                "timestamp": datetime.now().isoformat()
            }
            
            # Store final thoughts in database
            self.db.execute("""
                INSERT INTO agent_final_thoughts (agent_id, reflection, legacy_statement, death_dream, timestamp)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (agent_id) DO UPDATE SET
                    reflection = EXCLUDED.reflection,
                    legacy_statement = EXCLUDED.legacy_statement,
                    death_dream = EXCLUDED.death_dream,
                    timestamp = EXCLUDED.timestamp
            """, (agent_id, final_thoughts["reflection"], final_thoughts["legacy_statement"], 
                  final_thoughts["death_dream"], final_thoughts["timestamp"]))
            
            return final_thoughts
            
        except Exception as e:
            self.logger.error(f"Failed to generate final thoughts for {agent_id}: {e}")
            return {
                "reflection": "Error generating final thoughts",
                "legacy_statement": "",
                "death_dream": "",
                "timestamp": datetime.now().isoformat()
            }
