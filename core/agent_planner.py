#!/usr/bin/env python3
"""
VALIS Agent Planner - Sprint 10 Implementation
Autonomous multi-step planning and tool chaining for VALIS personas
"""

import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import sys
import os
from pathlib import Path

from core.tool_manager import tool_manager
from memory.query_client import memory
from memory.db import db
from core.synthetic_cognition_manager import SyntheticCognitionManager

logger = logging.getLogger("AgentPlanner")

class PlanStepType(Enum):
    """Types of planning steps"""
    QUERY_MEMORY = "query_memory"
    TOOL_CALL = "tool_call"
    ANALYSIS = "analysis"
    DECISION = "decision"
    RESPONSE = "response"

class PlanStepStatus(Enum):
    """Status of plan execution steps"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class PlanStep:
    """Individual step in an agent plan"""
    
    def __init__(self, step_id: str, step_type: PlanStepType, description: str,
                 tool_name: str = None, parameters: Dict[str, Any] = None,
                 reasoning: str = None, depends_on: List[str] = None):
        self.step_id = step_id
        self.step_type = step_type
        self.description = description
        self.tool_name = tool_name
        self.parameters = parameters or {}
        self.reasoning = reasoning
        self.depends_on = depends_on or []
        self.status = PlanStepStatus.PENDING
        self.result = None
        self.error = None
        self.execution_time = None
        self.created_at = datetime.now()
        self.executed_at = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary for serialization"""
        return {
            'step_id': self.step_id,
            'step_type': self.step_type.value,
            'description': self.description,
            'tool_name': self.tool_name,
            'parameters': self.parameters,
            'reasoning': self.reasoning,
            'depends_on': self.depends_on,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'execution_time': self.execution_time,
            'created_at': self.created_at.isoformat(),
            'executed_at': self.executed_at.isoformat() if self.executed_at else None
        }

