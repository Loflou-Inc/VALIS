"""
VALIS Synthetic Cognition Manager
"""
import json
import logging
from typing import Dict, Any
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from memory.db import db
from agents.self_model import AgentSelfModel
from agents.emotion_model import AgentEmotionModel
from agents.reflector import AgentReflector

logger = logging.getLogger(__name__)

class SyntheticCognitionManager:
    """Manages the three synthetic cognition modules"""
    
    def __init__(self):
        self.self_model = AgentSelfModel(db)
        self.emotion_model = AgentEmotionModel(db)
        self.reflector = AgentReflector(db)
        logger.info("Synthetic Cognition Manager initialized")
    
    def get_cognition_state(self, persona_id: str, session_id: str) -> Dict[str, Any]:
        """Get complete cognition state for prompt injection"""
        try:
            self_state = self.self_model.export_state_blob(persona_id)
            emotion_state = self.emotion_model.export_emotion_state(session_id)
            
            cognition_state = {
                "self": self_state,
                "emotion": emotion_state,
                "integration": {
                    "confidence_adjusted": self._adjust_confidence(
                        self_state.get('confidence', 0.5),
                        emotion_state.get('mood', 'neutral')
                    ),
                    "awareness_text": self._generate_awareness_text(self_state, emotion_state)
                }
            }
            return cognition_state
        except Exception as e:
            logger.error(f"Error getting cognition state: {e}")
            return {
                "self": {"confidence": 0.5, "alignment_score": 0.5},
                "emotion": {"mood": "neutral", "arousal_level": 5},
                "integration": {"confidence_adjusted": 0.5, "awareness_text": "Processing..."}
            }
    
    def _adjust_confidence(self, base_confidence: float, mood: str) -> float:
        """Adjust confidence based on emotional state"""
        if mood in ["excited", "happy", "focused"]:
            return min(base_confidence + 0.1, 1.0)
        elif mood in ["frustrated", "confused", "stressed"]:
            return max(base_confidence - 0.15, 0.0)
        return base_confidence
    
    def _generate_awareness_text(self, self_state: Dict, emotion_state: Dict) -> str:
        """Generate natural language awareness text"""
        confidence = self_state.get('confidence', 0.5)
        mood = emotion_state.get('mood', 'neutral')
        
        if confidence > 0.8 and mood in ["happy", "excited", "focused"]:
            return "I'm feeling confident and engaged with our conversation."
        elif confidence < 0.4 or mood in ["frustrated", "stressed"]:
            return "I'm working through some challenges but staying focused on helping you."
        else:
            return "I'm feeling balanced and ready to assist you effectively."
