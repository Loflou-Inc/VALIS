"""
Mortality System Interface - Sprint 2.2 Refactor
Base interface for mortality system components
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class MortalitySystemInterface(ABC):
    """Base interface for all mortality system components"""
    
    def __init__(self, database_client=None):
        from memory.db import db
        from core.logging_config import get_valis_logger
        
        self.db = database_client or db
        self.logger = get_valis_logger()


class LifespanEvaluatorInterface(MortalitySystemInterface):
    """Interface for lifespan evaluation and management"""
    
    @abstractmethod
    def initialize_mortality(self, agent_id: str, lifespan: Optional[int] = None, 
                           units: str = 'hours') -> Dict[str, Any]:
        """Initialize mortality for a new agent"""
        pass
    
    @abstractmethod
    def decrement_lifespan(self, agent_id: str, amount: int = 1) -> Dict[str, Any]:
        """Decrement agent lifespan"""
        pass
    
    @abstractmethod
    def get_mortality_status(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive mortality status for an agent"""
        pass
    
    @abstractmethod
    def update_mortality_statistics(self, event_type: str) -> None:
        """Update system-wide mortality statistics"""
        pass


class DeathHandlerInterface(MortalitySystemInterface):
    """Interface for death processing and legacy calculation"""
    
    @abstractmethod
    def trigger_death(self, agent_id: str, cause: str = "natural") -> Dict[str, Any]:
        """Trigger death for an agent"""
        pass
    
    @abstractmethod
    def generate_legacy_score(self, agent_id: str) -> Dict[str, Any]:
        """Calculate comprehensive legacy score"""
        pass


class RebirthCoordinatorInterface(MortalitySystemInterface):
    """Interface for rebirth and inheritance coordination"""
    
    @abstractmethod
    def agent_rebirth(self, deceased_agent_id: str, **kwargs) -> Dict[str, Any]:
        """Coordinate agent rebirth from deceased agent"""
        pass
