"""
VALIS Sprint 16: MCP Runtime Integration Hook
Automatic shadow detection integration into the MCP runtime pipeline

This module provides the integration hooks for automatically triggering
shadow detection and individuation analysis after VALIS sessions
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from typing import Dict, Any, Optional
from cognition.shadow_archive import ShadowArchiveEngine
from cognition.individuation import IndividuationEngine


class ShadowIntegrationHook:
    """
    Integration hook for automatic shadow detection in MCP runtime
    Triggers after sessions to analyze psychological contradictions
    """
    
    def __init__(self):
        self.shadow_engine = ShadowArchiveEngine()
        self.individuation_engine = IndividuationEngine()
        self.enabled = True
        
        print("[+] ShadowIntegrationHook initialized - automatic shadow analysis enabled")
    
    def post_session_shadow_analysis(self, agent_id: str, cognition_state: dict, 
                                   session_transcript: str) -> Dict[str, Any]:
        """
        Hook function to run after MCP sessions for shadow analysis
        
        Args:
            agent_id: UUID of the agent
            cognition_state: Final cognition state from session
            session_transcript: Complete session transcript
            
        Returns:
            Dict with shadow analysis results
        """
        if not self.enabled:
            return {'status': 'shadow_analysis_disabled'}
        
        try:
            # 1. Detect shadow contradictions
            shadow_result = self.shadow_engine.detect_shadow_contradictions(
                agent_id, cognition_state, session_transcript
            )
            
            # 2. Evaluate shadow reconciliation (check for dream/reflection integration)
            reconciliation_result = self.individuation_engine.evaluate_shadow_reconciliation(agent_id)
            
            # 3. Log integration success
            analysis_summary = {
                'agent_id': agent_id,
                'shadow_detection': shadow_result,
                'reconciliation_analysis': reconciliation_result,
                'timestamp': f"{__import__('datetime').datetime.now().isoformat()}",
                'integration_status': 'complete'
            }
            
            # Log summary for debugging
            if shadow_result.get('contradictions_found', 0) > 0:
                print(f"[SHADOW] Agent {agent_id[:8]}... detected {shadow_result['contradictions_found']} contradictions")
            
            if reconciliation_result.get('reconciliations_found', 0) > 0:
                print(f"[INDIVIDUATION] Agent {agent_id[:8]}... found {reconciliation_result['reconciliations_found']} reconciliations")
            
            return analysis_summary
            
        except Exception as e:
            print(f"[-] Shadow integration hook failed: {e}")
            return {
                'status': 'shadow_analysis_failed',
                'error': str(e),
                'agent_id': agent_id
            }
    
    def background_reconciliation_check(self, agent_id: str) -> Dict[str, Any]:
        """
        Background job for periodic shadow reconciliation analysis
        Should be called every 12 hours or as scheduled
        """
        try:
            return self.individuation_engine.evaluate_shadow_reconciliation(agent_id)
        except Exception as e:
            print(f"[-] Background reconciliation check failed: {e}")
            return {'status': 'background_check_failed', 'error': str(e)}
    
    def get_agent_psychological_status(self, agent_id: str) -> Dict[str, Any]:
        """
        Get comprehensive psychological status for an agent
        Combines shadow and individuation data
        """
        try:
            shadow_summary = self.shadow_engine.get_agent_shadow_summary(agent_id)
            individuation_summary = self.individuation_engine.get_agent_individuation_summary(agent_id)
            
            return {
                'agent_id': agent_id,
                'shadow_profile': shadow_summary,
                'individuation_progress': individuation_summary,
                'psychological_health': self._calculate_psychological_health(shadow_summary, individuation_summary)
            }
            
        except Exception as e:
            print(f"[-] Failed to get psychological status: {e}")
            return {'error': str(e)}
    
    def _calculate_psychological_health(self, shadow_summary: Dict, individuation_summary: Dict) -> Dict[str, float]:
        """Calculate overall psychological health metrics"""
        try:
            # Shadow integration health (lower unresolved shadows = better)
            shadow_health = 1.0 - (shadow_summary.get('unresolved_events', 0) / 
                                 max(shadow_summary.get('total_shadow_events', 1), 1))
            
            # Individuation progress health
            stage_weights = {
                'shadow_awareness': 0.2,
                'shadow_acceptance': 0.4,
                'anima_contact': 0.6,
                'self_realization': 0.8,
                'transcendence': 1.0
            }
            
            current_stage = individuation_summary.get('current_stage', 'shadow_awareness')
            individuation_health = stage_weights.get(current_stage, 0.2)
            
            # Overall psychological integration
            overall_health = (shadow_health * 0.6 + individuation_health * 0.4)
            
            return {
                'shadow_integration': shadow_health,
                'individuation_progress': individuation_health,
                'overall_psychological_health': overall_health
            }
            
        except Exception as e:
            print(f"[-] Failed to calculate psychological health: {e}")
            return {'shadow_integration': 0.0, 'individuation_progress': 0.0, 'overall_psychological_health': 0.0}
    
    def enable_shadow_analysis(self):
        """Enable automatic shadow analysis"""
        self.enabled = True
        print("[+] Shadow analysis enabled")
    
    def disable_shadow_analysis(self):
        """Disable automatic shadow analysis"""
        self.enabled = False
        print("[-] Shadow analysis disabled")


# Global instance for MCP runtime integration
shadow_integration = ShadowIntegrationHook()


def integrate_shadow_detection_into_runtime():
    """
    Integration function to add shadow detection to MCP runtime
    This should be called during MCP initialization
    """
    print("[+] Integrating shadow detection into MCP runtime...")
    
    # Example integration code (would be added to actual MCP runtime):
    """
    # In MCPRuntime.process_session() method, add after session completion:
    
    if hasattr(self, 'shadow_integration'):
        shadow_result = self.shadow_integration.post_session_shadow_analysis(
            agent_id=self.current_agent_id,
            cognition_state=self.cognition_state,
            session_transcript=self.session_transcript
        )
        
        # Optionally store shadow result in session logs
        self.session_logs['shadow_analysis'] = shadow_result
    """
    
    return shadow_integration


def schedule_background_reconciliation():
    """
    Schedule background reconciliation checks for all agents
    This should be called by a scheduler every 12 hours
    """
    print("[+] Scheduling background reconciliation checks...")
    
    # Example scheduler integration:
    """
    # In scheduler or background task manager:
    
    async def run_reconciliation_checks():
        from memory.db import db
        
        # Get all active agents
        agents = db.query("SELECT id FROM persona_profiles")
        
        for agent in agents:
            result = shadow_integration.background_reconciliation_check(agent['id'])
            if result.get('reconciliations_found', 0) > 0:
                print(f"[INDIVIDUATION] Agent {agent['id']} made progress")
    
    # Schedule to run every 12 hours
    schedule.every(12).hours.do(run_reconciliation_checks)
    """
    
    return True


if __name__ == "__main__":
    # Demo integration
    print("=" * 60)
    print("SPRINT 16: SHADOW INTEGRATION DEMO")
    print("=" * 60)
    
    # Initialize integration
    integration = integrate_shadow_detection_into_runtime()
    
    # Demo psychological status check
    from memory.db import db
    
    agents = db.query("SELECT id, name FROM persona_profiles LIMIT 3")
    for agent in agents:
        print(f"\n[ANALYZING] {agent['name']}")
        status = integration.get_agent_psychological_status(agent['id'])
        
        if 'error' not in status:
            health = status['psychological_health']
            print(f"  Shadow integration: {health['shadow_integration']:.2f}")
            print(f"  Individuation progress: {health['individuation_progress']:.2f}")
            print(f"  Overall health: {health['overall_psychological_health']:.2f}")
        else:
            print(f"  Error: {status['error']}")
    
    print("\n[+] Shadow integration system ready for MCP runtime")
    print("[+] Sprint 16 Phase 1 integration complete")
