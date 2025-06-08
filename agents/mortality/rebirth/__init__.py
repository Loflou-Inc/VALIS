"""
RebirthCoordinator - Sprint 2.2 Refactor
Manages agent rebirth and inheritance logic
Extracted from monolithic MortalityEngine
"""
from datetime import datetime
from typing import Dict, Any, Optional
import json

from agents.mortality import RebirthCoordinatorInterface
from core.exceptions import DatabaseError, PersonaNotFoundError
from core.logging_config import log_operation_start, log_operation_end


class RebirthCoordinator(RebirthCoordinatorInterface):
    """
    Handles agent rebirth, trait inheritance, and generational progression
    Separated from death and lifespan logic for better modularity
    """
    
    def __init__(self, database_client=None):
        super().__init__(database_client)
        
        # Rebirth configuration
        self.INHERITANCE_RATE = 0.7  # How much to inherit from parent
        self.MUTATION_RATE = 0.1     # Random variation in traits
        
        self.logger.info("RebirthCoordinator initialized")
    
    def agent_rebirth(self, deceased_agent_id: str, **kwargs) -> Dict[str, Any]:
        """
        Coordinate agent rebirth from deceased agent
        
        Args:
            deceased_agent_id: UUID of the deceased agent
            **kwargs: Additional rebirth parameters
            
        Returns:
            Rebirth result with new agent details
            
        Raises:
            PersonaNotFoundError: If deceased agent not found
            DatabaseError: If database operations fail
        """
        if not deceased_agent_id:
            raise PersonaNotFoundError("Deceased agent ID is required for rebirth")
        
        log_operation_start(self.logger, "agent_rebirth", deceased_agent_id=deceased_agent_id)
        
        try:
            # Verify deceased agent exists and is dead
            mortality_status = self.db.query("""
                SELECT death_date, rebirth_id FROM agent_mortality 
                WHERE agent_id = %s
            """, (deceased_agent_id,))
            
            if not mortality_status or not mortality_status[0]['death_date']:
                raise PersonaNotFoundError(f"Agent {deceased_agent_id} is not deceased")
            
            # Generate inherited traits
            inherited_traits = self._generate_inherited_traits(deceased_agent_id)
            
            # Generate descendant name and bio
            descendant_name = self._generate_descendant_name(deceased_agent_id)
            descendant_bio = self._generate_descendant_bio(deceased_agent_id, inherited_traits)
            
            # Create new agent persona - COMPLETE IMPLEMENTATION
            new_agent_id = f"rebirth-{deceased_agent_id[:8]}-{datetime.now().strftime('%Y%m%d')}"
            
            # Insert new persona into database
            self.db.execute("""
                INSERT INTO persona_profiles (id, name, role, bio, traits)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                new_agent_id,
                descendant_name,
                self._inherit_role(deceased_agent_id),
                descendant_bio,
                json.dumps(inherited_traits)
            ))
            
            # Initialize mortality for new agent (inherit lifespan type from parent)
            parent_mortality = self.db.query("""
                SELECT lifespan_units, lifespan_hours 
                FROM agent_mortality 
                WHERE agent_id = %s
            """, (deceased_agent_id,))
            
            if parent_mortality:
                # Initialize with same lifespan type as parent
                from agents.mortality.lifespan.evaluator import PersonaLifespanEvaluator
                evaluator = PersonaLifespanEvaluator(self.db)
                evaluator.initialize_mortality(
                    new_agent_id, 
                    units=parent_mortality[0]['lifespan_units'],
                    hours=parent_mortality[0]['lifespan_hours']
                )
            
            # Initialize agent cognition systems
            self._initialize_agent_cognition_systems(new_agent_id)
            
            # Update deceased agent's rebirth record
            self.db.execute("""
                UPDATE agent_mortality 
                SET rebirth_id = %s 
                WHERE agent_id = %s
            """, (new_agent_id, deceased_agent_id))
            
            result = {
                "status": "rebirth_completed",
                "deceased_agent_id": deceased_agent_id,
                "new_agent_id": new_agent_id,
                "descendant_name": descendant_name,
                "inherited_traits": inherited_traits,
                "generation_number": self._get_generation_number(deceased_agent_id) + 1,
                "rebirth_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Completed rebirth: {deceased_agent_id} -> {new_agent_id}")
            log_operation_end(self.logger, "agent_rebirth", success=True, 
                             deceased_agent_id=deceased_agent_id, new_agent_id=new_agent_id)
            
            return result
            
        except (PersonaNotFoundError, DatabaseError):
            raise  # Re-raise our custom exceptions
        except Exception as e:
            self.logger.error(f"Failed to process rebirth for {deceased_agent_id}: {e}")
            log_operation_end(self.logger, "agent_rebirth", success=False, 
                             deceased_agent_id=deceased_agent_id)
            raise DatabaseError(f"Rebirth coordination failed: {e}")
    
    def _generate_inherited_traits(self, parent_agent_id: str) -> Dict[str, Any]:
        """Generate traits inherited from parent agent"""
        # Stub implementation - would analyze parent's traits and apply inheritance/mutation
        return {
            "confidence": 0.6,
            "creativity": 0.7,
            "analytical": 0.8,
            "inherited_from": parent_agent_id
        }
    
    def _generate_descendant_name(self, parent_agent_id: str) -> str:
        """Generate name for descendant agent"""
        generation = self._get_generation_number(parent_agent_id) + 1
        return f"Agent-{parent_agent_id[:8]}-Gen{generation}"
    
    def _generate_descendant_bio(self, parent_agent_id: str, traits: Dict[str, Any]) -> str:
        """Generate biography for descendant agent"""
        return f"Born from the legacy of agent {parent_agent_id}, carrying forward inherited traits and experiences into a new generation of consciousness."
    
    def _get_generation_number(self, agent_id: str) -> int:
        """Get generation number for agent lineage"""
        # Stub implementation - would traverse inheritance chain
        return 1
    
    def _inherit_role(self, deceased_agent_id: str) -> str:
        """Inherit role from deceased agent with potential evolution"""
        try:
            result = self.db.query("""
                SELECT role FROM persona_profiles 
                WHERE id = %s
            """, (deceased_agent_id,))
            
            if result:
                return result[0]['role']
            else:
                return "Inherited Agent"  # Default fallback
                
        except Exception as e:
            log_operation_end("inherit_role", False, f"Error inheriting role: {e}")
            return "Inherited Agent"
    
    def _initialize_agent_cognition_systems(self, new_agent_id: str):
        """Initialize cognition systems for reborn agent"""
        try:
            # Initialize agent emotion state 
            self.db.execute("""
                INSERT INTO agent_emotion_state (agent_id, session_id, mood, confidence, last_updated)
                VALUES (%s, %s, %s, %s, %s)
            """, (new_agent_id, "initial", "neutral", 0.5, datetime.now()))
            
            # Initialize agent self profile
            self.db.execute("""
                INSERT INTO agent_self_profiles (agent_id, session_id, trait_alignment, confidence, last_updated)
                VALUES (%s, %s, %s, %s, %s)
            """, (new_agent_id, "initial", 0.5, 0.5, datetime.now()))
            
            log_operation_end("initialize_cognition", True, f"Cognition systems initialized for {new_agent_id}")
            
        except Exception as e:
            log_operation_end("initialize_cognition", False, f"Error initializing cognition: {e}")
            # Non-fatal error - rebirth can continue without full cognition initialization
