"""
VALIS Synthetic Cognition Layer
Agent self-awareness, emotion, and reflection modules
"""
from .self_model import AgentSelfModel
from .emotion_model import AgentEmotionModel
from .reflector import AgentReflector

__all__ = [
    'AgentSelfModel',
    'AgentEmotionModel', 
    'AgentReflector'
]
