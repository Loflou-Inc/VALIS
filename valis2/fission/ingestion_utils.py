"""
VALIS Mr. Fission v2 - Enhanced Ingestion Utilities
Soul Stratification: Document processing and classification utilities
"""

import os
import re
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import spacy
from collections import Counter

# Import document classifier
from .deep_fusion import DocumentClassifier

class IngestionUtils:
    """
    Enhanced utilities for processing and classifying uploaded documents
    """
    
    def __init__(self):
        self.classifier = DocumentClassifier()
        
        # Initialize NLP if available
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.nlp_available = True
        except OSError:
            print("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp_available = False
    
    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text content from various file types with enhanced metadata
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)
        
        result = {
            'file_path': file_path,
            'file_type': file_ext,
            'file_size': file_size,
            'content': '',
            'metadata': {},
            'extraction_status': 'success'
        }
        
        try:
            if file_ext == '.txt':
                result.update(self._extract_text_file(file_path))
            elif file_ext == '.pdf':
                result.update(self._extract_pdf_file(file_path))
            elif file_ext == '.md':
                result.update(self._extract_markdown_file(file_path))
            elif file_ext == '.json':
                result.update(self._extract_json_file(file_path))
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                result.update(self._extract_image_file(file_path))
            else:
                result['extraction_status'] = 'unsupported_format'
                result['content'] = f"Unsupported file format: {file_ext}"
        
        except Exception as e:
            result['extraction_status'] = 'error'
            result['content'] = f"Extraction failed: {str(e)}"
        
        return result
    
    def detect_archetypes(self, text: str) -> Dict[str, float]:
        """
        Enhanced archetype detection with confidence scoring
        """
        archetype_patterns = {
            'The Sage': {
                'keywords': ['wisdom', 'knowledge', 'truth', 'understanding', 'insight', 'learn', 'teach', 'philosophy'],
                'phrases': ['seek truth', 'understand deeply', 'share knowledge', 'wisdom comes', 'learn from']
            },
            'The Caregiver': {
                'keywords': ['help', 'care', 'nurture', 'support', 'heal', 'protect', 'comfort', 'serve'],
                'phrases': ['take care of', 'help others', 'be there for', 'support through', 'healing process']
            },
            'The Creator': {
                'keywords': ['create', 'build', 'make', 'design', 'art', 'craft', 'imagine', 'innovate'],
                'phrases': ['bring to life', 'create something', 'express myself', 'build from', 'artistic vision']
            },
            'The Hero': {
                'keywords': ['challenge', 'overcome', 'achieve', 'victory', 'strength', 'courage', 'fight', 'win'],
                'phrases': ['rise to challenge', 'overcome obstacles', 'never give up', 'fight for', 'achieve greatness']
            },
            'The Lover': {
                'keywords': ['love', 'passion', 'beauty', 'connection', 'relationship', 'intimacy', 'devotion'],
                'phrases': ['deep connection', 'passionate about', 'love deeply', 'beautiful moment', 'close relationship']
            },
            'The Explorer': {
                'keywords': ['adventure', 'discover', 'journey', 'freedom', 'new', 'explore', 'travel', 'seek'],
                'phrases': ['new adventure', 'explore the', 'journey to', 'discover something', 'freedom to']
            },
            'The Ruler': {
                'keywords': ['lead', 'control', 'organize', 'responsibility', 'authority', 'manage', 'direct'],
                'phrases': ['take charge', 'lead the way', 'organize everything', 'take responsibility', 'in control']
            },
            'The Magician': {
                'keywords': ['transform', 'change', 'power', 'influence', 'vision', 'manifest', 'catalyst'],
                'phrases': ['make it happen', 'transform into', 'powerful influence', 'vision becomes', 'catalyst for']
            }
        }
        
        text_lower = text.lower()
        archetype_scores = {}
        
        for archetype, patterns in archetype_patterns.items():
            score = 0
            
            # Count keyword matches
            keyword_matches = sum(1 for keyword in patterns['keywords'] if keyword in text_lower)
            score += keyword_matches * 1.0
            
            # Count phrase matches (weighted higher)
            phrase_matches = sum(1 for phrase in patterns['phrases'] if phrase in text_lower)
            score += phrase_matches * 2.0
            
            # Normalize by content length
            text_length = len(text.split())
            normalized_score = score / max(text_length / 100, 1)  # Normalize per 100 words
            
            archetype_scores[archetype] = min(1.0, normalized_score)
        
        return archetype_scores
    
    def detect_traits(self, text: str) -> Dict[str, float]:
        """
        Enhanced personality trait detection with Big Five + additional traits
        """
        trait_patterns = {
            'openness': {
                'high': ['creative', 'imaginative', 'curious', 'artistic', 'innovative', 'original', 'inventive'],
                'low': ['conventional', 'traditional', 'practical', 'routine', 'conservative', 'predictable']
            },
            'conscientiousness': {
                'high': ['organized', 'disciplined', 'responsible', 'thorough', 'careful', 'reliable', 'punctual'],
                'low': ['disorganized', 'careless', 'unreliable', 'spontaneous', 'flexible', 'casual']
            },
            'extraversion': {
                'high': ['outgoing', 'social', 'talkative', 'energetic', 'assertive', 'enthusiastic', 'confident'],
                'low': ['quiet', 'reserved', 'introverted', 'solitary', 'thoughtful', 'reflective', 'private']
            },
            'agreeableness': {
                'high': ['kind', 'cooperative', 'trusting', 'helpful', 'compassionate', 'sympathetic', 'generous'],
                'low': ['competitive', 'skeptical', 'demanding', 'critical', 'tough', 'firm', 'direct']
            },
            'neuroticism': {
                'high': ['anxious', 'worried', 'emotional', 'stressed', 'nervous', 'sensitive', 'reactive'],
                'low': ['calm', 'relaxed', 'stable', 'confident', 'secure', 'resilient', 'composed']
            },
            'emotional_intelligence': {
                'high': ['empathetic', 'understanding', 'aware', 'intuitive', 'perceptive', 'supportive'],
                'low': ['detached', 'analytical', 'logical', 'objective', 'rational', 'impersonal']
            },
            'intellectual_curiosity': {
                'high': ['inquisitive', 'questioning', 'learning', 'studying', 'researching', 'exploring'],
                'low': ['accepting', 'satisfied', 'content', 'practical', 'focused', 'specialized']
            }
        }
        
        text_lower = text.lower()
        trait_scores = {}
        
        for trait, directions in trait_patterns.items():
            high_score = sum(1 for keyword in directions['high'] if keyword in text_lower)
            low_score = sum(1 for keyword in directions['low'] if keyword in text_lower)
            
            # Calculate net score
            net_score = high_score - low_score
            total_indicators = high_score + low_score
            
            if total_indicators > 0:
                # Normalize to 0-1 scale where 0.5 is neutral
                normalized_score = 0.5 + (net_score / total_indicators) * 0.5
                trait_scores[trait] = max(0.0, min(1.0, normalized_score))
            else:
                trait_scores[trait] = 0.5  # Neutral if no indicators
        
        return trait_scores
    
    def tag_canon_status(self, text: str, title: str = "") -> Dict[str, Any]:
        """
        Determine canonical status and importance of content
        """
        # Combine title and content for analysis
        full_text = f"{title} {text}".lower()
        
        # Canon status indicators
        core_indicators = [
            'life-changing', 'transformative', 'pivotal', 'defining moment', 'never forgot',
            'shaped me', 'changed everything', 'most important', 'fundamental', 'core belief',
            'always remember', 'profound impact', 'deeply meaningful', 'essential experience'
        ]
        
        secondary_indicators = [
            'interesting', 'notable', 'worth mentioning', 'significant', 'influenced me',
            'learned from', 'helpful', 'relevant', 'connected to', 'related experience'
        ]
        
        noise_indicators = [
            'random', 'by the way', 'unrelated', 'off topic', 'not important', 'trivial',
            'whatever', 'doesn\'t matter', 'just thought', 'random thought', 'side note'
        ]
        
        # Score each category
        core_score = sum(1 for indicator in core_indicators if indicator in full_text)
        secondary_score = sum(1 for indicator in secondary_indicators if indicator in full_text)
        noise_score = sum(1 for indicator in noise_indicators if indicator in full_text)
        
        # Determine canon status
        if core_score > 0:
            canon_status = 'core'
            confidence = min(1.0, core_score / 3)
        elif noise_score > secondary_score:
            canon_status = 'noise'
            confidence = min(1.0, noise_score / 2)
        elif secondary_score > 0:
            canon_status = 'secondary'
            confidence = min(1.0, secondary_score / 3)
        else:
            # Default determination based on content characteristics
            word_count = len(text.split())
            emotional_words = self._count_emotional_words(text)
            
            if word_count > 200 and emotional_words > 5:
                canon_status = 'core'
                confidence = 0.6
            elif word_count > 50:
                canon_status = 'secondary'
                confidence = 0.5
            else:
                canon_status = 'noise'
                confidence = 0.4
        
        return {
            'canon_status': canon_status,
            'confidence': confidence,
            'indicators': {
                'core': core_score,
                'secondary': secondary_score,
                'noise': noise_score
            }
        }
    
    def extract_entities_and_concepts(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities and key concepts using NLP
        """
        entities = {
            'persons': [],
            'places': [],
            'organizations': [],
            'dates': [],
            'concepts': [],
            'skills': [],
            'emotions': []
        }
        
        if self.nlp_available:
            doc = self.nlp(text)
            
            # Extract named entities
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    entities['persons'].append(ent.text)
                elif ent.label_ in ["GPE", "LOC"]:  # Geopolitical entity, Location
                    entities['places'].append(ent.text)
                elif ent.label_ == "ORG":
                    entities['organizations'].append(ent.text)
                elif ent.label_ == "DATE":
                    entities['dates'].append(ent.text)
        
        # Extract concepts using keyword patterns
        concept_patterns = {
            'skills': ['skill', 'ability', 'talent', 'expertise', 'proficiency', 'competence'],
            'emotions': ['feel', 'emotion', 'happy', 'sad', 'angry', 'excited', 'nervous', 'proud'],
            'concepts': ['concept', 'idea', 'theory', 'principle', 'philosophy', 'belief', 'value']
        }
        
        text_lower = text.lower()
        for category, keywords in concept_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Extract surrounding context
                    sentences = text.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            entities[category].append(sentence.strip()[:100])
                            break
        
        # Remove duplicates and limit results
        for key in entities:
            entities[key] = list(set(entities[key]))[:10]
        
        return entities
    
    def classify_document_enhanced(self, title: str, content: str, file_type: str) -> Dict[str, Any]:
        """
        Enhanced document classification with confidence scoring and metadata
        """
        # Basic classification
        basic_classification = self.classifier.classify_document(title, content, file_type)
        
        # Enhanced analysis
        canon_analysis = self.tag_canon_status(content, title)
        trait_analysis = self.detect_traits(content)
        archetype_analysis = self.detect_archetypes(content)
        entities = self.extract_entities_and_concepts(content)
        
        # Generate tags based on content analysis
        tags = self._generate_content_tags(content, entities)
        
        # Combine all analysis
        enhanced_classification = {
            **basic_classification,
            'canon_analysis': canon_analysis,
            'traits_detected': trait_analysis,
            'archetypes_detected': archetype_analysis,
            'entities': entities,
            'tags': tags,
            'content_metrics': {
                'word_count': len(content.split()),
                'sentence_count': len(content.split('.')),
                'emotional_intensity': self._calculate_emotional_intensity(content),
                'complexity_score': self._calculate_complexity_score(content)
            }
        }
        
        return enhanced_classification
    
    # Helper methods for file extraction
    def _extract_text_file(self, file_path: str) -> Dict[str, Any]:
        """Extract content from text file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return {
            'content': content,
            'metadata': {
                'encoding': 'utf-8',
                'lines': len(content.split('\n'))
            }
        }
    
    def _extract_pdf_file(self, file_path: str) -> Dict[str, Any]:
        """Extract content from PDF file"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                content = ""
                for page in reader.pages:
                    content += page.extract_text() + "\n"
            
            return {
                'content': content,
                'metadata': {
                    'pages': len(reader.pages),
                    'extraction_method': 'PyPDF2'
                }
            }
        except ImportError:
            return {
                'content': "PDF extraction requires PyPDF2 library",
                'metadata': {'error': 'missing_dependency'}
            }
    
    def _extract_markdown_file(self, file_path: str) -> Dict[str, Any]:
        """Extract content from Markdown file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Remove markdown formatting for analysis
        import re
        clean_content = re.sub(r'[#*`\[\]()]+', '', content)
        
        return {
            'content': clean_content,
            'metadata': {
                'format': 'markdown',
                'headers': len(re.findall(r'^#+', content, re.MULTILINE))
            }
        }
    
    def _extract_json_file(self, file_path: str) -> Dict[str, Any]:
        """Extract content from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert JSON to readable text
        content = json.dumps(data, indent=2)
        
        return {
            'content': content,
            'metadata': {
                'format': 'json',
                'keys': list(data.keys()) if isinstance(data, dict) else [],
                'structure': type(data).__name__
            }
        }
    
    def _extract_image_file(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from image file (placeholder for vision processing)"""
        try:
            from PIL import Image
            img = Image.open(file_path)
            
            return {
                'content': f"Image file: {os.path.basename(file_path)} ({img.size[0]}x{img.size[1]})",
                'metadata': {
                    'format': img.format,
                    'size': img.size,
                    'mode': img.mode,
                    'vision_processing': 'not_implemented'
                }
            }
        except ImportError:
            return {
                'content': f"Image file: {os.path.basename(file_path)}",
                'metadata': {'error': 'missing_pil_dependency'}
            }
    
    def _count_emotional_words(self, text: str) -> int:
        """Count emotional words in text"""
        emotional_words = [
            'love', 'hate', 'happy', 'sad', 'angry', 'excited', 'nervous',
            'proud', 'ashamed', 'grateful', 'disappointed', 'frustrated',
            'amazing', 'terrible', 'wonderful', 'awful', 'incredible'
        ]
        
        text_lower = text.lower()
        return sum(1 for word in emotional_words if word in text_lower)
    
    def _generate_content_tags(self, content: str, entities: Dict[str, List[str]]) -> List[str]:
        """Generate content tags based on analysis"""
        tags = []
        
        # Add tags based on entities
        if entities['persons']:
            tags.append('people_mentioned')
        if entities['places']:
            tags.append('places_mentioned')
        if entities['organizations']:
            tags.append('organizations_mentioned')
        if entities['dates']:
            tags.append('dates_mentioned')
        
        # Add tags based on content patterns
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['trauma', 'difficult', 'struggle', 'pain']):
            tags.append('trauma')
        if any(word in content_lower for word in ['achievement', 'success', 'proud', 'accomplished']):
            tags.append('achievement')
        if any(word in content_lower for word in ['relationship', 'love', 'partner', 'family']):
            tags.append('relationships')
        if any(word in content_lower for word in ['work', 'job', 'career', 'professional']):
            tags.append('career')
        if any(word in content_lower for word in ['school', 'education', 'learning', 'study']):
            tags.append('education')
        
        return tags
    
    def _calculate_emotional_intensity(self, content: str) -> float:
        """Calculate emotional intensity of content"""
        emotional_word_count = self._count_emotional_words(content)
        total_words = len(content.split())
        
        if total_words == 0:
            return 0.0
        
        return min(1.0, emotional_word_count / total_words * 10)  # Normalize
    
    def _calculate_complexity_score(self, content: str) -> float:
        """Calculate linguistic complexity score"""
        sentences = content.split('.')
        words = content.split()
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        long_words = len([word for word in words if len(word) > 6])
        
        # Simple complexity score
        complexity = (avg_sentence_length / 20) + (long_words / len(words))
        
        return min(1.0, complexity)
