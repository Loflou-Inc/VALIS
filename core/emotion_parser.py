"""
VALIS NLP Emotion Parser - Sprint 2.1
Advanced emotion analysis using spaCy and transformer models
"""
import spacy
from typing import List, Dict, Tuple, Optional
import re
from collections import Counter

from core.emotion_taxonomy import (
    EmotionCategory, 
    EmotionMeasurement, 
    ValisEmotionTaxonomy
)
from core.logging_config import get_valis_logger
from core.exceptions import EmotionClassificationError

class ValisEmotionParser:
    """
    Advanced NLP-backed emotion parser for VALIS cognitive system
    Replaces primitive regex-based emotion detection with proper linguistic analysis
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.logger = get_valis_logger()
        self.model_name = model_name
        
        try:
            self.nlp = spacy.load(model_name)
            self.logger.info(f"Loaded spaCy model: {model_name}")
        except IOError as e:
            self.logger.error(f"Failed to load spaCy model {model_name}: {e}")
            raise EmotionClassificationError(
                f"spaCy model '{model_name}' not found. "
                f"Install with: python -m spacy download {model_name}"
            )
        
        # Sentiment polarity indicators (more sophisticated than keywords)
        self.sentiment_patterns = self._build_sentiment_patterns()
        
        # Emotional intensifiers and dampeners
        self.intensifiers = ["very", "extremely", "incredibly", "absolutely", "totally", "completely"]
        self.dampeners = ["slightly", "somewhat", "a bit", "kind of", "sort of", "rather"]
    def _build_sentiment_patterns(self) -> Dict[str, float]:
        """Build sophisticated sentiment patterns beyond simple keywords"""
        return {
            # Positive patterns
            "love": 0.8, "amazing": 0.9, "fantastic": 0.9, "wonderful": 0.8,
            "excellent": 0.7, "great": 0.6, "good": 0.5, "nice": 0.4,
            "enjoy": 0.6, "happy": 0.7, "excited": 0.8, "thrilled": 0.9,
            "delighted": 0.8, "pleased": 0.6, "satisfied": 0.5,
            
            # Negative patterns  
            "hate": -0.8, "terrible": -0.9, "awful": -0.9, "horrible": -0.8,
            "bad": -0.5, "poor": -0.4, "disappointing": -0.6,
            "frustrated": -0.7, "angry": -0.8, "annoyed": -0.6,
            "confused": -0.4, "worried": -0.6, "scared": -0.7,
            "sad": -0.7, "depressed": -0.8, "upset": -0.6,
            
            # Neutral/Complex
            "okay": 0.1, "fine": 0.2, "uncertain": -0.2, "mixed": 0.0
        }
    
    def parse_emotion(self, text: str, context: Optional[str] = None) -> EmotionMeasurement:
        """Parse emotion from text using hybrid keyword + NLP approach"""
        if not text or not text.strip():
            raise EmotionClassificationError("Cannot parse emotion from empty text")
        
        try:
            # Process text with spaCy
            doc = self.nlp(text)
            
            # Extract linguistic features for fallback
            sentiment_score = self._calculate_sentiment_score(doc)
            arousal_score = self._calculate_arousal_score(doc)
            valence = max(-1.0, min(1.0, sentiment_score))
            arousal = max(0.0, min(1.0, arousal_score))
            
            # PRIMARY: Try keyword detection first (more reliable)
            primary_emotion, keyword_confidence = self._find_primary_emotion_by_keywords(doc)
            
            # FALLBACK: Use valence/arousal mapping if low keyword confidence
            if keyword_confidence < 0.3:
                primary_emotion = ValisEmotionTaxonomy.emotion_from_valence_arousal(valence, arousal)
                classification_confidence = self._calculate_confidence(doc, sentiment_score, arousal_score)
            else:
                classification_confidence = keyword_confidence
            
            # Calculate intensity
            intensity = ValisEmotionTaxonomy.get_emotion_intensity(valence, arousal)
            
            # Find secondary emotions (exclude primary)
            secondary_emotions = self._find_secondary_emotions(doc, primary_emotion)
            
            # Extract context tags
            context_tags = self._extract_context_tags(doc)
            
            return EmotionMeasurement(
                primary_emotion=primary_emotion,
                intensity=intensity,
                confidence=classification_confidence,
                valence=valence,
                arousal=arousal,
                secondary_emotions=secondary_emotions,
                context_tags=context_tags
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing emotion from text: {e}")
            raise EmotionClassificationError(f"Failed to parse emotion: {e}")
    
    def _find_primary_emotion_by_keywords(self, doc) -> Tuple[EmotionCategory, float]:
        """Find primary emotion using keyword matching with confidence scoring"""
        from collections import Counter
        emotion_scores = Counter()
        total_matches = 0
        
        # Count keyword matches for each emotion
        for emotion in EmotionCategory:
            keywords = ValisEmotionTaxonomy.EMOTION_KEYWORDS.get(emotion, [])
            matches = 0
            
            for token in doc:
                if token.lemma_.lower() in keywords:
                    # Apply modifiers for more accurate scoring
                    base_score = 1.0
                    modified_score = self._apply_modifiers(token, base_score)
                    matches += modified_score
            
            if matches > 0:
                emotion_scores[emotion] = matches
                total_matches += matches
        
        # If no keyword matches, return default with low confidence
        if total_matches == 0:
            return EmotionCategory.CONTENTMENT, 0.0
        
        # Get the highest scoring emotion
        best_emotion, best_score = emotion_scores.most_common(1)[0]
        
        # Improved confidence calculation: 
        # - Give high confidence for any keyword match
        # - Scale by number of matches vs competing emotions
        base_confidence = 0.4  # Minimum confidence for any keyword match
        match_boost = min(0.5, best_score * 0.3)  # Boost for multiple matches
        clarity_boost = 0.0
        
        # Boost confidence if this emotion clearly dominates
        if len(emotion_scores) == 1:
            clarity_boost = 0.2  # Only one emotion detected
        elif best_score >= total_matches * 0.7:
            clarity_boost = 0.1  # This emotion is 70%+ of matches
        
        confidence = min(1.0, base_confidence + match_boost + clarity_boost)
        
        return best_emotion, confidence
    def _calculate_sentiment_score(self, doc) -> float:
        """Calculate sentiment score using linguistic analysis"""
        sentiment_sum = 0.0
        word_count = 0
        
        for token in doc:
            if token.is_alpha and not token.is_stop:
                lemma = token.lemma_.lower()
                
                # Check sentiment patterns
                if lemma in self.sentiment_patterns:
                    score = self.sentiment_patterns[lemma]
                    
                    # Apply intensifiers/dampeners
                    score = self._apply_modifiers(token, score)
                    
                    sentiment_sum += score
                    word_count += 1
        
        # Normalize by word count
        return sentiment_sum / word_count if word_count > 0 else 0.0
    
    def _calculate_arousal_score(self, doc) -> float:
        """Calculate arousal/energy level from linguistic features"""
        arousal_indicators = {
            "!": 0.3, "?": 0.2, "...": -0.1,
            "very": 0.2, "extremely": 0.4, "incredibly": 0.3,
            "quickly": 0.2, "suddenly": 0.3, "immediately": 0.3
        }
        
        arousal_sum = 0.5  # Base arousal
        
        # Check punctuation
        text = doc.text
        for indicator, score in arousal_indicators.items():
            arousal_sum += text.count(indicator) * score
        
        # Check sentence length (shorter = higher arousal)
        avg_sent_length = sum(len(sent) for sent in doc.sents) / len(list(doc.sents)) if list(doc.sents) else 20
        if avg_sent_length < 10:
            arousal_sum += 0.2
        elif avg_sent_length > 30:
            arousal_sum -= 0.1
        
        return max(0.0, min(1.0, arousal_sum))
    
    def _apply_modifiers(self, token, base_score: float) -> float:
        """Apply intensifiers and dampeners to sentiment score"""
        # Look for modifiers in nearby tokens
        for child in token.children:
            if child.lemma_.lower() in self.intensifiers:
                return base_score * 1.5
            elif child.lemma_.lower() in self.dampeners:
                return base_score * 0.6
        
        # Check previous token
        if token.i > 0:
            prev_token = token.doc[token.i - 1]
            if prev_token.lemma_.lower() in self.intensifiers:
                return base_score * 1.5
            elif prev_token.lemma_.lower() in self.dampeners:
                return base_score * 0.6
        
        return base_score
    def _calculate_confidence(self, doc, sentiment_score: float, arousal_score: float) -> float:
        """Calculate confidence in emotion classification"""
        # Base confidence from sentiment strength
        sentiment_strength = abs(sentiment_score)
        
        # Adjust for text length (longer text = more confident)
        text_length_factor = min(1.0, len(doc.text) / 100.0)
        
        # Adjust for emotional word density
        emotional_words = sum(1 for token in doc if token.lemma_.lower() in self.sentiment_patterns)
        emotional_density = emotional_words / len(doc) if len(doc) > 0 else 0
        
        confidence = (sentiment_strength * 0.5 + 
                     text_length_factor * 0.2 + 
                     emotional_density * 0.3)
        
        return max(0.1, min(1.0, confidence))
    
    def _find_secondary_emotions(self, doc, primary_emotion: EmotionCategory) -> List[Tuple[EmotionCategory, float]]:
        """Find secondary emotions present in the text"""
        emotion_counts = Counter()
        
        # Use taxonomy to find emotion keywords
        for emotion in EmotionCategory:
            if emotion == primary_emotion:
                continue
                
            # Count matches for this emotion's keywords
            keywords = ValisEmotionTaxonomy.EMOTION_KEYWORDS.get(emotion, [])
            matches = sum(1 for token in doc if token.lemma_.lower() in keywords)
            
            if matches > 0:
                emotion_counts[emotion] = matches
        
        # Return top 3 secondary emotions with normalized scores
        total_matches = sum(emotion_counts.values())
        if total_matches == 0:
            return []
        
        secondary = []
        for emotion, count in emotion_counts.most_common(3):
            score = count / total_matches
            secondary.append((emotion, score))
        
        return secondary
    
    def _extract_context_tags(self, doc) -> List[str]:
        """Extract context tags from linguistic analysis"""
        tags = []
        
        # Check for question vs statement
        if "?" in doc.text:
            tags.append("question")
        elif "!" in doc.text:
            tags.append("exclamation")
        else:
            tags.append("statement")
        
        # Check tense
        for token in doc:
            if token.tag_ in ["VBD", "VBN"]:  # Past tense
                tags.append("past_tense")
                break
            elif token.tag_ in ["VBG", "VBZ", "VBP"]:  # Present
                tags.append("present_tense") 
                break
            elif token.tag_ == "MD":  # Modal (future/conditional)
                tags.append("modal")
                break
        
        # Check for personal pronouns
        pronouns = [token.text.lower() for token in doc if token.pos_ == "PRON"]
        if any(p in ["i", "me", "my", "myself"] for p in pronouns):
            tags.append("first_person")
        if any(p in ["you", "your", "yourself"] for p in pronouns):
            tags.append("second_person")
        
        return list(set(tags))  # Remove duplicates