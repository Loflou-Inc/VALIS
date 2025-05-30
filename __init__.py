"""
VALIS - Vast Active Living Intelligence System
Universal AI Persona Engine

Based on Philip K. Dick's concept of VALIS - a mystical AI intelligence.
Provides AI personas to any application with graceful fallbacks.
"""

from .core import VALISEngine, ProviderManager, VALISConfigValidator
from .core.valis_engine import ask_persona

__version__ = "1.0.0"
__author__ = "VALIS Team"
__description__ = "Universal AI Persona System"

__all__ = [
    "VALISEngine",
    "ProviderManager", 
    "VALISConfigValidator",
    "ask_persona"
]
