"""
VALIS Mr. Fission v2 - Deep Fusion Engine
Soul Stratification: Layered consciousness construction with knowledge boundaries
"""

import json
import uuid
import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import sqlite3
import os

# Import existing utilities
import sys
sys.path.append('..')
from memory.db import db

class LayeredPersonaBlueprint:
    """
    Enhanced persona blueprint with dual-layer identity system
    Separates narrative identity (lived experience) from knowledge identity (factual knowledge)
    """
    
    def __init__(self):
        self.schema = {
            "id": str(uuid.uuid4()),
            "name": "",
            "version": "2.0",  # Soul Stratification version
            "created_at": datetime.now().isoformat(),
            
            # Dual-layer identity system
            "narrative_identity": {
                "life_phases": {
                    "childhood": {"events": [], "themes": [], "formative_experiences": []},
                    "adolescence": {"events": [], "themes": [], "formative_experiences": []},
                    "young_adult": {"events": [], "themes": [], "formative_experiences": []},
                    "adult": {"events": [], "themes": [], "formative_experiences": []},
                    "current": {"events": [], "themes": [], "current_circumstances": []}
                },
                "core_narratives": [],  # Central life stories and self-concepts
                "symbolic_memories": [], # Emotionally/symbolically significant memories
                "personality_development": {
                    "trait_evolution": {},  # How traits developed over time
                    "defining_moments": [], # Key events that shaped personality
                    "recurring_patterns": [] # Behavioral/emotional patterns
                }
            },
            
            "knowledge_identity": {
                "formal_education": {
                    "degrees": [],      # {institution, degree, field, years, gpa}
                    "courses": [],      # Specific courses taken
                    "certifications": [], # Professional certifications
                    "academic_achievements": []
                },
                "professional_experience": {
                    "positions": [],    # {company, role, years, responsibilities}
                    "skills": [],       # Technical and professional skills
                    "domains": [],      # Areas of expertise
                    "accomplishments": []
                },
                "cultural_knowledge": {
                    "languages": [],    # Languages and proficiency levels
                    "literature": [],   # Books, authors actually read/studied
                    "arts": [],         # Artistic knowledge and exposure
                    "philosophy": [],   # Philosophical concepts actually understood
                    "sciences": []      # Scientific knowledge areas
                },
                "lived_knowledge": {
                    "places_lived": [], # Geographic knowledge from residence
                    "travels": [],      # Places visited and cultural exposure
                    "communities": [],  # Social groups and cultural contexts
                    "relationships": [] # Significant relationships and what they taught
                },
                "knowledge_boundaries": {
                    "unknown_domains": [],   # Explicitly what they DON'T know
                    "surface_knowledge": [], # Things they know only superficially
                    "deep_expertise": [],    # Areas of genuine deep knowledge
                    "learning_style": ""     # How they acquire new knowledge
                }
            },
            
            # Enhanced trait system
            "personality_traits": {
                "big_five": {
                    "openness": 0.5,
                    "conscientiousness": 0.5,
                    "extraversion": 0.5,
                    "agreeableness": 0.5,
                    "neuroticism": 0.5
                },
                "jungian_types": {
                    "primary_function": "",
                    "auxiliary_function": "",
                    "tertiary_function": "",
                    "inferior_function": ""
                },
                "communication_style": {
                    "formality_level": "moderate",
                    "humor_style": "",
                    "conflict_approach": "",
                    "emotional_expression": ""
                }
            },
            
            # Archetypal influences
            "archetypes": {
                "primary": "",      # Dominant archetype
                "secondary": [],    # Supporting archetypes
                "shadow": "",       # Shadow archetype
                "aspirational": ""  # Archetype they aspire to embody
            },
            
            # Document provenance and traceability
            "source_documents": {
                "total_count": 0,
                "by_type": {},
                "canon_distribution": {},
                "life_phase_coverage": [],
                "document_ids": []  # References to persona_documents table
            },
            
            # Fusion metadata and quality metrics
            "fusion_metadata": {
                "fusion_confidence": 0.0,
                "knowledge_completeness": 0.0,  # How complete is their knowledge profile
                "narrative_coherence": 0.0,     # How coherent is their life story
                "boundary_clarity": 0.0,        # How clear are their knowledge boundaries
                "processing_method": "deep_stratification",
                "source_file_count": 0,
                "warnings": [],                  # Potential issues or gaps
                "recommendations": []            # Suggestions for improvement
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return self.schema
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.schema, indent=indent, default=str)
    
    def save(self, filepath: str) -> None:
        """Save enhanced blueprint to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())


class DocumentClassifier:
    """
    Classifies uploaded documents by type, canon status, and life phase
    """
    
    def __init__(self):
        # Document type classification patterns
        self.doc_type_patterns = {
            'education': [
                'transcript', 'diploma', 'certificate', 'syllabus', 'coursework',
                'university', 'college', 'school', 'degree', 'gpa', 'course',
                'academic', 'thesis', 'dissertation', 'curriculum'
            ],
            'career': [
                'resume', 'cv', 'job', 'position', 'company', 'employer',
                'career', 'professional', 'work', 'employment', 'salary',
                'promotion', 'manager', 'employee', 'business'
            ],
            'narrative': [
                'journal', 'diary', 'memoir', 'autobiography', 'story',
                'experience', 'memory', 'childhood', 'family', 'relationship',
                'feeling', 'emotion', 'personal', 'life', 'growing up'
            ],
            'reference': [
                'article', 'research', 'study', 'book', 'author', 'theory',
                'concept', 'definition', 'encyclopedia', 'textbook'
            ]
        }
        
        # Life phase classification patterns
        self.life_phase_patterns = {
            'childhood': [
                'child', 'childhood', 'young', 'elementary', 'grade school',
                'kindergarten', 'baby', 'toddler', 'preschool', 'family home'
            ],
            'adolescence': [
                'teenager', 'teen', 'adolescent', 'high school', 'puberty',
                'dating', 'prom', 'graduation', 'first job', 'driving'
            ],
            'young_adult': [
                'college', 'university', 'dorm', 'fraternity', 'sorority',
                'first apartment', 'internship', 'entry level', 'twenties'
            ],
            'adult': [
                'marriage', 'wedding', 'spouse', 'children', 'parenting',
                'mortgage', 'career', 'thirties', 'forties', 'established'
            ],
            'current': [
                'now', 'currently', 'today', 'present', 'recent', 'lately',
                'this year', 'these days', 'at the moment'
            ]
        }
        
        # Canon status indicators
        self.canon_indicators = {
            'core': [
                'important', 'significant', 'defining', 'life-changing',
                'formative', 'crucial', 'pivotal', 'fundamental', 'essential'
            ],
            'secondary': [
                'interesting', 'notable', 'worth mentioning', 'relevant',
                'related', 'connected', 'influenced', 'affected'
            ],
            'noise': [
                'random', 'unrelated', 'tangent', 'aside', 'by the way',
                'off topic', 'irrelevant', 'not important', 'whatever'
            ]
        }
    
    def classify_document(self, title: str, content: str, file_type: str) -> Dict[str, str]:
        """
        Classify a document by type, canon status, and life phase
        """
        classification = {
            'doc_type': self._classify_doc_type(title, content),
            'canon_status': self._classify_canon_status(content),
            'life_phase': self._classify_life_phase(content),
            'confidence': 0.0
        }
        
        # Calculate classification confidence
        classification['confidence'] = self._calculate_confidence(classification, content)
        
        return classification
    
    def _classify_doc_type(self, title: str, content: str) -> str:
        """Determine document type based on content analysis"""
        text = (title + " " + content).lower()
        scores = {}
        
        for doc_type, patterns in self.doc_type_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text)
            scores[doc_type] = score
        
        if not scores or max(scores.values()) == 0:
            return 'personal'  # Default classification
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _classify_canon_status(self, content: str) -> str:
        """Determine canonical importance of content"""
        text = content.lower()
        scores = {}
        
        for status, indicators in self.canon_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text)
            scores[status] = score
        
        if not scores or max(scores.values()) == 0:
            return 'core'  # Default to core if unclear
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _classify_life_phase(self, content: str) -> Optional[str]:
        """Determine life phase referenced in content"""
        text = content.lower()
        scores = {}
        
        for phase, patterns in self.life_phase_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text)
            scores[phase] = score
        
        if not scores or max(scores.values()) == 0:
            return None  # No clear life phase
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_confidence(self, classification: Dict[str, str], content: str) -> float:
        """Calculate confidence score for classification"""
        # Simple confidence based on content length and classification clarity
        base_confidence = min(0.8, len(content) / 1000)  # Longer content = higher confidence
        
        # Boost confidence if multiple classification signals present
        if classification['life_phase']:
            base_confidence += 0.1
        if classification['canon_status'] != 'core':  # Non-default canon status
            base_confidence += 0.1
        
        return min(1.0, base_confidence)


class DeepFusionEngine:
    """
    Enhanced fusion engine that creates layered persona blueprints with knowledge boundaries
    Implements Soul Stratification architecture
    """
    
    def __init__(self, db_connection=None):
        self.db = db_connection or db
        self.classifier = DocumentClassifier()
        
        # Knowledge domain patterns for boundary detection
        self.knowledge_domains = {
            'academic': {
                'philosophy': ['philosophy', 'kant', 'aristotle', 'ethics', 'metaphysics', 'epistemology'],
                'literature': ['literature', 'poetry', 'shakespeare', 'novel', 'author', 'literary'],
                'science': ['science', 'physics', 'chemistry', 'biology', 'research', 'experiment'],
                'mathematics': ['mathematics', 'algebra', 'calculus', 'geometry', 'statistics', 'math'],
                'history': ['history', 'historical', 'ancient', 'medieval', 'war', 'empire'],
                'psychology': ['psychology', 'cognitive', 'behavioral', 'therapy', 'mental health']
            },
            'practical': {
                'technology': ['computer', 'programming', 'software', 'internet', 'digital', 'tech'],
                'business': ['business', 'finance', 'marketing', 'sales', 'management', 'corporate'],
                'arts': ['art', 'music', 'painting', 'design', 'creative', 'artistic'],
                'sports': ['sport', 'football', 'basketball', 'exercise', 'athletic', 'fitness'],
                'cooking': ['cooking', 'recipe', 'food', 'kitchen', 'culinary', 'chef']
            }
        }
    
    def store_document(self, persona_id: str, session_id: str, title: str, 
                      content: str, file_type: str, file_size: int) -> str:
        """
        Store document in persona_documents table with classification
        """
        # Classify document
        classification = self.classifier.classify_document(title, content, file_type)
        
        # Generate content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Store in database
        doc_id = str(uuid.uuid4())
        
        self.db.execute("""
            INSERT INTO persona_documents 
            (id, persona_id, session_id, title, content, file_type, doc_type, 
             canon_status, life_phase, content_hash, file_size, processed_timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            doc_id, persona_id, session_id, title, content, file_type,
            classification['doc_type'], classification['canon_status'], 
            classification['life_phase'], content_hash, file_size, datetime.now()
        ))
        
        return doc_id
    
    def load_persona_documents(self, persona_id: str) -> Dict[str, List[Dict]]:
        """
        Load all documents for a persona, organized by type and phase
        """
        documents = self.db.query("""
            SELECT id, title, content, file_type, doc_type, canon_status, 
                   life_phase, tags, metadata, created_at
            FROM persona_documents 
            WHERE persona_id = %s
            ORDER BY created_at ASC
        """, (persona_id,))
        
        # Organize documents by type
        organized = {
            'narrative': defaultdict(list),
            'education': [],
            'career': [],
            'reference': [],
            'personal': []
        }
        
        for doc in documents:
            doc_type = doc['doc_type']
            if doc_type == 'narrative' and doc['life_phase']:
                organized['narrative'][doc['life_phase']].append(doc)
            else:
                organized[doc_type].append(doc)
        
        return organized
    
    def fuse_layered_persona(self, persona_id: str, persona_name: str) -> LayeredPersonaBlueprint:
        """
        Create a layered persona blueprint from stored documents
        Main fusion method that implements knowledge boundary logic
        """
        blueprint = LayeredPersonaBlueprint()
        blueprint.schema['name'] = persona_name
        blueprint.schema['id'] = persona_id
        
        # Load organized documents
        documents = self.load_persona_documents(persona_id)
        
        # Process narrative identity
        self._fuse_narrative_identity(blueprint, documents['narrative'])
        
        # Process knowledge identity
        self._fuse_knowledge_identity(blueprint, documents)
        
        # Extract personality traits across all documents
        self._fuse_personality_traits(blueprint, documents)
        
        # Determine archetypes
        self._fuse_archetypes(blueprint, documents)
        
        # Set knowledge boundaries (solve Faust problem)
        self._establish_knowledge_boundaries(blueprint, documents)
        
        # Calculate fusion metrics
        self._calculate_fusion_metrics(blueprint, documents)
        
        # Update source document metadata
        blueprint.schema['source_documents'] = self._compile_source_metadata(documents)
        
        return blueprint    
    def _fuse_narrative_identity(self, blueprint: LayeredPersonaBlueprint, narrative_docs: Dict[str, List[Dict]]):
        """
        Process narrative documents to build life-phase mapped identity
        """
        for phase, docs in narrative_docs.items():
            if not docs:
                continue
                
            phase_data = blueprint.schema['narrative_identity']['life_phases'][phase]
            
            for doc in docs:
                content = doc['content']
                
                # Extract events and themes from narrative content
                events = self._extract_life_events(content)
                themes = self._extract_narrative_themes(content)
                
                phase_data['events'].extend(events)
                phase_data['themes'].extend(themes)
                
                # Mark formative experiences based on canon status
                if doc['canon_status'] == 'core':
                    formative_exp = self._extract_formative_experiences(content)
                    if phase == 'current':
                        phase_data['current_circumstances'].extend(formative_exp)
                    else:
                        phase_data['formative_experiences'].extend(formative_exp)
        
        # Build core narratives from patterns across phases
        blueprint.schema['narrative_identity']['core_narratives'] = self._identify_core_narratives(narrative_docs)
    
    def _fuse_knowledge_identity(self, blueprint: LayeredPersonaBlueprint, documents: Dict[str, List[Dict]]):
        """
        Process knowledge documents to build bounded expertise profile
        """
        knowledge = blueprint.schema['knowledge_identity']
        
        # Process education documents
        for doc in documents['education']:
            education_data = self._extract_education_info(doc['content'])
            if education_data:
                knowledge['formal_education']['degrees'].extend(education_data.get('degrees', []))
                knowledge['formal_education']['courses'].extend(education_data.get('courses', []))
                knowledge['formal_education']['certifications'].extend(education_data.get('certifications', []))
        
        # Process career documents
        for doc in documents['career']:
            career_data = self._extract_career_info(doc['content'])
            if career_data:
                knowledge['professional_experience']['positions'].extend(career_data.get('positions', []))
                knowledge['professional_experience']['skills'].extend(career_data.get('skills', []))
                knowledge['professional_experience']['domains'].extend(career_data.get('domains', []))
        
        # Extract cultural knowledge from all narrative sources
        all_content = ""
        for doc_type, docs in documents.items():
            if doc_type == 'narrative':
                for phase_docs in docs.values():
                    all_content += " ".join([d['content'] for d in phase_docs])
            else:
                all_content += " ".join([d['content'] for d in docs])
        
        cultural_knowledge = self._extract_cultural_knowledge(all_content)
        knowledge['cultural_knowledge'].update(cultural_knowledge)
    
    def _fuse_personality_traits(self, blueprint: LayeredPersonaBlueprint, documents: Dict[str, List[Dict]]):
        """
        Extract personality traits from all document sources
        """
        all_text = self._compile_all_text(documents)
        
        # Extract Big Five traits using keyword analysis
        big_five = self._extract_big_five_traits(all_text)
        blueprint.schema['personality_traits']['big_five'].update(big_five)
        
        # Determine communication style
        comm_style = self._extract_communication_style(all_text)
        blueprint.schema['personality_traits']['communication_style'].update(comm_style)
    
    def _fuse_archetypes(self, blueprint: LayeredPersonaBlueprint, documents: Dict[str, List[Dict]]):
        """
        Identify Jungian archetypes based on narrative patterns
        """
        all_text = self._compile_all_text(documents)
        
        archetype_scores = self._score_archetypes(all_text)
        
        # Sort by score and assign
        sorted_archetypes = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_archetypes:
            blueprint.schema['archetypes']['primary'] = sorted_archetypes[0][0]
            if len(sorted_archetypes) > 1:
                blueprint.schema['archetypes']['secondary'] = [arch[0] for arch in sorted_archetypes[1:3]]
    
    def _establish_knowledge_boundaries(self, blueprint: LayeredPersonaBlueprint, documents: Dict[str, List[Dict]]):
        """
        CRITICAL: Solve the Faust problem by establishing what the persona actually knows
        """
        knowledge_bounds = blueprint.schema['knowledge_identity']['knowledge_boundaries']
        all_text = self._compile_all_text(documents)
        
        # Detect domains with evidence of knowledge
        demonstrated_knowledge = []
        surface_knowledge = []
        
        for domain_category, domains in self.knowledge_domains.items():
            for domain, keywords in domains.items():
                # Count keyword occurrences and context
                keyword_count = sum(1 for keyword in keywords if keyword in all_text.lower())
                
                if keyword_count >= 3:  # Strong evidence of knowledge
                    demonstrated_knowledge.append(domain)
                elif keyword_count >= 1:  # Surface-level knowledge
                    surface_knowledge.append(domain)
        
        knowledge_bounds['deep_expertise'] = demonstrated_knowledge
        knowledge_bounds['surface_knowledge'] = surface_knowledge
        
        # Explicitly mark unknown domains (everything else)
        all_domains = set()
        for domains in self.knowledge_domains.values():
            all_domains.update(domains.keys())
        
        known_domains = set(demonstrated_knowledge + surface_knowledge)
        unknown_domains = all_domains - known_domains
        
        knowledge_bounds['unknown_domains'] = list(unknown_domains)
        
        # Set learning style based on education/career patterns
        knowledge_bounds['learning_style'] = self._infer_learning_style(documents)
    
    def _calculate_fusion_metrics(self, blueprint: LayeredPersonaBlueprint, documents: Dict[str, List[Dict]]):
        """
        Calculate quality metrics for the fusion process
        """
        metadata = blueprint.schema['fusion_metadata']
        
        # Count total documents and types
        total_docs = sum(len(docs) if isinstance(docs, list) else sum(len(phase_docs) for phase_docs in docs.values()) 
                        for docs in documents.values())
        
        metadata['source_file_count'] = total_docs
        
        # Calculate completeness metrics
        life_phases_covered = len([phase for phase, docs in documents['narrative'].items() if docs])
        knowledge_completeness = len(blueprint.schema['knowledge_identity']['knowledge_boundaries']['deep_expertise']) / 10
        narrative_coherence = life_phases_covered / 5  # 5 life phases total
        
        metadata['knowledge_completeness'] = min(1.0, knowledge_completeness)
        metadata['narrative_coherence'] = narrative_coherence
        metadata['boundary_clarity'] = self._calculate_boundary_clarity(blueprint)
        
        # Overall fusion confidence
        metadata['fusion_confidence'] = (
            metadata['knowledge_completeness'] * 0.3 +
            metadata['narrative_coherence'] * 0.3 +
            metadata['boundary_clarity'] * 0.4
        )
        
        # Generate warnings and recommendations
        metadata['warnings'] = self._generate_warnings(blueprint, documents)
        metadata['recommendations'] = self._generate_recommendations(blueprint, documents)
    
    def _compile_source_metadata(self, documents: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Compile metadata about source documents
        """
        total_count = 0
        by_type = {}
        canon_distribution = {}
        life_phase_coverage = set()
        document_ids = []
        
        for doc_type, docs in documents.items():
            if doc_type == 'narrative':
                type_count = sum(len(phase_docs) for phase_docs in docs.values())
                by_type[doc_type] = type_count
                total_count += type_count
                
                for phase, phase_docs in docs.items():
                    if phase_docs:
                        life_phase_coverage.add(phase)
                    for doc in phase_docs:
                        document_ids.append(doc['id'])
                        canon_status = doc['canon_status']
                        canon_distribution[canon_status] = canon_distribution.get(canon_status, 0) + 1
            else:
                by_type[doc_type] = len(docs)
                total_count += len(docs)
                for doc in docs:
                    document_ids.append(doc['id'])
                    canon_status = doc['canon_status']
                    canon_distribution[canon_status] = canon_distribution.get(canon_status, 0) + 1
        
        return {
            'total_count': total_count,
            'by_type': by_type,
            'canon_distribution': canon_distribution,
            'life_phase_coverage': list(life_phase_coverage),
            'document_ids': document_ids
        }
    
    # Helper methods for content extraction
    def _extract_life_events(self, content: str) -> List[str]:
        """Extract life events from narrative content"""
        # Simple pattern matching for events
        event_patterns = [
            r'when I (\w+)', r'I remember (\w+)', r'the time I (\w+)',
            r'during (\w+)', r'after I (\w+)', r'before I (\w+)'
        ]
        
        events = []
        for pattern in event_patterns:
            matches = re.findall(pattern, content.lower())
            events.extend(matches[:3])  # Limit to prevent noise
        
        return events[:10]  # Max 10 events per document
    
    def _extract_narrative_themes(self, content: str) -> List[str]:
        """Extract themes from narrative content"""
        theme_keywords = {
            'growth': ['growth', 'learning', 'development', 'change', 'evolution'],
            'struggle': ['difficult', 'hard', 'challenge', 'struggle', 'overcome'],
            'relationships': ['friend', 'family', 'love', 'relationship', 'together'],
            'achievement': ['success', 'accomplished', 'achieved', 'proud', 'won'],
            'loss': ['lost', 'death', 'ended', 'gone', 'grief'],
            'discovery': ['discovered', 'realized', 'found', 'learned', 'understood']
        }
        
        themes = []
        content_lower = content.lower()
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _extract_formative_experiences(self, content: str) -> List[str]:
        """Extract formative experiences from core canon content"""
        formative_indicators = [
            'life-changing', 'never forgot', 'always remember', 'shaped me',
            'realized', 'understood', 'learned', 'changed everything'
        ]
        
        sentences = content.split('.')
        formative_experiences = []
        
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in formative_indicators):
                formative_experiences.append(sentence.strip()[:100])  # Truncate long sentences
        
        return formative_experiences[:5]  # Max 5 per document
    
    def _identify_core_narratives(self, narrative_docs: Dict[str, List[Dict]]) -> List[str]:
        """Identify recurring narratives across life phases"""
        # This would be more sophisticated in a full implementation
        all_themes = []
        for phase_docs in narrative_docs.values():
            for doc in phase_docs:
                themes = self._extract_narrative_themes(doc['content'])
                all_themes.extend(themes)
        
        # Find most common themes as core narratives
        from collections import Counter
        theme_counts = Counter(all_themes)
        return [theme for theme, count in theme_counts.most_common(3)]
    
    def _extract_education_info(self, content: str) -> Dict[str, List]:
        """Extract education information from content"""
        education_data = {'degrees': [], 'courses': [], 'certifications': []}
        
        # Simple pattern matching for education - would be more sophisticated in production
        degree_patterns = [
            r'(bachelor|master|phd|doctorate|associate).*?in ([\w\s]+)',
            r'(ba|bs|ma|ms|phd).*?in ([\w\s]+)',
            r'degree in ([\w\s]+)'
        ]
        
        content_lower = content.lower()
        for pattern in degree_patterns:
            matches = re.findall(pattern, content_lower)
            for match in matches:
                if isinstance(match, tuple):
                    education_data['degrees'].append(f"{match[0]} in {match[1]}")
                else:
                    education_data['degrees'].append(match)
        
        return education_data
    
    def _extract_career_info(self, content: str) -> Dict[str, List]:
        """Extract career information from content"""
        career_data = {'positions': [], 'skills': [], 'domains': []}
        
        # Simple extraction - would be more sophisticated in production
        position_patterns = [
            r'worked as ([\w\s]+)', r'job as ([\w\s]+)', r'position as ([\w\s]+)',
            r'(manager|director|analyst|engineer|developer|consultant)'
        ]
        
        content_lower = content.lower()
        for pattern in position_patterns:
            matches = re.findall(pattern, content_lower)
            career_data['positions'].extend(matches[:3])
        
        return career_data
    
    def _extract_cultural_knowledge(self, content: str) -> Dict[str, List]:
        """Extract cultural knowledge indicators"""
        cultural = {
            'languages': [],
            'literature': [],
            'arts': [],
            'philosophy': [],
            'sciences': []
        }
        
        # Simple keyword detection - would be more sophisticated in production
        language_indicators = ['speak', 'fluent', 'language', 'bilingual']
        literature_indicators = ['book', 'novel', 'author', 'read', 'literature']
        
        content_lower = content.lower()
        
        if any(indicator in content_lower for indicator in language_indicators):
            cultural['languages'].append('multilingual_evidence')
        
        if any(indicator in content_lower for indicator in literature_indicators):
            cultural['literature'].append('literary_engagement')
        
        return cultural
    
    def _compile_all_text(self, documents: Dict[str, List[Dict]]) -> str:
        """Compile all document text for analysis"""
        all_text = ""
        
        for doc_type, docs in documents.items():
            if doc_type == 'narrative':
                for phase_docs in docs.values():
                    all_text += " ".join([doc['content'] for doc in phase_docs])
            else:
                all_text += " ".join([doc['content'] for doc in docs])
        
        return all_text
    
    def _extract_big_five_traits(self, content: str) -> Dict[str, float]:
        """Extract Big Five personality traits from content"""
        # Simplified trait extraction - would use more sophisticated NLP in production
        trait_keywords = {
            'openness': ['creative', 'imaginative', 'curious', 'open', 'artistic'],
            'conscientiousness': ['organized', 'disciplined', 'responsible', 'thorough'],
            'extraversion': ['outgoing', 'social', 'talkative', 'energetic', 'assertive'],
            'agreeableness': ['kind', 'cooperative', 'trusting', 'helpful', 'compassionate'],
            'neuroticism': ['anxious', 'worried', 'emotional', 'stressed', 'nervous']
        }
        
        traits = {}
        content_lower = content.lower()
        
        for trait, keywords in trait_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            traits[trait] = min(1.0, score / 10)  # Normalize to 0-1
        
        return traits
    
    def _extract_communication_style(self, content: str) -> Dict[str, str]:
        """Extract communication style indicators"""
        # Simple communication style detection
        formal_indicators = ['therefore', 'furthermore', 'moreover', 'consequently']
        casual_indicators = ['yeah', 'cool', 'awesome', 'totally', 'like']
        
        content_lower = content.lower()
        formal_count = sum(1 for indicator in formal_indicators if indicator in content_lower)
        casual_count = sum(1 for indicator in casual_indicators if indicator in content_lower)
        
        if formal_count > casual_count:
            formality = 'formal'
        elif casual_count > formal_count:
            formality = 'casual'
        else:
            formality = 'moderate'
        
        return {'formality_level': formality}
    
    def _score_archetypes(self, content: str) -> Dict[str, float]:
        """Score Jungian archetypes based on content"""
        archetype_keywords = {
            'The Sage': ['wise', 'knowledge', 'understanding', 'truth', 'insight'],
            'The Caregiver': ['help', 'care', 'support', 'nurture', 'protect'],
            'The Creator': ['create', 'build', 'make', 'design', 'artistic'],
            'The Hero': ['challenge', 'overcome', 'achieve', 'victory', 'strength'],
            'The Lover': ['love', 'passion', 'relationship', 'beauty', 'connection'],
            'The Explorer': ['adventure', 'discover', 'journey', 'freedom', 'new']
        }
        
        scores = {}
        content_lower = content.lower()
        
        for archetype, keywords in archetype_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            scores[archetype] = score / len(keywords)  # Normalize
        
        return scores
    
    def _infer_learning_style(self, documents: Dict[str, List[Dict]]) -> str:
        """Infer learning style from education and career patterns"""
        # Simple inference based on document types and content
        if documents['education']:
            return 'formal_academic'
        elif documents['career']:
            return 'experiential_professional'
        else:
            return 'self_directed'
    
    def _calculate_boundary_clarity(self, blueprint: LayeredPersonaBlueprint) -> float:
        """Calculate how clearly defined the knowledge boundaries are"""
        bounds = blueprint.schema['knowledge_identity']['knowledge_boundaries']
        
        total_domains = len(bounds['deep_expertise']) + len(bounds['surface_knowledge']) + len(bounds['unknown_domains'])
        
        if total_domains == 0:
            return 0.0
        
        # Higher clarity when we have good coverage of known/unknown domains
        clarity = min(1.0, total_domains / 15)  # Normalize against expected domain count
        
        return clarity
    
    def _generate_warnings(self, blueprint: LayeredPersonaBlueprint, documents: Dict[str, List[Dict]]) -> List[str]:
        """Generate warnings about potential issues"""
        warnings = []
        
        # Check for gaps in life phases
        narrative_phases = blueprint.schema['narrative_identity']['life_phases']
        empty_phases = [phase for phase, data in narrative_phases.items() if not data['events']]
        
        if len(empty_phases) > 2:
            warnings.append(f"Missing narrative data for life phases: {', '.join(empty_phases)}")
        
        # Check for knowledge boundaries
        bounds = blueprint.schema['knowledge_identity']['knowledge_boundaries']
        if not bounds['deep_expertise']:
            warnings.append("No areas of deep expertise identified - persona may lack knowledge boundaries")
        
        return warnings
    
    def _generate_recommendations(self, blueprint: LayeredPersonaBlueprint, documents: Dict[str, List[Dict]]) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []
        
        # Recommend more education/career docs if missing
        if not documents['education']:
            recommendations.append("Add education documents to establish formal knowledge boundaries")
        
        if not documents['career']:
            recommendations.append("Add career documents to establish professional expertise")
        
        # Recommend narrative coverage
        narrative_phases = blueprint.schema['narrative_identity']['life_phases']
        sparse_phases = [phase for phase, data in narrative_phases.items() if len(data['events']) < 2]
        
        if sparse_phases:
            recommendations.append(f"Add more narrative content for: {', '.join(sparse_phases)}")
        
        return recommendations
