"""
VALIS Mr. Fission - Ingestion Engine
Converts raw human material into symbolic features for persona construction
"""

import os
import json
import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

# File processing imports
import PyPDF2
import pandas as pd
from PIL import Image
import wave
import speech_recognition as sr

# Text analysis
import nltk
from textstat import flesch_reading_ease, syllable_count
from collections import Counter
import spacy

# Vision processing (optional)
try:
    import torch
    import clip
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    print("Vision processing not available - install torch and clip for image analysis")

class FissionIngestionEngine:
    """
    Ingests arbitrary human material and extracts symbolic/conceptual features
    for persona construction
    """
    
    def __init__(self, output_dir: str = "C:\\VALIS\\vault\\personas\\raw"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize vision model if available
        if VISION_AVAILABLE:
            try:
                self.vision_model, self.vision_preprocess = clip.load("ViT-B/32")
                print("CLIP vision model loaded successfully")
            except Exception as e:
                print(f"Failed to load CLIP: {e}")
                self.vision_model = None
        else:
            self.vision_model = None
        
        # Personality trait keywords
        self.trait_keywords = {
            "extraversion": ["outgoing", "social", "energetic", "talkative", "party", "crowd", "leader"],
            "introversion": ["quiet", "reserved", "thoughtful", "solitary", "reflection", "alone", "private"],
            "openness": ["creative", "imaginative", "curious", "artistic", "novel", "adventure", "explore"],
            "conscientiousness": ["organized", "responsible", "disciplined", "careful", "plan", "detail", "goal"],
            "agreeableness": ["kind", "helpful", "trusting", "cooperative", "empathetic", "caring", "warm"],
            "neuroticism": ["anxious", "worried", "stressed", "emotional", "moody", "nervous", "tension"],
            "analytical": ["logic", "reason", "analyze", "think", "rational", "systematic", "precise"],
            "intuitive": ["feeling", "instinct", "sense", "intuition", "gut", "vibe", "energy"]
        }
        
        # Archetypal keywords
        self.archetype_keywords = {
            "The Sage": ["wisdom", "knowledge", "teach", "learn", "understand", "truth", "mentor"],
            "The Caregiver": ["help", "nurture", "care", "support", "protect", "heal", "service"],
            "The Hero": ["achieve", "challenge", "overcome", "brave", "courage", "victory", "fight"],
            "The Rebel": ["change", "revolution", "break", "freedom", "different", "challenge", "rule"],
            "The Lover": ["passion", "beauty", "relationship", "romance", "connection", "intimate", "heart"],
            "The Creator": ["create", "build", "make", "design", "art", "imagination", "vision"],
            "The Jester": ["fun", "humor", "laugh", "play", "joy", "light", "joke"],
            "The Explorer": ["discover", "adventure", "journey", "travel", "explore", "new", "freedom"],
            "The Magician": ["transform", "magic", "vision", "dream", "possibility", "power", "mystical"],
            "The Ruler": ["control", "leadership", "authority", "order", "organize", "responsible", "status"],
            "The Innocent": ["simple", "pure", "hope", "faith", "optimistic", "trust", "goodness"],
            "The Orphan": ["belong", "connect", "community", "realistic", "practical", "down-to-earth"]
        }
    
    def ingest_file(self, file_path: str) -> Dict[str, Any]:
        """
        Main ingestion method - routes to appropriate parser based on file type
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)
        
        result = {
            "source_file": file_name,
            "file_path": file_path,
            "file_type": file_ext,
            "processed_at": datetime.now().isoformat(),
            "content_hash": self._get_file_hash(file_path),
            "features": {}
        }
        
        try:
            if file_ext == '.pdf':
                result["features"] = self._parse_pdf(file_path)
            elif file_ext in ['.txt', '.md']:
                result["features"] = self._parse_text(file_path)
            elif file_ext == '.json':
                result["features"] = self._parse_json(file_path)
            elif file_ext == '.csv':
                result["features"] = self._parse_csv(file_path)
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                result["features"] = self._parse_image(file_path)
            elif file_ext in ['.wav', '.mp3']:
                result["features"] = self._parse_audio(file_path)
            else:
                result["features"] = {"error": f"Unsupported file type: {file_ext}"}
        
        except Exception as e:
            result["features"] = {"error": f"Failed to parse {file_ext}: {str(e)}"}
        
        return result
    
    def _get_file_hash(self, file_path: str) -> str:
        """Generate hash of file content for deduplication"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text and features from PDF"""
        features = {"type": "document", "content": "", "pages": 0}
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                features["pages"] = len(pdf_reader.pages)
                
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
                
                features["content"] = text_content
                features.update(self._analyze_text_content(text_content))
                
        except Exception as e:
            features["error"] = f"PDF parsing failed: {str(e)}"
        
        return features
    
    def _parse_text(self, file_path: str) -> Dict[str, Any]:
        """Extract features from text file"""
        features = {"type": "text", "content": ""}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                features["content"] = content
                features.update(self._analyze_text_content(content))
                
        except Exception as e:
            features["error"] = f"Text parsing failed: {str(e)}"
        
        return features
    
    def _analyze_text_content(self, text: str) -> Dict[str, Any]:
        """Deep analysis of text content for personality traits and themes"""
        analysis = {
            "word_count": len(text.split()),
            "char_count": len(text),
            "readability": flesch_reading_ease(text) if text.strip() else 0,
            "personality_traits": {},
            "archetypes": {},
            "themes": [],
            "emotional_tone": {},
            "writing_style": {}
        }
        
        # Normalize text for analysis
        text_lower = text.lower()
        
        # Personality trait analysis
        for trait, keywords in self.trait_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            analysis["personality_traits"][trait] = score / len(text.split()) if text.split() else 0
        
        # Archetype analysis
        for archetype, keywords in self.archetype_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            analysis["archetypes"][archetype] = score / len(text.split()) if text.split() else 0
        
        # Emotional tone analysis (simple keyword-based)
        emotional_keywords = {
            "positive": ["happy", "joy", "love", "excited", "wonderful", "amazing", "great", "good"],
            "negative": ["sad", "angry", "frustrated", "terrible", "awful", "hate", "bad", "difficult"],
            "neutral": ["okay", "fine", "normal", "regular", "standard", "typical"],
            "intense": ["extremely", "very", "incredibly", "absolutely", "totally", "completely"]
        }
        
        for emotion, keywords in emotional_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            analysis["emotional_tone"][emotion] = score / len(text.split()) if text.split() else 0
        
        # Writing style analysis
        sentences = re.split(r'[.!?]+', text)
        analysis["writing_style"] = {
            "avg_sentence_length": sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0,
            "question_count": text.count('?'),
            "exclamation_count": text.count('!'),
            "first_person_usage": text_lower.count('i ') + text_lower.count('me ') + text_lower.count('my '),
            "complexity_score": syllable_count(text) / len(text.split()) if text.split() else 0
        }
        
        # Extract key themes using NLP if available
        if self.nlp and text.strip():
            try:
                doc = self.nlp(text[:1000000])  # Limit for memory
                
                # Extract named entities
                entities = [(ent.text, ent.label_) for ent in doc.ents]
                analysis["named_entities"] = entities[:20]  # Top 20
                
                # Extract key phrases (noun phrases)
                noun_phrases = [chunk.text for chunk in doc.noun_chunks]
                analysis["key_phrases"] = Counter(noun_phrases).most_common(10)
                
            except Exception as e:
                analysis["nlp_error"] = str(e)
        
        return analysis
    
    def _parse_json(self, file_path: str) -> Dict[str, Any]:
        """Parse JSON file for structured data"""
        features = {"type": "structured_data"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                features["data"] = data
                features["structure"] = self._analyze_json_structure(data)
                
                # If it contains text fields, analyze them
                text_content = self._extract_text_from_json(data)
                if text_content:
                    features.update(self._analyze_text_content(text_content))
                
        except Exception as e:
            features["error"] = f"JSON parsing failed: {str(e)}"
        
        return features
    
    def _analyze_json_structure(self, data: Any) -> Dict[str, Any]:
        """Analyze structure of JSON data"""
        if isinstance(data, dict):
            return {
                "type": "object",
                "keys": list(data.keys()),
                "key_count": len(data.keys())
            }
        elif isinstance(data, list):
            return {
                "type": "array",
                "length": len(data),
                "item_types": [type(item).__name__ for item in data[:5]]
            }
        else:
            return {
                "type": type(data).__name__,
                "value": str(data)[:100]
            }
    
    def _extract_text_from_json(self, data: Any) -> str:
        """Extract all text content from JSON for analysis"""
        text_content = []
        
        def extract_strings(obj):
            if isinstance(obj, str):
                text_content.append(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_strings(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_strings(item)
        
        extract_strings(data)
        return " ".join(text_content)
    
    def _parse_csv(self, file_path: str) -> Dict[str, Any]:
        """Parse CSV file for timeline/event data"""
        features = {"type": "tabular_data"}
        
        try:
            df = pd.read_csv(file_path)
            
            features["rows"] = len(df)
            features["columns"] = list(df.columns)
            features["shape"] = df.shape
            
            # Look for date columns
            date_columns = []
            for col in df.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    date_columns.append(col)
            
            features["date_columns"] = date_columns
            
            # Extract text content for analysis
            text_columns = df.select_dtypes(include=['object']).columns
            if len(text_columns) > 0:
                text_content = ' '.join(df[text_columns].fillna('').astype(str).sum())
                features.update(self._analyze_text_content(text_content))
            
            # Store sample data
            features["sample_data"] = df.head(3).to_dict('records')
            
        except Exception as e:
            features["error"] = f"CSV parsing failed: {str(e)}"
        
        return features
    
    def _parse_image(self, file_path: str) -> Dict[str, Any]:
        """Extract features from image using CLIP if available"""
        features = {"type": "image"}
        
        try:
            # Basic image info
            with Image.open(file_path) as img:
                features["dimensions"] = img.size
                features["mode"] = img.mode
                features["format"] = img.format
            
            # Vision analysis if available
            if self.vision_model is not None:
                features.update(self._analyze_image_with_clip(file_path))
            else:
                features["vision_analysis"] = "CLIP not available - basic image info only"
                
        except Exception as e:
            features["error"] = f"Image parsing failed: {str(e)}"
        
        return features
    
    def _analyze_image_with_clip(self, file_path: str) -> Dict[str, Any]:
        """Analyze image using CLIP model"""
        try:
            image = Image.open(file_path)
            image_input = self.vision_preprocess(image).unsqueeze(0)
            
            # Predefined text prompts for analysis
            text_prompts = [
                "a person", "a face", "a portrait", "a photograph",
                "happy", "sad", "angry", "peaceful", "energetic",
                "professional", "casual", "artistic", "natural",
                "indoor", "outdoor", "urban", "nature",
                "vintage", "modern", "colorful", "monochrome"
            ]
            
            text_inputs = clip.tokenize(text_prompts)
            
            with torch.no_grad():
                image_features = self.vision_model.encode_image(image_input)
                text_features = self.vision_model.encode_text(text_inputs)
                
                # Calculate similarities
                similarities = (100.0 * image_features @ text_features.T).softmax(dim=-1)
                values, indices = similarities[0].topk(5)
                
                # Create results
                top_matches = []
                for i in range(5):
                    top_matches.append({
                        "description": text_prompts[indices[i]],
                        "confidence": float(values[i])
                    })
                
                return {
                    "vision_analysis": "CLIP analysis complete",
                    "top_descriptions": top_matches,
                    "detected_elements": [match["description"] for match in top_matches if match["confidence"] > 0.15]
                }
                
        except Exception as e:
            return {"vision_error": f"CLIP analysis failed: {str(e)}"}
    
    def _parse_audio(self, file_path: str) -> Dict[str, Any]:
        """Extract features from audio file"""
        features = {"type": "audio"}
        
        try:
            # Basic audio info
            if file_path.endswith('.wav'):
                with wave.open(file_path, 'rb') as audio_file:
                    features["duration"] = audio_file.getnframes() / audio_file.getframerate()
                    features["channels"] = audio_file.getnchannels()
                    features["sample_rate"] = audio_file.getframerate()
            
            # Speech recognition (if possible)
            try:
                r = sr.Recognizer()
                with sr.AudioFile(file_path) as source:
                    audio = r.record(source)
                    text = r.recognize_google(audio)
                    features["transcription"] = text
                    features.update(self._analyze_text_content(text))
            except:
                features["transcription"] = "Speech recognition failed or not available"
                
        except Exception as e:
            features["error"] = f"Audio parsing failed: {str(e)}"
        
        return features
    
    def batch_ingest(self, file_paths: List[str]) -> Dict[str, Any]:
        """Ingest multiple files and combine results"""
        results = {
            "batch_id": hashlib.md5(str(file_paths).encode()).hexdigest()[:8],
            "processed_at": datetime.now().isoformat(),
            "file_count": len(file_paths),
            "files": {},
            "combined_features": {}
        }
        
        all_features = []
        
        for file_path in file_paths:
            try:
                file_result = self.ingest_file(file_path)
                results["files"][os.path.basename(file_path)] = file_result
                
                if "error" not in file_result["features"]:
                    all_features.append(file_result["features"])
                    
            except Exception as e:
                results["files"][os.path.basename(file_path)] = {
                    "error": f"Failed to process: {str(e)}"
                }
        
        # Combine features from all files
        if all_features:
            results["combined_features"] = self._combine_features(all_features)
        
        return results
    
    def _combine_features(self, features_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine features from multiple files into unified persona features"""
        combined = {
            "personality_traits": {},
            "archetypes": {},
            "emotional_tone": {},
            "content_summary": {
                "total_word_count": 0,
                "avg_readability": 0,
                "dominant_themes": []
            }
        }
        
        trait_scores = {}
        archetype_scores = {}
        emotion_scores = {}
        total_words = 0
        readability_scores = []
        
        for features in features_list:
            # Aggregate personality traits
            if "personality_traits" in features:
                for trait, score in features["personality_traits"].items():
                    if trait not in trait_scores:
                        trait_scores[trait] = []
                    trait_scores[trait].append(score)
            
            # Aggregate archetypes
            if "archetypes" in features:
                for archetype, score in features["archetypes"].items():
                    if archetype not in archetype_scores:
                        archetype_scores[archetype] = []
                    archetype_scores[archetype].append(score)
            
            # Aggregate emotional tone
            if "emotional_tone" in features:
                for emotion, score in features["emotional_tone"].items():
                    if emotion not in emotion_scores:
                        emotion_scores[emotion] = []
                    emotion_scores[emotion].append(score)
            
            # Aggregate content metrics
            if "word_count" in features:
                total_words += features["word_count"]
            
            if "readability" in features:
                readability_scores.append(features["readability"])
        
        # Calculate averages
        combined["personality_traits"] = {
            trait: sum(scores) / len(scores) 
            for trait, scores in trait_scores.items()
        }
        
        combined["archetypes"] = {
            archetype: sum(scores) / len(scores) 
            for archetype, scores in archetype_scores.items()
        }
        
        combined["emotional_tone"] = {
            emotion: sum(scores) / len(scores) 
            for emotion, scores in emotion_scores.items()
        }
        
        combined["content_summary"]["total_word_count"] = total_words
        combined["content_summary"]["avg_readability"] = (
            sum(readability_scores) / len(readability_scores) 
            if readability_scores else 0
        )
        
        return combined


# Example usage and testing
if __name__ == "__main__":
    print("=== VALIS MR. FISSION INGESTION ENGINE ===")
    
    # Initialize ingestion engine
    ingester = FissionIngestionEngine()
    
    # Test with a simple text file
    test_text = """
    Jane is a warm and caring therapist who has dedicated her life to helping others.
    She believes in the power of human connection and empathy. With over 15 years of experience,
    Jane has developed a unique approach that combines traditional therapy with mindfulness practices.
    
    She grew up in a small town where community support was everything. This shaped her belief
    that everyone deserves compassion and understanding. Jane is known for her gentle wisdom
    and ability to see the best in people, even during their darkest moments.
    
    In her free time, Jane enjoys reading philosophy, practicing yoga, and spending time in nature.
    She finds that these activities help her maintain balance and continue growing as both a person
    and a professional.
    """
    
    # Save test text and analyze
    test_file = "C:\\VALIS\\test_jane.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_text)
    
    # Ingest the test file
    result = ingester.ingest_file(test_file)
    
    print("Ingestion Results:")
    print(f"File: {result['source_file']}")
    print(f"Type: {result['file_type']}")
    
    if "personality_traits" in result["features"]:
        print("\nPersonality Traits:")
        for trait, score in result["features"]["personality_traits"].items():
            if score > 0:
                print(f"  {trait}: {score:.3f}")
    
    if "archetypes" in result["features"]:
        print("\nArchetypes:")
        for archetype, score in result["features"]["archetypes"].items():
            if score > 0:
                print(f"  {archetype}: {score:.3f}")
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("\n=== INGESTION ENGINE ONLINE ===")
