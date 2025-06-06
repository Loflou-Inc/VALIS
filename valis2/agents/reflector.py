"""
VALIS Synthetic Cognition Layer - AgentReflector
Metacognitive reflection and plan evaluation
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class AgentReflector:
    """Manages agent metacognitive reflection and plan evaluation"""
    
    def __init__(self, db_client):
        """Initialize with database client"""
        self.db = db_client
    
    def reflect_on_plan_result(self, plan: dict, outcome: dict, ego_state: dict, session_id: str) -> str:
        """Perform metacognitive reflection on plan execution results"""
        try:
            # Analyze plan success
            plan_success_score = self._calculate_plan_success(plan, outcome)
            
            # Analyze ego alignment during execution
            ego_alignment_score = ego_state.get('alignment_score', 0.5)
            
            # Generate reflection text based on performance
            reflection_text = self._generate_reflection_text(
                plan_success_score, 
                ego_alignment_score, 
                outcome
            )
            
            # Extract reflection tags for categorization
            tags = self._extract_reflection_tags(plan, outcome, plan_success_score)
            
            logger.info(f"Generated reflection for session {session_id}: success={plan_success_score:.3f}")
            
            return reflection_text
            
        except Exception as e:
            logger.error(f"Error reflecting on plan result for session {session_id}: {e}")
            return "I had difficulty analyzing my performance in this session."
    
    def log_reflection(self, session_id: str, reflection: str, persona_id: str, 
                      plan_success_score: float = None, ego_alignment_score: float = None) -> None:
        """Log reflection to database"""
        try:
            tags = ["metacognitive_analysis"]
            if plan_success_score is not None:
                if plan_success_score > 0.8:
                    tags.append("high_success")
                elif plan_success_score < 0.4:
                    tags.append("needs_improvement")
            
            self.db.execute("""
                INSERT INTO agent_reflection_log (session_id, persona_id, reflection, tags, 
                                                 plan_success_score, ego_alignment_score)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (session_id, persona_id, reflection, json.dumps(tags), 
                  plan_success_score, ego_alignment_score))
            
            logger.info(f"Logged reflection for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error logging reflection for session {session_id}: {e}")
    
    def suggest_replan(self, ego_score: float, outcome_quality: float) -> bool:
        """Determine if replanning is suggested based on performance"""
        try:
            # Simple heuristic for Phase 1
            if ego_score < 0.3 and outcome_quality < 0.4:
                logger.info("Suggesting replan due to low ego alignment and poor outcome")
                return True
            elif outcome_quality < 0.2:
                logger.info("Suggesting replan due to very poor outcome quality")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error in replan suggestion: {e}")
            return False
    
    def _calculate_plan_success(self, plan: dict, outcome: dict) -> float:
        """Calculate plan success score from 0.0 to 1.0"""
        try:
            if not plan or not outcome:
                return 0.5
            
            # Simple success calculation based on outcome status
            if outcome.get('status') == 'completed':
                return 0.9
            elif outcome.get('status') == 'partially_completed':
                return 0.6
            elif outcome.get('status') == 'failed':
                return 0.2
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error calculating plan success: {e}")
            return 0.5
    
    def _generate_reflection_text(self, plan_success: float, ego_alignment: float, outcome: dict) -> str:
        """Generate natural language reflection"""
        if plan_success > 0.8 and ego_alignment > 0.7:
            return "I performed well in this session. My actions were aligned with my personality and the plan was executed successfully."
        elif plan_success > 0.6:
            return "I had moderate success in this session. There are some areas where I can improve my approach."
        elif plan_success < 0.4:
            return "This session was challenging. I need to reflect on what went wrong and adjust my strategy."
        else:
            return "I had mixed results in this session. Some aspects went well while others need improvement."
    
    def _extract_reflection_tags(self, plan: dict, outcome: dict, success_score: float) -> List[str]:
        """Extract categorization tags from reflection analysis"""
        tags = []
        
        if success_score > 0.8:
            tags.append("successful_execution")
        elif success_score < 0.4:
            tags.append("execution_issues")
            
        if outcome.get('error_count', 0) > 0:
            tags.append("encountered_errors")
            
        return tags