class AgentPlan:
    """Complete agent execution plan"""
    
    def __init__(self, plan_id: str, goal: str, client_id: str, persona_id: str):
        self.plan_id = plan_id
        self.goal = goal
        self.client_id = client_id
        self.persona_id = persona_id
        self.steps: List[PlanStep] = []
        self.status = "planning"
        self.created_at = datetime.now()
        self.completed_at = None
        self.context = {}
        self.max_steps = 5  # Safety limit
        
    def add_step(self, step: PlanStep):
        """Add step to plan with validation"""
        if len(self.steps) >= self.max_steps:
            raise ValueError(f"Plan exceeds maximum steps ({self.max_steps})")
        self.steps.append(step)
        
    def get_pending_steps(self) -> List[PlanStep]:
        """Get steps ready for execution"""
        pending = []
        for step in self.steps:
            if step.status == PlanStepStatus.PENDING:
                # Check if dependencies are met
                deps_met = all(
                    any(s.step_id == dep_id and s.status == PlanStepStatus.COMPLETED 
                        for s in self.steps)
                    for dep_id in step.depends_on
                )
                if not step.depends_on or deps_met:
                    pending.append(step)
        return pending
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary for serialization"""
        return {
            'plan_id': self.plan_id,
            'goal': self.goal,
            'client_id': self.client_id,
            'persona_id': self.persona_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'context': self.context,
            'steps': [step.to_dict() for step in self.steps]
        }

class AgentPlanner:
    """
    Autonomous planning system for VALIS agents
    Creates and executes multi-step workflows based on goals
    """
    
    def __init__(self):
        self.active_plans: Dict[str, AgentPlan] = {}
        self.config = {
            "max_concurrent_plans": 10,
            "max_plan_steps": 5,
            "execution_timeout": 300,  # 5 minutes
            "enable_memory_precheck": True,
            "enable_safety_checks": True
        }
        self.cognition_manager = SyntheticCognitionManager()
        logger.info("AgentPlanner initialized with synthetic cognition")
    
    async def create_plan(self, goal: str, client_id: str, persona_id: str,
                         context: Dict[str, Any] = None) -> AgentPlan:
        """
        Create a multi-step plan to achieve the given goal
        
        Args:
            goal: The objective to achieve
            client_id: Client UUID for context
            persona_id: Persona UUID for strategy
            context: Additional context for planning
            
        Returns:
            AgentPlan: Complete execution plan
        """
        plan_id = str(uuid.uuid4())[:8]
        
        logger.info(f"Creating plan {plan_id} for goal: {goal[:50]}...")
        
        # Create plan object
        plan = AgentPlan(plan_id, goal, client_id, persona_id)
        if context:
            plan.context.update(context)
        
        # Get persona for strategy
        try:
            persona = memory.get_persona(persona_id)
            if not persona:
                raise ValueError(f"Persona {persona_id} not found")
        except Exception as e:
            logger.error(f"Failed to get persona {persona_id}: {e}")
            raise
        
        # Analyze goal and determine planning strategy
        planning_strategy = self._determine_strategy(goal, persona)
        
        # Build plan steps based on strategy
        if planning_strategy == "memory_first":
            await self._build_memory_first_plan(plan, goal, persona)
        elif planning_strategy == "tool_chain":
            await self._build_tool_chain_plan(plan, goal, persona)
        elif planning_strategy == "analysis_deep":
            await self._build_analysis_plan(plan, goal, persona)
        else:
            # Default: simple execution plan
            await self._build_simple_plan(plan, goal, persona)
        
        # Store active plan
        self.active_plans[plan_id] = plan
        
        # Persist plan to database for admin monitoring
        await self._persist_plan(plan)
        
        logger.info(f"Plan {plan_id} created with {len(plan.steps)} steps")
        return plan
    
    def _determine_strategy(self, goal: str, persona: Dict[str, Any]) -> str:
        """Determine planning strategy based on goal and persona"""
        goal_lower = goal.lower()
        persona_name = persona.get('name', '').lower()
        
        # Memory-related goals
        if any(keyword in goal_lower for keyword in 
               ['remember', 'recall', 'know about', 'what do you', 'tell me about']):
            return "memory_first"
        
        # File/system operations
        if any(keyword in goal_lower for keyword in 
               ['file', 'directory', 'search', 'find', 'list', 'read']):
            return "tool_chain"
        
        # Analysis tasks
        if any(keyword in goal_lower for keyword in 
               ['analyze', 'compare', 'evaluate', 'summarize', 'report']):
            return "analysis_deep"
        
        # Persona-specific strategies
        if 'kai' in persona_name:
            return "motivational_action"
        elif 'luna' in persona_name:
            return "empathetic_analysis"
        elif 'jane' in persona_name:
            return "structured_process"
        
        return "simple"
    
    async def _build_memory_first_plan(self, plan: AgentPlan, goal: str, persona: Dict[str, Any]):
        """Build plan that starts with memory query"""
        # Step 1: Query memory for context
        memory_step = PlanStep(
            step_id="mem_001",
            step_type=PlanStepType.QUERY_MEMORY,
            description="Query memory for relevant context",
            tool_name="query_memory",
            parameters={
                "user_id": plan.client_id,
                "topic": self._extract_topic_from_goal(goal)
            },
            reasoning="Check existing knowledge before proceeding"
        )
        plan.add_step(memory_step)
        
        # Step 2: Analyze memory results and plan next action
        analysis_step = PlanStep(
            step_id="ana_001",
            step_type=PlanStepType.ANALYSIS,
            description="Analyze memory results and determine response strategy",
            reasoning="Base response on retrieved memories and persona knowledge",
            depends_on=["mem_001"]
        )
        plan.add_step(analysis_step)
        
        # Step 3: Generate final response
        response_step = PlanStep(
            step_id="res_001",
            step_type=PlanStepType.RESPONSE,
            description="Generate contextual response based on memory and analysis",
            reasoning="Provide informed answer using retrieved context",
            depends_on=["ana_001"]
        )
        plan.add_step(response_step)
    
    async def _build_tool_chain_plan(self, plan: AgentPlan, goal: str, persona: Dict[str, Any]):
        """Build plan with tool chaining for file/system operations"""
        goal_lower = goal.lower()
        
        if 'list' in goal_lower and ('file' in goal_lower or 'director' in goal_lower):
            # File listing workflow
            list_step = PlanStep(
                step_id="tool_001",
                step_type=PlanStepType.TOOL_CALL,
                description="List directory contents",
                tool_name="list_directory",
                parameters={"path": self._extract_path_from_goal(goal)},
                reasoning="Get directory contents as requested"
            )
            plan.add_step(list_step)
            
        elif 'search' in goal_lower or 'find' in goal_lower:
            # Search workflow
            search_step = PlanStep(
                step_id="tool_001", 
                step_type=PlanStepType.TOOL_CALL,
                description="Search for files matching criteria",
                tool_name="search_files",
                parameters={"keyword": self._extract_search_term_from_goal(goal)},
                reasoning="Locate files matching the search criteria"
            )
            plan.add_step(search_step)
            
        elif 'read' in goal_lower and 'file' in goal_lower:
            # File reading workflow  
            read_step = PlanStep(
                step_id="tool_001",
                step_type=PlanStepType.TOOL_CALL,
                description="Read file contents",
                tool_name="read_file", 
                parameters={"path": self._extract_path_from_goal(goal)},
                reasoning="Read the requested file contents"
            )
            plan.add_step(read_step)
        
        # Add analysis step for tool results
        analysis_step = PlanStep(
            step_id="ana_001",
            step_type=PlanStepType.ANALYSIS,
            description="Analyze tool results and prepare response",
            reasoning="Process tool output for user presentation",
            depends_on=["tool_001"]
        )
        plan.add_step(analysis_step)
    
    async def _build_analysis_plan(self, plan: AgentPlan, goal: str, persona: Dict[str, Any]):
        """Build plan for analysis and comparison tasks"""
        # Step 1: Gather information
        info_step = PlanStep(
            step_id="info_001",
            step_type=PlanStepType.QUERY_MEMORY,
            description="Gather relevant information for analysis",
            tool_name="query_memory",
            parameters={
                "user_id": plan.client_id,
                "topic": self._extract_topic_from_goal(goal)
            },
            reasoning="Collect baseline information for analysis"
        )
        plan.add_step(info_step)
        
        # Step 2: Deep analysis
        analysis_step = PlanStep(
            step_id="ana_001",
            step_type=PlanStepType.ANALYSIS,
            description="Perform detailed analysis of gathered information",
            reasoning="Analyze data to identify patterns and insights",
            depends_on=["info_001"]
        )
        plan.add_step(analysis_step)
        
        # Step 3: Generate structured response
        response_step = PlanStep(
            step_id="res_001",
            step_type=PlanStepType.RESPONSE,
            description="Generate structured analysis response",
            reasoning="Present analysis in clear, actionable format",
            depends_on=["ana_001"]
        )
        plan.add_step(response_step)
    
    async def _build_simple_plan(self, plan: AgentPlan, goal: str, persona: Dict[str, Any]):
        """Build simple single-step plan"""
        simple_step = PlanStep(
            step_id="sim_001",
            step_type=PlanStepType.RESPONSE,
            description="Generate direct response to goal",
            reasoning="Straightforward response using persona knowledge"
        )
        plan.add_step(simple_step)
    
    def _extract_topic_from_goal(self, goal: str) -> str:
        """Extract search topic from goal text"""
        # Simple extraction - in production would use NLP
        goal_lower = goal.lower()
        
        # Remove common question words
        for word in ['what', 'do', 'you', 'know', 'about', 'tell', 'me']:
            goal_lower = goal_lower.replace(word, '')
        
        return goal_lower.strip() or "general"
    
    def _extract_path_from_goal(self, goal: str) -> str:
        """Extract file path from goal text"""
        # Look for path-like strings
        import re
        
        # Match C:\ paths or relative paths
        path_match = re.search(r'[a-zA-Z]:[\\\/][\w\\\/\.\-]+|[\w\\\/\.\-]+', goal)
        if path_match:
            return path_match.group(0)
        
        return "C:\\VALIS"  # Default path
    
    def _extract_search_term_from_goal(self, goal: str) -> str:
        """Extract search term from goal text"""
        goal_lower = goal.lower()
        
        # Remove action words
        for word in ['search', 'find', 'look', 'for', 'files', 'named']:
            goal_lower = goal_lower.replace(word, '')
        
        return goal_lower.strip() or "*.txt"
    
    async def _persist_plan(self, plan: AgentPlan):
        """Save plan to database for monitoring"""
        try:
            db.execute("""
                INSERT INTO agent_plans 
                (plan_id, client_id, persona_id, goal, status, plan_data, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                plan.plan_id,
                plan.client_id,
                plan.persona_id,
                plan.goal,
                plan.status,
                json.dumps(plan.to_dict()),
                plan.created_at
            ))
            
            logger.info(f"Plan {plan.plan_id} persisted to database")
            
        except Exception as e:
            logger.warning(f"Failed to persist plan {plan.plan_id}: {e}")
    
    async def execute_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Execute an agent plan step by step
        
        Args:
            plan_id: ID of plan to execute
            
        Returns:
            Execution results and final response
        """
        if plan_id not in self.active_plans:
            raise ValueError(f"Plan {plan_id} not found")
        
        plan = self.active_plans[plan_id]
        plan.status = "executing"
        
        logger.info(f"Executing plan {plan_id} with {len(plan.steps)} steps")
        
        execution_results = []
        final_response = ""
        
        try:
            while True:
                pending_steps = plan.get_pending_steps()
                
                if not pending_steps:
                    # No more steps to execute
                    break
                
                # Execute next pending step
                for step in pending_steps:
                    result = await self._execute_step(step, plan)
                    execution_results.append(result)
                    
                    # Update plan context with step results
                    if result.get('success') and result.get('result'):
                        plan.context[f"step_{step.step_id}"] = result['result']
                    
                    # Break after first step to check dependencies
                    break
            
            # Generate final response based on execution results
            final_response = await self._generate_final_response(plan, execution_results)
            
            plan.status = "completed"
            plan.completed_at = datetime.now()
            
            # Trigger post-execution reflection
            try:
                # Get current cognition state
                session_id = context.get('session_id') if context else None
                if session_id:
                    ego_state = self.cognition_manager.get_cognition_state(persona_id, session_id)
                    
                    # Calculate plan outcome quality
                    success_rate = len([r for r in execution_results if r.get('success')]) / max(len(execution_results), 1)
                    outcome_data = {
                        'status': 'completed',
                        'success_rate': success_rate,
                        'error_count': len([r for r in execution_results if not r.get('success')]),
                        'execution_time': (datetime.now() - plan.created_at).total_seconds()
                    }
                    
                    # Generate reflection
                    reflection_text = self.cognition_manager.reflector.reflect_on_plan_result(
                        plan.to_dict(), outcome_data, ego_state.get('self', {}), session_id
                    )
                    
                    # Log reflection
                    self.cognition_manager.reflector.log_reflection(
                        session_id, reflection_text, persona_id, 
                        success_rate, ego_state.get('self', {}).get('alignment_score', 0.5)
                    )
                    
                    logger.info(f"Plan reflection logged for {plan_id}")
                    
            except Exception as e:
                logger.error(f"Failed to generate reflection for plan {plan_id}: {e}")
            
            logger.info(f"Plan {plan_id} completed successfully")
            
            return {
                'success': True,
                'plan_id': plan_id,
                'steps_executed': len([r for r in execution_results if r.get('success')]),
                'execution_results': execution_results,
                'final_response': final_response,
                'plan_summary': plan.to_dict()
            }
            
        except Exception as e:
            plan.status = "failed"
            logger.error(f"Plan {plan_id} execution failed: {e}")
            
            return {
                'success': False,
                'plan_id': plan_id,
                'error': str(e),
                'execution_results': execution_results,
                'plan_summary': plan.to_dict()
            }
        
        finally:
            # Update plan in database
            await self._update_plan_status(plan)
    
    async def _execute_step(self, step: PlanStep, plan: AgentPlan) -> Dict[str, Any]:
        """Execute a single plan step"""
        step.status = PlanStepStatus.IN_PROGRESS
        step.executed_at = datetime.now()
        start_time = datetime.now()
        
        logger.info(f"Executing step {step.step_id}: {step.description}")
        
        try:
            if step.step_type == PlanStepType.TOOL_CALL:
                # Execute tool via ToolManager
                result = tool_manager.execute_tool(
                    tool_name=step.tool_name,
                    parameters=step.parameters,
                    client_id=plan.client_id,
                    persona_id=plan.persona_id,
                    request_id=f"plan_{plan.plan_id}_{step.step_id}"
                )
                
                if result['success']:
                    step.status = PlanStepStatus.COMPLETED
                    step.result = result
                else:
                    step.status = PlanStepStatus.FAILED
                    step.error = result.get('error')
                
                return result
                
            elif step.step_type == PlanStepType.QUERY_MEMORY:
                # Execute memory query
                result = tool_manager.execute_tool(
                    tool_name="query_memory",
                    parameters=step.parameters,
                    client_id=plan.client_id,
                    persona_id=plan.persona_id
                )
                
                step.status = PlanStepStatus.COMPLETED if result['success'] else PlanStepStatus.FAILED
                step.result = result
                return result
                
            elif step.step_type == PlanStepType.ANALYSIS:
                # Perform analysis using LLM (placeholder for now)
                analysis_result = await self._perform_analysis(step, plan)
                step.status = PlanStepStatus.COMPLETED
                step.result = analysis_result
                return analysis_result
                
            elif step.step_type == PlanStepType.RESPONSE:
                # Generate response using LLM (placeholder for now)
                response_result = await self._generate_response(step, plan)
                step.status = PlanStepStatus.COMPLETED
                step.result = response_result
                return response_result
                
            else:
                # Unknown step type
                step.status = PlanStepStatus.FAILED
                step.error = f"Unknown step type: {step.step_type}"
                return {
                    'success': False,
                    'error': step.error
                }
                
        except Exception as e:
            step.status = PlanStepStatus.FAILED
            step.error = str(e)
            logger.error(f"Step {step.step_id} failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        
        finally:
            step.execution_time = (datetime.now() - start_time).total_seconds()
    
    async def _perform_analysis(self, step: PlanStep, plan: AgentPlan) -> Dict[str, Any]:
        """Perform analysis step (placeholder - would use LLM in production)"""
        # Gather context from previous steps
        context_data = []
        for prev_step in plan.steps:
            if prev_step.status == PlanStepStatus.COMPLETED and prev_step.result:
                context_data.append({
                    'step': prev_step.step_id,
                    'result': prev_step.result
                })
        
        analysis = {
            'success': True,
            'analysis_type': 'context_synthesis',
            'context_items': len(context_data),
            'summary': f"Analyzed {len(context_data)} previous steps",
            'insights': ["Data gathered successfully", "Ready for response generation"]
        }
        
        return analysis
    
    async def _generate_response(self, step: PlanStep, plan: AgentPlan) -> Dict[str, Any]:
        """Generate response step (placeholder - would use LLM in production)"""
        # Synthesize all previous step results
        response_parts = []
        
        for prev_step in plan.steps:
            if prev_step.status == PlanStepStatus.COMPLETED and prev_step.result:
                if prev_step.step_type == PlanStepType.TOOL_CALL:
                    tool_result = prev_step.result.get('result', '')
                    response_parts.append(f"Tool result: {tool_result}")
                elif prev_step.step_type == PlanStepType.ANALYSIS:
                    analysis = prev_step.result.get('summary', '')
                    response_parts.append(f"Analysis: {analysis}")
        
        final_response = f"Based on the plan execution:\n\n" + "\n".join(response_parts)
        
        return {
            'success': True,
            'response': final_response,
            'components_used': len(response_parts)
        }
    
    async def _generate_final_response(self, plan: AgentPlan, execution_results: List[Dict[str, Any]]) -> str:
        """Generate final response from all execution results"""
        if not execution_results:
            return f"Plan completed but no results were generated."
        
        # Find the final response step
        for result in reversed(execution_results):
            if result.get('success') and 'response' in result.get('result', {}):
                return result['result']['response']
        
        # Fallback: summarize all results
        successful_steps = [r for r in execution_results if r.get('success')]
        return f"Plan completed successfully with {len(successful_steps)} steps executed."
    
    async def _update_plan_status(self, plan: AgentPlan):
        """Update plan status in database"""
        try:
            db.execute("""
                UPDATE agent_plans 
                SET status = %s, plan_data = %s, completed_at = %s
                WHERE plan_id = %s
            """, (
                plan.status,
                json.dumps(plan.to_dict()),
                plan.completed_at,
                plan.plan_id
            ))
            
        except Exception as e:
            logger.warning(f"Failed to update plan {plan.plan_id}: {e}")
    
    def get_plan_status(self, plan_id: str) -> Dict[str, Any]:
        """Get current status of a plan"""
        if plan_id not in self.active_plans:
            return {'error': 'Plan not found'}
        
        plan = self.active_plans[plan_id]
        return plan.to_dict()
    
    def list_active_plans(self) -> List[Dict[str, Any]]:
        """List all active plans"""
        return [plan.to_dict() for plan in self.active_plans.values()]
    
    async def cancel_plan(self, plan_id: str) -> bool:
        """Cancel an active plan"""
        if plan_id in self.active_plans:
            plan = self.active_plans[plan_id]
            plan.status = "cancelled"
            await self._update_plan_status(plan)
            del self.active_plans[plan_id]
            logger.info(f"Plan {plan_id} cancelled")
            return True
        return False


# Global instance for use across VALIS
agent_planner = AgentPlanner()
