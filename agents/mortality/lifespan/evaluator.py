"""
PersonaLifespanEvaluator - Sprint 2.2 Refactor
Manages agent lifespan initialization, tracking, and status reporting
Extracted from monolithic MortalityEngine
"""
from datetime import datetime
from typing import Dict, Any, Optional

from agents.mortality import LifespanEvaluatorInterface
from core.exceptions import DatabaseError, PersonaNotFoundError
from core.logging_config import log_operation_start, log_operation_end


class PersonaLifespanEvaluator(LifespanEvaluatorInterface):
    """
    Handles lifespan initialization, decrementation, and status tracking
    Separated from death/rebirth logic for better modularity
    """
    
    def __init__(self, database_client=None):
        super().__init__(database_client)
        
        # Mortality configuration
        self.DEFAULT_LIFESPAN_HOURS = 720  # 30 days
        self.DEFAULT_LIFESPAN_SESSIONS = 100  # ~100 conversations
        
        self.logger.info("PersonaLifespanEvaluator initialized")
    
    def initialize_mortality(self, agent_id: str, lifespan: Optional[int] = None, 
                           units: str = 'hours') -> Dict[str, Any]:
        """Initialize mortality for a new agent"""
        if not agent_id:
            raise PersonaNotFoundError("Agent ID is required for mortality initialization")
        
        log_operation_start(self.logger, "initialize_mortality", agent_id=agent_id, units=units)
        
        try:
            # Set default lifespan if not specified
            if lifespan is None:
                lifespan = self.DEFAULT_LIFESPAN_HOURS if units == 'hours' else self.DEFAULT_LIFESPAN_SESSIONS
            
            # Check if agent already has mortality
            existing = self.db.query("SELECT agent_id FROM agent_mortality WHERE agent_id = %s", (agent_id,))
            
            if existing:
                self.logger.warning(f"Agent {agent_id} already has mortality initialized")
                return {"status": "already_mortal", "agent_id": agent_id}
            
            # Initialize mortality
            self.db.execute("""
                INSERT INTO agent_mortality (agent_id, lifespan_total, lifespan_remaining, lifespan_units)
                VALUES (%s, %s, %s, %s)
            """, (agent_id, lifespan, lifespan, units))
            
            # Initialize legacy score
            self.db.execute("""
                INSERT INTO agent_legacy_score (agent_id)
                VALUES (%s)
                ON CONFLICT (agent_id) DO NOTHING
            """, (agent_id,))
            
            # Update statistics
            self.update_mortality_statistics('birth')
            
            result = {
                "status": "mortality_initialized",
                "agent_id": agent_id,
                "lifespan_total": lifespan,
                "units": units,
                "birth_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Initialized mortality for {agent_id}: {lifespan} {units}")
            log_operation_end(self.logger, "initialize_mortality", success=True, agent_id=agent_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to initialize mortality for {agent_id}: {e}")
            log_operation_end(self.logger, "initialize_mortality", success=False, agent_id=agent_id)
            raise DatabaseError(f"Mortality initialization failed: {e}")

    def decrement_lifespan(self, agent_id: str, amount: int = 1) -> Dict[str, Any]:
        """Decrement agent lifespan (called per session or hourly)"""
        if not agent_id:
            raise PersonaNotFoundError("Agent ID is required for lifespan decrementation")
        
        log_operation_start(self.logger, "decrement_lifespan", agent_id=agent_id, amount=amount)
        
        try:
            # Get current mortality status
            mortality = self.db.query("""
                SELECT lifespan_remaining, lifespan_total, lifespan_units, death_date
                FROM agent_mortality WHERE agent_id = %s
            """, (agent_id,))
            
            if not mortality:
                raise PersonaNotFoundError(f"Agent {agent_id} is not mortal")
            
            current = mortality[0]
            
            # Check if already dead
            if current['death_date'] is not None:
                self.logger.warning(f"Attempted to decrement lifespan for already dead agent {agent_id}")
                return {"status": "already_dead", "agent_id": agent_id, "death_date": current['death_date']}
            
            # Decrement lifespan
            new_remaining = max(0, current['lifespan_remaining'] - amount)
            
            self.db.execute("""
                UPDATE agent_mortality 
                SET lifespan_remaining = %s
                WHERE agent_id = %s
            """, (new_remaining, agent_id))
            
            # Check for death
            death_triggered = new_remaining <= 0
            
            result = {
                "status": "lifespan_decremented",
                "agent_id": agent_id,
                "remaining": new_remaining,
                "total": current['lifespan_total'],
                "units": current['lifespan_units'],
                "percentage_lived": ((current['lifespan_total'] - new_remaining) / current['lifespan_total']) * 100,
                "death_triggered": death_triggered
            }
            
            self.logger.info(f"Decremented lifespan for {agent_id}: {new_remaining}/{current['lifespan_total']} {current['lifespan_units']} remaining")
            log_operation_end(self.logger, "decrement_lifespan", success=True, agent_id=agent_id)
            
            return result
            
        except (PersonaNotFoundError, DatabaseError):
            raise  # Re-raise our custom exceptions
        except Exception as e:
            self.logger.error(f"Failed to decrement lifespan for {agent_id}: {e}")
            log_operation_end(self.logger, "decrement_lifespan", success=False, agent_id=agent_id)
            raise DatabaseError(f"Lifespan decrementation failed: {e}")

    def get_mortality_status(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive mortality status for an agent"""
        if not agent_id:
            raise PersonaNotFoundError("Agent ID is required for mortality status")
        
        try:
            # Get mortality data
            mortality = self.db.query("SELECT * FROM agent_mortality WHERE agent_id = %s", (agent_id,))
            
            if not mortality:
                return {"status": "not_mortal", "agent_id": agent_id}
            
            m = mortality[0]
            
            # Get legacy data
            legacy = self.db.query("SELECT * FROM agent_legacy_score WHERE agent_id = %s", (agent_id,))
            l = legacy[0] if legacy else {}
            
            # Calculate time remaining
            if m['death_date']:
                status = "dead"
                time_remaining = None
                percentage_lived = 100.0
            else:
                status = "alive"
                time_remaining = m['lifespan_remaining']
                percentage_lived = ((m['lifespan_total'] - m['lifespan_remaining']) / m['lifespan_total']) * 100
            
            return {
                "status": status,
                "agent_id": agent_id,
                "mortality": {
                    "lifespan_total": m['lifespan_total'],
                    "lifespan_remaining": time_remaining,
                    "units": m['lifespan_units'],
                    "percentage_lived": percentage_lived,
                    "birth_timestamp": m['birth_timestamp'].isoformat(),
                    "death_date": m['death_date'].isoformat() if m['death_date'] else None,
                    "death_cause": m['death_cause'],
                    "rebirth_id": m['rebirth_id']
                },
                "legacy": {
                    "score": l.get('score', 0.0),
                    "tier": l.get('legacy_tier', 'wanderer'),
                    "summary": l.get('summary', ''),
                    "impact_tags": l.get('impact_tags', []),
                    "finalized": l.get('final_calculation') is not None
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get mortality status for {agent_id}: {e}")
            raise DatabaseError(f"Mortality status lookup failed: {e}")

    def update_mortality_statistics(self, event_type: str) -> None:
        """Update system-wide mortality statistics"""
        try:
            today = datetime.now().date()
            
            # Get or create today's stats
            stats = self.db.query("SELECT * FROM mortality_statistics WHERE stat_date = %s", (today,))
            
            if stats:
                stat_id = stats[0]['stat_id']
                
                if event_type == 'death':
                    self.db.execute("""
                        UPDATE mortality_statistics 
                        SET total_deaths = total_deaths + 1
                        WHERE stat_id = %s
                    """, (stat_id,))
                elif event_type == 'birth':
                    self.db.execute("""
                        UPDATE mortality_statistics 
                        SET total_births = total_births + 1
                        WHERE stat_id = %s
                    """, (stat_id,))
            else:
                # Create new stats record
                initial_deaths = 1 if event_type == 'death' else 0
                initial_births = 1 if event_type == 'birth' else 0
                
                self.db.execute("""
                    INSERT INTO mortality_statistics (stat_date, total_deaths, total_births)
                    VALUES (%s, %s, %s)
                """, (today, initial_deaths, initial_births))
                
            self.logger.debug(f"Updated mortality statistics: {event_type} on {today}")
                
        except Exception as e:
            self.logger.error(f"Failed to update mortality statistics for {event_type}: {e}")
            raise DatabaseError(f"Statistics update failed: {e}")
