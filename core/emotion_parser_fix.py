    def parse_emotion(self, text: str) -> EmotionMeasurement:
        """Parse emotion from text using hybrid NLP + keyword approach"""
        try:
            if not text.strip():
                return EmotionMeasurement(
                    primary_emotion=EmotionCategory.CONTENTMENT,
                    intensity=0.0,
                    confidence=0.0,
                    valence=0.0,
                    arousal=0.0,
                    secondary_emotions=[],
                    context_tags=[]
                )
            
            # Process with spaCy
            doc = self.nlp(text)
            
            # Extract linguistic features
            sentiment_score = self._calculate_sentiment_score(doc)
            arousal_score = self._calculate_arousal_score(doc)
            
            # Convert to valence/arousal coordinates
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
        confidence = min(1.0, best_score / len(doc) * 2.0)  # Normalize by text length
        
        return best_emotion, confidence
