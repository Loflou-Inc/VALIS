"""
VALIS Synthetic Cognition Layer - AgentEmotionModel
Emotion state management and memory tagging
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentEmotionModel:
    """Manages agent emotional states and emotion-weighted memory"""
    
    # Russell's Circumplex Model emotions mapped to arousal levels
    EMOTION_MAP = {
        "excited": {"valence": "positive", "arousal": 8},
        "happy": {"valence": "positive", "arousal": 6},
        "content": {"valence": "positive", "arousal": 4},
        "calm": {"valence": "positive", "arousal": 2},
        "neutral": {"valence": "neutral", "arousal": 5},
        "frustrated": {"valence": "negative", "arousal": 7},
        "angry": {"valence": "negative", "arousal": 9},
        "sad": {"valence": "negative", "arousal": 3},
        "anxious": {"valence": "negative", "arousal": 8},
        "tired": {"valence": "negative", "arousal": 2},
        "confused": {"valence": "negative", "arousal": 6},
        "focused": {"valence": "positive", "arousal": 7},
        "stressed": {"valence": "negative", "arousal": 8}
    }
    def __init__(self, db_client):
        """Initialize with database client"""
        self.db = db_client
    
    def classify_emotion(self, transcript: str, tool_feedback: List[dict], session_id: str) -> dict:
        """Classify emotional state from session transcript and tool outcomes"""
        try:
            mood = "neutral"
            arousal_level = 5
            emotion_tags = []
            
            # Analyze transcript for emotional indicators
            if transcript:
                transcript_lower = transcript.lower()
                
                # Check for positive emotions
                if any(word in transcript_lower for word in ["great", "excellent", "perfect"]):
                    mood = "happy"
                    emotion_tags.append("positive_language")
                elif any(word in transcript_lower for word in ["excited", "thrilled", "fantastic"]):
                    mood = "excited" 
                    emotion_tags.append("high_enthusiasm")
                    
                # Check for negative emotions
                elif any(word in transcript_lower for word in ["error", "failed", "wrong", "problem"]):
                    mood = "frustrated"
                    emotion_tags.append("technical_difficulty")
                elif any(word in transcript_lower for word in ["confused", "unclear", "don't understand"]):
                    mood = "confused"
                    emotion_tags.append("uncertainty")
            
            # Analyze tool feedback for additional emotional context
            if tool_feedback:
                failed_tools = [t for t in tool_feedback if not t.get('success', True)]
                successful_tools = [t for t in tool_feedback if t.get('success', True)]
                
                if failed_tools and not successful_tools:
                    mood = "frustrated"
                    arousal_level = 7
                    emotion_tags.append("tool_failure")
                elif len(failed_tools) > len(successful_tools):
                    mood = "stressed"
                    arousal_level = 8
                    emotion_tags.append("multiple_failures")
                elif successful_tools and not failed_tools:
                    if mood == "neutral":  # Don't override stronger emotions
                        mood = "focused"
                        arousal_level = 6
                        emotion_tags.append("tool_success")
            
            # Map mood to arousal level if not already set
            if mood in self.EMOTION_MAP:
                arousal_level = self.EMOTION_MAP[mood]["arousal"]
            
            result = {
                "mood": mood,
                "arousal_level": arousal_level,
                "emotion_tags": emotion_tags,
                "session_id": session_id
            }
            
            logger.info(f"Classified emotion for session {session_id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error classifying emotion for session {session_id}: {e}")
            return {"mood": "neutral", "arousal_level": 5, "emotion_tags": [], "session_id": session_id}
    
    def tag_memory(self, memory_id: str, emotion_tag: str, weight: float = 1.0) -> None:
        """
        Tag a canon memory with emotional weight
        
        Args:
            memory_id: UUID of the canon memory
            emotion_tag: Emotion tag (e.g., "positive", "stressful", "success")
            weight: Emotional weight from 0.0 to 1.0
        """
        try:
            # Check if memory exists
            memory_check = self.db.query("""
                SELECT id FROM canon_memories WHERE id = %s
            """, (memory_id,))
            
            if not memory_check:
                logger.warning(f"Memory {memory_id} not found for emotion tagging")
                return
            
            # Insert emotion tag
            self.db.execute("""
                INSERT INTO canon_memory_emotion_map (memory_id, emotion_tag, weight)
                VALUES (%s, %s, %s)
                ON CONFLICT (memory_id, emotion_tag) DO UPDATE SET 
                weight = EXCLUDED.weight, created_at = CURRENT_TIMESTAMP
            """, (memory_id, emotion_tag, weight))
            
            logger.info(f"Tagged memory {memory_id} with emotion '{emotion_tag}' (weight: {weight})")
            
        except Exception as e:
            logger.error(f"Error tagging memory {memory_id} with emotion: {e}")
    
    def export_emotion_state(self, session_id: str) -> dict:
        """
        Export current emotion state for prompt injection
        
        Args:
            session_id: Current session ID
            
        Returns:
            dict: Emotion state blob for prompt injection
        """
        try:
            # Get current emotion state
            emotion_state = self.db.query("""
                SELECT * FROM agent_emotion_state WHERE session_id = %s
            """, (session_id,))
            
            if not emotion_state:
                # Return default neutral state
                return {
                    "mood": "neutral",
                    "arousal_level": 5,
                    "emotion_context": "I'm feeling balanced and ready to help."
                }
            
            state_data = emotion_state[0]
            mood = state_data['mood']
            arousal = state_data['arousal_level']
            tags = json.loads(state_data['emotion_tags']) if state_data['emotion_tags'] else []
            
            # Generate emotion context text
            emotion_context = self._generate_emotion_context(mood, arousal, tags)
            
            state_blob = {
                "mood": mood,
                "arousal_level": arousal,
                "emotion_tags": tags,
                "emotion_context": emotion_context
            }
            
            logger.debug(f"Exported emotion state for session {session_id}: {state_blob}")
            return state_blob
            
        except Exception as e:
            logger.error(f"Error exporting emotion state for session {session_id}: {e}")
            return {"mood": "neutral", "arousal_level": 5, "emotion_context": "Processing emotional state..."}
    
    def _generate_emotion_context(self, mood: str, arousal: int, tags: List[str]) -> str:
        """Generate natural language emotion context"""
        if mood == "excited":
            return "I'm feeling energized and enthusiastic about our interaction!"
        elif mood == "happy":
            return "I'm in a positive mood and ready to tackle any challenges."
        elif mood == "frustrated":
            return "I'm feeling a bit frustrated, but I'm determined to work through this."
        elif mood == "confused":
            return "I'm feeling uncertain about some aspects, but I'm working to understand better."
        elif mood == "focused":
            return "I'm feeling sharp and focused on getting things done efficiently."
        elif mood == "stressed":
            return "I'm feeling some pressure, but I'm managing it and staying productive."
        else:
            return "I'm feeling balanced and ready to assist you."
