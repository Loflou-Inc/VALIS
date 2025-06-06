"""
VALIS Sprint 17: Consolidation Task Runner
Scheduled background tasks for automatic memory consolidation

This module implements the periodic consolidation jobs that run every 12 hours
to consolidate psychological experiences into symbolic memories
"""
import sys
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any

sys.path.append(str(Path(__file__).parent.parent))

from memory.db import db
from memory.consolidation import MemoryConsolidationEngine


class ConsolidationRunner:
    """
    Background task runner for memory consolidation
    Handles scheduled consolidation sweeps for all active agents
    """
    
    def __init__(self):
        self.consolidation_engine = MemoryConsolidationEngine()
        self.last_run = None
        self.consolidation_interval_hours = 12
        
        print("[+] ConsolidationRunner initialized - automatic consolidation scheduled")
    
    def should_run_consolidation(self) -> bool:
        """Check if it's time to run consolidation"""
        if self.last_run is None:
            return True
        
        time_since_last = datetime.now() - self.last_run
        return time_since_last.total_seconds() >= (self.consolidation_interval_hours * 3600)
    
    def get_active_agents(self) -> List[Dict]:
        """Get list of active agents eligible for consolidation"""
        try:
            # Get agents that have recent psychological activity
            cutoff_date = datetime.now() - timedelta(days=7)
            
            agents = db.query("""
                SELECT DISTINCT pp.id, pp.name 
                FROM persona_profiles pp
                WHERE EXISTS (
                    SELECT 1 FROM unconscious_log ul 
                    WHERE ul.agent_id = pp.id AND ul.timestamp > %s
                ) OR EXISTS (
                    SELECT 1 FROM agent_reflection_log arl 
                    WHERE arl.persona_id = pp.id AND arl.created_at > %s
                ) OR EXISTS (
                    SELECT 1 FROM shadow_events se 
                    WHERE se.agent_id = pp.id AND se.timestamp > %s
                )
                ORDER BY pp.name
            """, (cutoff_date, cutoff_date, cutoff_date))
            
            return agents
            
        except Exception as e:
            print(f"[-] Failed to get active agents: {e}")
            return []
    
    def run_consolidation_sweep(self) -> Dict[str, Any]:
        """Run consolidation for all eligible agents"""
        try:
            print(f"[+] Starting consolidation sweep at {datetime.now()}")
            
            active_agents = self.get_active_agents()
            if not active_agents:
                return {
                    'status': 'no_active_agents',
                    'timestamp': datetime.now().isoformat(),
                    'agents_processed': 0
                }
            
            sweep_results = {
                'status': 'consolidation_sweep_complete',
                'timestamp': datetime.now().isoformat(),
                'agents_processed': len(active_agents),
                'total_memories_consolidated': 0,
                'total_narratives_compressed': 0,
                'agent_results': []
            }
            
            for agent in active_agents:
                agent_id = agent['id']
                agent_name = agent['name']
                
                print(f"[+] Consolidating memories for {agent_name} ({agent_id[:8]}...)")
                
                # Run consolidation for this agent
                consolidation_result = self.consolidation_engine.consolidate_agent_memories(agent_id)
                
                # Add to sweep results
                agent_summary = {
                    'agent_id': agent_id,
                    'agent_name': agent_name,
                    'memories_consolidated': consolidation_result.get('symbolic_memories_created', 0),
                    'narratives_compressed': consolidation_result.get('narrative_compressions', 0),
                    'total_resonance': consolidation_result.get('total_resonance', 0.0)
                }
                
                sweep_results['agent_results'].append(agent_summary)
                sweep_results['total_memories_consolidated'] += agent_summary['memories_consolidated']
                sweep_results['total_narratives_compressed'] += agent_summary['narratives_compressed']
            
            # Update last run time
            self.last_run = datetime.now()
            
            print(f"[+] Consolidation sweep complete:")
            print(f"    Agents processed: {sweep_results['agents_processed']}")
            print(f"    Total memories consolidated: {sweep_results['total_memories_consolidated']}")
            print(f"    Total narratives compressed: {sweep_results['total_narratives_compressed']}")
            
            return sweep_results
            
        except Exception as e:
            print(f"[-] Consolidation sweep failed: {e}")
            return {
                'status': 'consolidation_sweep_failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
