"""
VALIS Synthetic Cognition Layer - AgentEmotionModel - REFACTORED FOR SPRINT 2.1
Emotion state management and memory tagging with NLP-backed analysis
"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from core.logging_config import get_valis_logger, log_emotion_classification
from core.exceptions import (
    EmotionClassificationError, 
    MemoryError, 
    DatabaseError
)
from core.emotion_parser import ValisEmotionParser
from core.emotion_taxonomy import EmotionCategory, EmotionMeasurement

class AgentEmotionModel:
    """Manages agent emotional states and emotion-weighted memory with NLP analysis"""
    
    def __init__(self, db_client):
        """Initialize with database client and NLP parser"""
        self.db = db_client
        self.logger = get_valis_logger()
        
        # Initialize NLP emotion parser
        try:
            self.emotion_parser = ValisEmotionParser()
            self.logger.info("NLP emotion parser initialized successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize NLP parser, falling back to legacy: {e}")
            self.emotion_parser = None
    def classify_emotion(self, transcript: str, tool_feedback: List[dict], session_id: str) -> dict:
        """
        Classify emotional state using NLP analysis and tool feedback
        
        Args:
            transcript: Session transcript text
            tool_feedback: List of tool execution results
            session_id: Current session identifier
            
        Returns:
            Dict with emotion classification results
        """
        if not transcript and not tool_feedback:
            raise EmotionClassificationError("Cannot classify emotion without transcript or tool feedback")
        
        if not session_id:
            raise EmotionClassificationError("Session ID is required for emotion classification")
        
        try:
            # Use NLP parser if available, otherwise fall back to legacy
            if self.emotion_parser and transcript:
                emotion_measurement = self._classify_with_nlp(transcript)
                
                # Adjust for tool feedback
                emotion_measurement = self._adjust_for_tool_feedback(emotion_measurement, tool_feedback)
                
                # Convert to legacy format for compatibility
                result = self._convert_to_legacy_format(emotion_measurement, session_id)
                
                # Log with accuracy metrics
                log_emotion_classification(
                    self.logger, 
                    session_id, 
                    emotion_measurement.primary_emotion.value,
                    confidence=emotion_measurement.confidence
                )
                
                # Log accuracy information
                self.logger.info(
                    "NLP emotion classification completed",
                    extra={
                        'session_id': session_id,
                        'primary_emotion': emotion_measurement.primary_emotion.value,
                        'intensity': emotion_measurement.intensity,
                        'confidence': emotion_measurement.confidence,
                        'valence': emotion_measurement.valence,
                        'arousal': emotion_measurement.arousal,
                        'secondary_emotions': len(emotion_measurement.secondary_emotions or []),
                        'context_tags': emotion_measurement.context_tags,
                        'method': 'nlp_analysis'
                    }
                )
                
                return result
            else:
                # Fall back to neutral state if no input to analyze
                self.logger.info(f"No valid input for emotion classification in session {session_id}, using neutral state")
                return self._get_neutral_emotion_state(session_id)
            
        except (TypeError, KeyError) as e:
            self.logger.error(
                "Invalid data structure in emotion classification", 
                extra={
                    'session_id': session_id,
                    'error': str(e),
                    'transcript_length': len(transcript) if transcript else 0,
                    'tool_feedback_count': len(tool_feedback) if tool_feedback else 0
                }
            )
            raise EmotionClassificationError(f"Invalid input data: {e}")
        except Exception as e:
            self.logger.critical(
                "Unexpected error in emotion classification",
                extra={
                    'session_id': session_id,
                    'error': str(e),
                    'operation': 'emotion_classification'
                }
            )
            raise
    def _classify_with_nlp(self, transcript: str) -> EmotionMeasurement:
        """Classify emotion using NLP parser"""
        return self.emotion_parser.parse_emotion(transcript)
    
    def _adjust_for_tool_feedback(self, emotion: EmotionMeasurement, tool_feedback: List[dict]) -> EmotionMeasurement:
        """Adjust emotion based on tool execution results"""
        if not tool_feedback:
            return emotion
        
        # Analyze tool feedback
        failed_tools = [t for t in tool_feedback if not t.get('success', True)]
        successful_tools = [t for t in tool_feedback if t.get('success', True)]
        
        # Adjust valence and arousal based on tool outcomes
        if failed_tools and not successful_tools:
            # All tools failed - increase negative valence and arousal
            emotion.valence = max(-1.0, emotion.valence - 0.3)
            emotion.arousal = min(1.0, emotion.arousal + 0.2)
            emotion.primary_emotion = EmotionCategory.FRUSTRATION
            if emotion.context_tags is None:
                emotion.context_tags = []
            emotion.context_tags.append("tool_failure")
            
        elif len(failed_tools) > len(successful_tools):
            # More failures than successes
            emotion.valence = max(-1.0, emotion.valence - 0.2)
            emotion.arousal = min(1.0, emotion.arousal + 0.1)
            if emotion.context_tags is None:
                emotion.context_tags = []
            emotion.context_tags.append("mixed_tool_results")
            
        elif successful_tools and not failed_tools:
            # All tools succeeded - boost positive emotions
            emotion.valence = min(1.0, emotion.valence + 0.2)
            if emotion.primary_emotion in [EmotionCategory.CONTENTMENT, EmotionCategory.JOY]:
                # Already positive, enhance it
                emotion.arousal = min(1.0, emotion.arousal + 0.1)
            if emotion.context_tags is None:
                emotion.context_tags = []
            emotion.context_tags.append("tool_success")
        
        return emotion
    
    def _convert_to_legacy_format(self, emotion: EmotionMeasurement, session_id: str) -> dict:
        """Convert EmotionMeasurement to legacy format for compatibility"""
        # Map new emotion categories to legacy mood strings
        legacy_mood_map = {
            EmotionCategory.JOY: "happy",
            EmotionCategory.EXCITEMENT: "excited",
            EmotionCategory.CONTENTMENT: "content",
            EmotionCategory.ANGER: "angry",
            EmotionCategory.FRUSTRATION: "frustrated",
            EmotionCategory.SADNESS: "sad",
            EmotionCategory.FEAR: "anxious",
            EmotionCategory.ANXIETY: "anxious",
            EmotionCategory.CONFUSION: "confused",
            EmotionCategory.CURIOSITY: "focused",
            EmotionCategory.DETERMINATION: "focused",
            EmotionCategory.TRUST: "calm",
            EmotionCategory.SURPRISE: "excited",
            EmotionCategory.DISGUST: "frustrated",
            EmotionCategory.ANTICIPATION: "focused",
            EmotionCategory.RELIEF: "calm"
        }
        
        legacy_mood = legacy_mood_map.get(emotion.primary_emotion, "neutral")
        arousal_level = int(emotion.arousal * 10)  # Convert to 0-10 scale
        
        # Build context tags from NLP analysis
        context_tags = emotion.context_tags or []
        if emotion.secondary_emotions:
            for sec_emotion, strength in emotion.secondary_emotions[:2]:  # Top 2 secondary
                context_tags.append(f"secondary_{sec_emotion.value}")
        
        return {
            "mood": legacy_mood,
            "arousal_level": arousal_level,
            "emotion_tags": context_tags,
            "session_id": session_id,
            # Extended fields for new system
            "nlp_confidence": emotion.confidence,
            "valence": emotion.valence,
            "primary_emotion": emotion.primary_emotion.value,
            "intensity": emotion.intensity
        }