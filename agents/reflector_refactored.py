"""
VALIS Synthetic Cognition Layer - AgentReflector
Metacognitive reflection and plan evaluation
Sprint 1.2: Exception Refactor + Structured Logging
"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

# Import VALIS logging and exceptions
from core.valis_logging import get_valis_logger, CognitiveOperation
from core.exceptions import (
    ReflectorError, ReflectionGenerationError, DatabaseError,
    InputValidationError, handle_cognitive_error
)

# Initialize logger with VALIS context
logger = get_valis_logger(__name__)


class AgentReflector:
    """Manages agent metacognitive reflection and plan evaluation"""
    
    def __init__(self, db_client):
        """Initialize with database client"""
        self.db = db_client
        logger.info("AgentReflector initialized", cognitive_module="reflector")
    
    def reflect_on_plan_result(self, plan: dict, outcome: dict, ego_state: dict, session_id: str) -> str:
        """Perform metacognitive reflection on plan execution results"""
        
        # Set context for this operation
        logger.set_context(
            session_id=session_id,
            cognitive_module="reflector",
            operation="reflect_on_plan_result"
        )
        
        with CognitiveOperation(logger, "reflection_analysis", session_id=session_id):
            
            # Validate inputs
            if not session_id:
                raise InputValidationError("session_id is required for reflection")
            
            if not isinstance(plan, dict) or not isinstance(outcome, dict):
                raise InputValidationError("plan and outcome must be dictionaries")
            
            if not isinstance(ego_state, dict):
                raise InputValidationError("ego_state must be a dictionary")
            
            try:
                # Analyze plan success
                plan_success_score = self._calculate_plan_success(plan, outcome)
                logger.debug(f"Calculated plan success score: {plan_success_score:.3f}")
                
                # Analyze ego alignment during execution
                ego_alignment_score = ego_state.get('alignment_score', 0.5)
                logger.debug(f"Ego alignment score: {ego_alignment_score:.3f}")
                
                # Generate reflection text based on performance
                reflection_text = self._generate_reflection_text(
                    plan_success_score, 
                    ego_alignment_score, 
                    outcome
                )
                
                # Extract reflection tags for categorization
                tags = self._extract_reflection_tags(plan, outcome, plan_success_score)
                
                logger.info(
                    "Generated reflection successfully",
                    plan_success_score=plan_success_score,
                    ego_alignment_score=ego_alignment_score,
                    reflection_tags=tags
                )
                
                return reflection_text
                
            except (ValueError, TypeError) as e:
                raise ReflectionGenerationError(
                    f"Invalid data for reflection generation: {e}"
                ) from e
            except KeyError as e:
                raise ReflectionGenerationError(
                    f"Missing required field for reflection: {e}"
                ) from e
            except Exception as e:
                logger.critical(
                    "Unexpected error during reflection generation",
                    error_details=str(e),
                    exc_info=True
                )
                raise ReflectorError(
                    f"Unexpected error during reflection generation: {e}"
                ) from e
            finally:
                logger.clear_context()
    
    def log_reflection(self, session_id: str, reflection: str, persona_id: str, 
                      plan_success_score: float = None, ego_alignment_score: float = None) -> None:
        """Log reflection to database"""
        
        logger.set_context(
            session_id=session_id,
            persona_id=persona_id,
            cognitive_module="reflector",
            operation="log_reflection"
        )
        
        with CognitiveOperation(logger, "reflection_logging", 
                              session_id=session_id, persona_id=persona_id):
            
            # Validate inputs
            if not session_id or not reflection or not persona_id:
                raise InputValidationError(
                    "session_id, reflection, and persona_id are required"
                )
            
            if len(reflection.strip()) == 0:
                raise InputValidationError("reflection cannot be empty")
            
            try:
                # Generate reflection tags
                tags = ["metacognitive_analysis"]
                if plan_success_score is not None:
                    if plan_success_score > 0.8:
                        tags.append("high_success")
                    elif plan_success_score < 0.4:
                        tags.append("needs_improvement")
                
                # Insert into database
                reflection_id = str(uuid.uuid4())
                self.db.execute("""
                    INSERT INTO agent_reflection_log (id, session_id, persona_id, reflection_text, 
                                                     plan_success_score, ego_alignment_score, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (reflection_id, session_id, persona_id, reflection, 
                      plan_success_score, ego_alignment_score, datetime.utcnow()))
                
                logger.info(
                    "Reflection logged successfully",
                    reflection_id=reflection_id,
                    reflection_length=len(reflection),
                    tags=tags
                )
                
            except Exception as e:
                # Check if it's a database error
                error_msg = str(e).lower()
                if any(term in error_msg for term in ['database', 'sql', 'connection', 'table']):
                    raise DatabaseError(
                        f"Database error while logging reflection: {e}"
                    ) from e
                else:
                    logger.critical(
                        "Unexpected error during reflection logging",
                        error_details=str(e),
                        exc_info=True
                    )
                    raise ReflectorError(
                        f"Failed to log reflection: {e}"
                    ) from e
            finally:
                logger.clear_context()
    
    def suggest_replan(self, ego_score: float, outcome_quality: float) -> bool:
        """Determine if replanning is suggested based on performance"""
        
        logger.set_context(
            cognitive_module="reflector",
            operation="suggest_replan"
        )
        
        try:
            # Validate inputs
            if not isinstance(ego_score, (int, float)) or not isinstance(outcome_quality, (int, float)):
                raise InputValidationError("ego_score and outcome_quality must be numeric")
            
            if not (0.0 <= ego_score <= 1.0) or not (0.0 <= outcome_quality <= 1.0):
                raise InputValidationError("scores must be between 0.0 and 1.0")
            
            # Replan decision logic
            should_replan = False
            reason = None
            
            if ego_score < 0.3 and outcome_quality < 0.4:
                should_replan = True
                reason = "low ego alignment and poor outcome"
            elif outcome_quality < 0.2:
                should_replan = True  
                reason = "very poor outcome quality"
            
            logger.info(
                "Replan suggestion generated",
                ego_score=ego_score,
                outcome_quality=outcome_quality,
                should_replan=should_replan,
                reason=reason
            )
            
            return should_replan
            
        except InputValidationError:
            raise  # Re-raise validation errors
        except Exception as e:
            logger.error(
                "Unexpected error in replan suggestion",
                ego_score=ego_score,
                outcome_quality=outcome_quality,
                error_details=str(e),
                exc_info=True
            )
            # Return safe default for replan suggestion
            return False
        finally:
            logger.clear_context()
