"""
VALIS Emotion Taxonomy - Sprint 2.1
Comprehensive emotion classification system based on psychological research
"""
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

class EmotionCategory(Enum):
    """Primary emotion categories based on Plutchik's Wheel and Russell's Circumplex"""
    # Primary emotions (Plutchik)
    JOY = "joy"
    SADNESS = "sadness" 
    ANGER = "anger"
    FEAR = "fear"
    TRUST = "trust"
    DISGUST = "disgust"
    SURPRISE = "surprise"
    ANTICIPATION = "anticipation"
    
    # Extended emotions for AI context
    CONFUSION = "confusion"
    FRUSTRATION = "frustration"
    EXCITEMENT = "excitement"
    CONTENTMENT = "contentment"
    ANXIETY = "anxiety"
    CURIOSITY = "curiosity"
    DETERMINATION = "determination"
    RELIEF = "relief"

@dataclass
class EmotionMeasurement:
    """Structured emotion measurement with confidence and context"""
    primary_emotion: EmotionCategory
    intensity: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0 (parser confidence)
    valence: float    # -1.0 (negative) to 1.0 (positive)
    arousal: float    # 0.0 (calm) to 1.0 (energized)
    secondary_emotions: List[Tuple[EmotionCategory, float]] = None
    context_tags: List[str] = None

class ValisEmotionTaxonomy:
    """VALIS emotion taxonomy with Russell's Circumplex mapping and NLP integration"""
    
    # Russell's Circumplex Model mapping (valence, arousal)
    EMOTION_COORDINATES = {
        EmotionCategory.JOY: (0.8, 0.6),
        EmotionCategory.EXCITEMENT: (0.9, 0.9),
        EmotionCategory.SURPRISE: (0.0, 0.8),
        EmotionCategory.ANGER: (-0.6, 0.8),
        EmotionCategory.FEAR: (-0.7, 0.7),
        EmotionCategory.ANXIETY: (-0.5, 0.7),
        EmotionCategory.SADNESS: (-0.8, 0.3),
        EmotionCategory.DISGUST: (-0.7, 0.4),
        EmotionCategory.TRUST: (0.6, 0.3),
        EmotionCategory.CONTENTMENT: (0.7, 0.2),
        EmotionCategory.ANTICIPATION: (0.4, 0.6),
        EmotionCategory.CURIOSITY: (0.3, 0.5),
        EmotionCategory.CONFUSION: (-0.2, 0.4),
        EmotionCategory.FRUSTRATION: (-0.6, 0.7),
        EmotionCategory.DETERMINATION: (0.3, 0.8),
        EmotionCategory.RELIEF: (0.5, 0.1)
    }
    
    @classmethod
    def get_valence_arousal(cls, emotion: EmotionCategory) -> Tuple[float, float]:
        """Get valence and arousal coordinates for an emotion"""
        return cls.EMOTION_COORDINATES.get(emotion, (0.0, 0.5))
    
    @classmethod
    def emotion_from_valence_arousal(cls, valence: float, arousal: float) -> EmotionCategory:
        """Find closest emotion based on valence/arousal coordinates"""
        min_distance = float('inf')
        closest_emotion = EmotionCategory.CONTENTMENT
        
        for emotion, (v, a) in cls.EMOTION_COORDINATES.items():
            distance = ((valence - v) ** 2 + (arousal - a) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_emotion = emotion
        
        return closest_emotion
    
    @classmethod
    def get_emotion_intensity(cls, valence: float, arousal: float) -> float:
        """Calculate emotion intensity from valence/arousal magnitude"""
        return min(1.0, (abs(valence) + arousal) / 2.0)
    # Keyword mappings for emotion detection
    EMOTION_KEYWORDS = {
        EmotionCategory.JOY: [
            "happy", "joyful", "delighted", "pleased", "cheerful", "elated",
            "ecstatic", "blissful", "glad", "satisfied", "wonderful", "amazing"
        ],
        EmotionCategory.EXCITEMENT: [
            "excited", "thrilled", "exhilarated", "energetic", "pumped",
            "enthusiastic", "eager", "passionate", "fired up"
        ],
        EmotionCategory.ANGER: [
            "angry", "furious", "mad", "irritated", "annoyed", "outraged",
            "livid", "enraged", "heated", "pissed", "frustrated"
        ],
        EmotionCategory.FEAR: [
            "afraid", "scared", "terrified", "frightened", "worried",
            "nervous", "apprehensive", "alarmed", "panicked"
        ],
        EmotionCategory.SADNESS: [
            "sad", "depressed", "melancholy", "grief", "sorrow", "glum",
            "downhearted", "dejected", "mournful", "blue"
        ],
        EmotionCategory.SURPRISE: [
            "surprised", "astonished", "amazed", "shocked", "stunned",
            "bewildered", "startled", "unexpected"
        ],
        EmotionCategory.TRUST: [
            "trust", "confident", "secure", "reliable", "faith",
            "believe", "dependable", "assured"
        ],
        EmotionCategory.DISGUST: [
            "disgusted", "revolted", "repulsed", "sickened", "nauseated",
            "appalled", "horrified"
        ],
        EmotionCategory.ANTICIPATION: [
            "anticipating", "expecting", "hopeful", "optimistic",
            "looking forward", "awaiting"
        ],
        EmotionCategory.CONFUSION: [
            "confused", "puzzled", "perplexed", "baffled", "unclear",
            "uncertain", "lost", "bewildered"
        ],
        EmotionCategory.FRUSTRATION: [
            "frustrated", "annoyed", "irritated", "vexed", "aggravated",
            "exasperated", "stuck", "blocked"
        ],
        EmotionCategory.ANXIETY: [
            "anxious", "worried", "stressed", "tense", "uneasy",
            "restless", "troubled", "concerned"
        ],
        EmotionCategory.CURIOSITY: [
            "curious", "interested", "intrigued", "wondering",
            "questioning", "exploring", "investigating"
        ],
        EmotionCategory.CONTENTMENT: [
            "content", "peaceful", "calm", "serene", "tranquil",
            "relaxed", "satisfied", "at ease"
        ],
        EmotionCategory.DETERMINATION: [
            "determined", "focused", "driven", "motivated", "resolved",
            "committed", "persistent", "dedicated"
        ],
        EmotionCategory.RELIEF: [
            "relieved", "grateful", "thankful", "unburdened",
            "reassured", "comforted"
        ]
    }