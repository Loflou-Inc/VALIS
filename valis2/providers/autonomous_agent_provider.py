#!/usr/bin/env python3
"""
Autonomous Agent Provider - Sprint 10 Implementation
Provider that creates and executes multi-step autonomous plans
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
import os
from pathlib import Path

# Add valis2 to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.agent_planner import agent_planner
from memory.query_client import memory

logger = logging.getLogger("AutonomousAgentProvider")

class AutonomousAgentProvider:
    """
    Autonomous agent provider that creates and executes multi-step plans
    """
    
    def __init__(self):
        self.provider_name = "autonomous_agent"
        self.config = {
            "enable_autonomous_mode": True,
            "require_explicit_planning": False,  # If True, only plan when explicitly requested
            "max_concurrent_plans": 5,
            "planning_timeout": 30,  # seconds
            "execution_timeout": 300  # seconds
        }
        logger.info("AutonomousAgentProvider initialized")
    
    def should_use_autonomous_mode(self, prompt: str, context: Dict[str, Any] = None) -> bool:
        """
        Determine if the prompt requires autonomous planning
        
        Args:
            prompt: User input
            context: Additional context
            
        Returns:
            True if autonomous planning should be used
        """
        if not self.config["enable_autonomous_mode"]:
            return False
        
        prompt_lower = prompt.lower()
        
        # Explicit planning triggers
        planning_triggers = [
            'plan', 'create a plan', 'step by step', 'how would you',
            'what steps', 'analyze and', 'research and', 'find and summarize',
            'check if', 'compare and', 'gather information about'
        ]
        
        if any(trigger in prompt_lower for trigger in planning_triggers):
            return True
        
        # Multi-action indicators
        multi_action_indicators = [
            ' and then ', ' after that', ' followed by', ' next ',
            'first', 'second', 'finally', 'also check'
        ]
        
        if any(indicator in prompt_lower for indicator in multi_action_indicators):
            return True
        
        # Complex queries that benefit from planning
        complex_patterns = [
            ('search', 'analyze'),  # Search then analyze
            ('find', 'summarize'),  # Find then summarize  
            ('list', 'compare'),    # List then compare
            ('check', 'report'),    # Check then report
            ('gather', 'evaluate')  # Gather then evaluate
        ]
        
        for pattern in complex_patterns:
            if all(word in prompt_lower for word in pattern):
                return True
        
        return False
    
    def ask(self, prompt: str, client_id: str, persona_id: str, 
            context: Dict[str, Any] = None, request_id: str = None) -> Dict[str, Any]:
        """
        Process user request with autonomous planning if needed (sync wrapper)
        """
        # Run async method in event loop
        try:
            # Try to get existing loop
            loop = asyncio.get_running_loop()
            # If we're already in a loop, we can't run another coroutine with run_until_complete
            # So we'll just return a fallback response
            return {
                'success': False,
                'error': 'Autonomous mode not available in nested event loop',
                'provider': self.provider_name,
                'fallback_reason': 'Event loop conflict'
            }
        except RuntimeError:
            # No running loop, safe to create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._ask_async(prompt, client_id, persona_id, context, request_id))
            finally:
                loop.close()
    
    async def _ask_async(self, prompt: str, client_id: str, persona_id: str, 
                  context: Dict[str, Any] = None, request_id: str = None) -> Dict[str, Any]:
        """
        Process user request with autonomous planning if needed
        
        Args:
            prompt: User input
            client_id: Client UUID
            persona_id: Persona UUID
            context: Additional context
            request_id: Request tracking ID
            
        Returns:
            Response with autonomous execution results
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Processing autonomous request: {prompt[:50]}...")
            
            # Check if autonomous mode should be used
            if not self.should_use_autonomous_mode(prompt, context):
                return {
                    'success': False,
                    'error': 'Autonomous mode not triggered',
                    'provider': self.provider_name,
                    'fallback_reason': 'Simple query, no planning needed'
                }
            
            logger.info(f"Autonomous mode triggered for: {prompt[:30]}...")
            
            # Create execution plan
            try:
                plan = await agent_planner.create_plan(
                    goal=prompt,
                    client_id=client_id,
                    persona_id=persona_id,
                    context=context or {}
                )
                
                logger.info(f"Created plan {plan.plan_id} with {len(plan.steps)} steps")
                
            except Exception as e:
                logger.error(f"Failed to create plan: {e}")
                return {
                    'success': False,
                    'error': f'Planning failed: {str(e)}',
                    'provider': self.provider_name
                }
            
            # Execute the plan
            try:
                execution_result = await agent_planner.execute_plan(plan.plan_id)
                
                if execution_result['success']:
                    processing_time = (datetime.now() - start_time).total_seconds()
                    
                    # Log autonomous execution to working memory
                    await self._log_autonomous_execution(
                        client_id, persona_id, prompt, execution_result, request_id
                    )
                    
                    return {
                        'success': True,
                        'response': execution_result['final_response'],
                        'provider': self.provider_name,
                        'autonomous_execution': {
                            'plan_id': plan.plan_id,
                            'steps_executed': execution_result['steps_executed'],
                            'processing_time': processing_time,
                            'plan_summary': execution_result['plan_summary']
                        },
                        'metadata': {
                            'mode': 'autonomous',
                            'planning_strategy': plan.context.get('strategy', 'unknown'),
                            'total_steps': len(plan.steps)
                        }
                    }
                else:
                    logger.error(f"Plan execution failed: {execution_result.get('error')}")
                    return {
                        'success': False,
                        'error': f"Autonomous execution failed: {execution_result.get('error')}",
                        'provider': self.provider_name,
                        'plan_id': plan.plan_id
                    }
                    
            except Exception as e:
                logger.error(f"Plan execution error: {e}")
                return {
                    'success': False,
                    'error': f'Execution failed: {str(e)}',
                    'provider': self.provider_name
                }
        
        except Exception as e:
            logger.error(f"Autonomous provider error: {e}")
            return {
                'success': False,
                'error': f'Autonomous processing failed: {str(e)}',
                'provider': self.provider_name
            }
    
    async def _log_autonomous_execution(self, client_id: str, persona_id: str, 
                                       original_prompt: str, execution_result: Dict[str, Any],
                                       request_id: str = None):
        """Log autonomous execution to working memory"""
        try:
            # Create working memory entry about autonomous execution
            memory_content = f"Autonomous execution completed: {original_prompt[:100]}..."
            
            # Add execution details
            execution_summary = {
                'plan_id': execution_result.get('plan_id'),
                'steps_executed': execution_result.get('steps_executed'),
                'success': execution_result.get('success'),
                'request_id': request_id
            }
            
            # Store in working memory (this would need to be implemented in memory system)
            # For now, just log it
            logger.info(f"Autonomous execution logged: {execution_summary}")
            
        except Exception as e:
            logger.warning(f"Failed to log autonomous execution: {e}")
    
    def get_active_plans(self) -> List[Dict[str, Any]]:
        """Get list of active autonomous plans"""
        return agent_planner.list_active_plans()
    
    async def cancel_plan(self, plan_id: str) -> bool:
        """Cancel an active autonomous plan"""
        return await agent_planner.cancel_plan(plan_id)
    
    def get_plan_status(self, plan_id: str) -> Dict[str, Any]:
        """Get status of a specific plan"""
        return agent_planner.get_plan_status(plan_id)
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get autonomous provider statistics"""
        active_plans = self.get_active_plans()
        
        return {
            'provider': self.provider_name,
            'autonomous_mode_enabled': self.config['enable_autonomous_mode'],
            'active_plans': len(active_plans),
            'max_concurrent_plans': self.config['max_concurrent_plans'],
            'planning_timeout': self.config['planning_timeout'],
            'execution_timeout': self.config['execution_timeout']
        }


# Global instance for use across VALIS
autonomous_agent_provider = AutonomousAgentProvider()
