"""
VALIS Mr. Fission - Fusion Engine
Converts parsed features into structured Persona Blueprints
"""

import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import math

class PersonaBlueprint:
    """
    Structured persona blueprint schema
    """
    
    def __init__(self):
        self.schema = {
            "id": str(uuid.uuid4()),
            "name": "",
            "type": "interface",  # interface, companion, specialist
            "domain": [],
            "archetypes": [],
            "memory_mode": "canonical+reflective",
            "dreams_enabled": True,
            "replay_mode": "standard",
            "source_material": [],
            "traits": {
                "tone": "",
                "symbolic_awareness": True,
                "personality_scores": {},
                "emotional_baseline": {},
                "communication_style": {}
            },
            "boundaries": {
                "allow_direct_advice": True,
                "use_mystical_language": False,
                "confidence_level": "moderate",
                "formality_level": "casual"
            },
            "memory_seeds": [],
            "created_at": datetime.now().isoformat(),
            "fusion_metadata": {
                "source_files": [],
                "fusion_confidence": 0.0,
                "dominant_traits": [],
                "suggested_improvements": []
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return self.schema
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.schema, indent=indent, default=str)
    
    def save(self, filepath: str) -> None:
        """Save blueprint to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

class FissionFusionEngine:
    """
    Converts extracted features into deployable persona blueprints
    """
    
    def __init__(self):
        # Trait mapping thresholds
        self.trait_thresholds = {
            "high": 0.015,    # Strong presence of trait
            "moderate": 0.008, # Moderate presence
            "low": 0.003      # Slight presence
        }
        
        # Archetype confidence thresholds
        self.archetype_thresholds = {
            "primary": 0.012,   # Primary archetype
            "secondary": 0.008, # Secondary influence
            "tertiary": 0.004   # Slight influence
        }
        
        # Domain mapping based on content analysis
        self.domain_keywords = {
            "therapy": ["therapy", "counseling", "mental health", "psychology", "healing"],
            "coaching": ["coaching", "development", "growth", "goals", "leadership"],
            "education": ["teaching", "learning", "education", "student", "knowledge"],
            "creative": ["art", "design", "creative", "imagination", "artistic"],
            "technical": ["technology", "programming", "engineering", "technical", "software"],
            "business": ["business", "corporate", "management", "strategy", "finance"],
            "spiritual": ["spiritual", "meditation", "mindfulness", "philosophy", "wisdom"],
            "health": ["health", "wellness", "fitness", "nutrition", "medical"]
        }
    
    def fuse_persona(self, ingestion_results: Dict[str, Any], persona_name: str = None) -> PersonaBlueprint:
        """
        Main fusion method - converts ingestion results into persona blueprint
        """
        blueprint = PersonaBlueprint()
        
        # Set basic info
        blueprint.schema["name"] = persona_name or f"persona_{uuid.uuid4().hex[:8]}"
        blueprint.schema["source_material"] = self._extract_source_files(ingestion_results)
        
        # Process combined features if available, otherwise process first file
        if "combined_features" in ingestion_results:
            features = ingestion_results["combined_features"]
            blueprint.schema["fusion_metadata"]["source_files"] = list(ingestion_results["files"].keys())
        else:
            # Single file processing
            first_file = next(iter(ingestion_results["files"].values()))
            features = first_file.get("features", {})
            blueprint.schema["fusion_metadata"]["source_files"] = [first_file.get("source_file", "unknown")]
        
        # Fuse personality traits
        self._fuse_personality_traits(blueprint, features)
        
        # Fuse archetypes
        self._fuse_archetypes(blueprint, features)
        
        # Fuse emotional tone
        self._fuse_emotional_baseline(blueprint, features)
        
        # Fuse communication style
        self._fuse_communication_style(blueprint, features)
        
        # Determine domains
        self._determine_domains(blueprint, features, ingestion_results)
        
        # Extract memory seeds
        self._extract_memory_seeds(blueprint, ingestion_results)
        
        # Set boundaries and preferences
        self._set_boundaries(blueprint, features)
        
        # Calculate fusion confidence
        self._calculate_fusion_confidence(blueprint, features)
        
        # Generate suggestions
        self._generate_suggestions(blueprint, features)
        
        return blueprint
    
    def _extract_source_files(self, ingestion_results: Dict[str, Any]) -> List[str]:
        """Extract list of source files"""
        if "files" in ingestion_results:
            return list(ingestion_results["files"].keys())
        return []
    
    def _fuse_personality_traits(self, blueprint: PersonaBlueprint, features: Dict[str, Any]) -> None:
        """Convert personality trait scores into structured traits"""
        if "personality_traits" not in features:
            return
        
        trait_scores = features["personality_traits"]
        personality = {}
        dominant_traits = []
        
        for trait, score in trait_scores.items():
            if score >= self.trait_thresholds["high"]:
                personality[trait] = "high"
                dominant_traits.append(trait)
            elif score >= self.trait_thresholds["moderate"]:
                personality[trait] = "moderate"
            elif score >= self.trait_thresholds["low"]:
                personality[trait] = "low"
        
        blueprint.schema["traits"]["personality_scores"] = personality
        blueprint.schema["fusion_metadata"]["dominant_traits"] = dominant_traits
        
        # Generate tone description
        tone_parts = []
        
        if personality.get("agreeableness") in ["high", "moderate"]:
            tone_parts.append("warm")
        if personality.get("conscientiousness") in ["high", "moderate"]:
            tone_parts.append("thoughtful")
        if personality.get("openness") in ["high", "moderate"]:
            tone_parts.append("creative")
        if personality.get("extraversion") == "high":
            tone_parts.append("energetic")
        elif personality.get("introversion") in ["high", "moderate"]:
            tone_parts.append("reflective")
        if personality.get("analytical") in ["high", "moderate"]:
            tone_parts.append("precise")
        if personality.get("intuitive") in ["high", "moderate"]:
            tone_parts.append("intuitive")
        
        blueprint.schema["traits"]["tone"] = ", ".join(tone_parts) if tone_parts else "balanced"
    
    def _fuse_archetypes(self, blueprint: PersonaBlueprint, features: Dict[str, Any]) -> None:
        """Determine primary and secondary archetypes"""
        if "archetypes" not in features:
            return
        
        archetype_scores = features["archetypes"]
        selected_archetypes = []
        
        # Sort by score and select top archetypes
        sorted_archetypes = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)
        
        for archetype, score in sorted_archetypes:
            if score >= self.archetype_thresholds["primary"] and len(selected_archetypes) == 0:
                selected_archetypes.append(archetype)
            elif score >= self.archetype_thresholds["secondary"] and len(selected_archetypes) < 2:
                selected_archetypes.append(archetype)
            elif score >= self.archetype_thresholds["tertiary"] and len(selected_archetypes) < 3:
                selected_archetypes.append(archetype)
        
        blueprint.schema["archetypes"] = selected_archetypes
    
    def _fuse_emotional_baseline(self, blueprint: PersonaBlueprint, features: Dict[str, Any]) -> None:
        """Set emotional baseline from tone analysis"""
        if "emotional_tone" not in features:
            return
        
        emotional_tone = features["emotional_tone"]
        baseline = {}
        
        for emotion, score in emotional_tone.items():
            if score >= 0.01:  # Significant emotional presence
                baseline[emotion] = score
        
        blueprint.schema["traits"]["emotional_baseline"] = baseline
    
    def _fuse_communication_style(self, blueprint: PersonaBlueprint, features: Dict[str, Any]) -> None:
        """Determine communication style from writing analysis"""
        if "writing_style" not in features:
            return
        
        writing_style = features["writing_style"]
        comm_style = {}
        
        # Analyze sentence complexity
        avg_length = writing_style.get("avg_sentence_length", 0)
        if avg_length > 20:
            comm_style["sentence_style"] = "complex"
        elif avg_length > 10:
            comm_style["sentence_style"] = "moderate"
        else:
            comm_style["sentence_style"] = "concise"
        
        # Analyze personal pronoun usage
        first_person = writing_style.get("first_person_usage", 0)
        if first_person > 10:
            comm_style["perspective"] = "personal"
        else:
            comm_style["perspective"] = "general"
        
        # Analyze expressiveness
        questions = writing_style.get("question_count", 0)
        exclamations = writing_style.get("exclamation_count", 0)
        total_expression = questions + exclamations
        
        if total_expression > 5:
            comm_style["expressiveness"] = "high"
        elif total_expression > 2:
            comm_style["expressiveness"] = "moderate"
        else:
            comm_style["expressiveness"] = "restrained"
        
        # Complexity score
        complexity = writing_style.get("complexity_score", 0)
        if complexity > 1.5:
            comm_style["vocabulary"] = "sophisticated"
        elif complexity > 1.2:
            comm_style["vocabulary"] = "moderate"
        else:
            comm_style["vocabulary"] = "accessible"
        
        blueprint.schema["traits"]["communication_style"] = comm_style
    
    def _determine_domains(self, blueprint: PersonaBlueprint, features: Dict[str, Any], 
                          ingestion_results: Dict[str, Any]) -> None:
        """Determine expertise domains from content analysis"""
        domains = []
        
        # Analyze all text content for domain keywords
        all_text = ""
        
        # Collect text from all sources
        for file_name, file_data in ingestion_results.get("files", {}).items():
            file_features = file_data.get("features", {})
            if "content" in file_features:
                all_text += " " + file_features["content"]
        
        all_text = all_text.lower()
        
        # Score domains based on keyword presence
        domain_scores = {}
        for domain, keywords in self.domain_keywords.items():
            score = sum(all_text.count(keyword) for keyword in keywords)
            if score > 0:
                domain_scores[domain] = score
        
        # Select top domains
        if domain_scores:
            sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
            domains = [domain for domain, score in sorted_domains[:3] if score >= 2]
        
        blueprint.schema["domain"] = domains if domains else ["general"]
    
    def _extract_memory_seeds(self, blueprint: PersonaBlueprint, ingestion_results: Dict[str, Any]) -> None:
        """Extract key memories/experiences to seed the persona"""
        memory_seeds = []
        
        for file_name, file_data in ingestion_results.get("files", {}).items():
            file_features = file_data.get("features", {})
            
            # Extract key phrases as memory seeds
            if "key_phrases" in file_features:
                for phrase, count in file_features["key_phrases"][:5]:  # Top 5 phrases
                    if len(phrase.strip()) > 3 and count > 1:
                        memory_seeds.append({
                            "type": "key_concept",
                            "content": phrase.strip(),
                            "source": file_name,
                            "importance": count
                        })
            
            # Extract named entities as memories
            if "named_entities" in file_features:
                for entity, entity_type in file_features["named_entities"][:10]:  # Top 10 entities
                    memory_seeds.append({
                        "type": "named_entity",
                        "content": f"{entity} ({entity_type})",
                        "source": file_name,
                        "entity_type": entity_type
                    })
            
            # Extract image descriptions as visual memories
            if file_features.get("type") == "image" and "top_descriptions" in file_features:
                for desc in file_features["top_descriptions"][:3]:
                    memory_seeds.append({
                        "type": "visual_memory",
                        "content": desc["description"],
                        "source": file_name,
                        "confidence": desc["confidence"]
                    })
        
        blueprint.schema["memory_seeds"] = memory_seeds
    
    def _set_boundaries(self, blueprint: PersonaBlueprint, features: Dict[str, Any]) -> None:
        """Set persona boundaries based on analyzed traits"""
        boundaries = blueprint.schema["boundaries"]
        
        # Adjust based on personality traits
        personality = blueprint.schema["traits"].get("personality_scores", {})
        
        # Confidence level
        if personality.get("conscientiousness") == "high":
            boundaries["confidence_level"] = "high"
        elif personality.get("neuroticism") == "high":
            boundaries["confidence_level"] = "cautious"
        
        # Formality level
        comm_style = blueprint.schema["traits"].get("communication_style", {})
        if comm_style.get("vocabulary") == "sophisticated":
            boundaries["formality_level"] = "formal"
        elif comm_style.get("expressiveness") == "high":
            boundaries["formality_level"] = "casual"
        
        # Mystical language based on archetypes
        archetypes = blueprint.schema["archetypes"]
        if "The Magician" in archetypes or "The Sage" in archetypes:
            boundaries["use_mystical_language"] = True
        
        # Direct advice based on domains and archetypes
        domains = blueprint.schema["domain"]
        if "therapy" in domains or "coaching" in domains or "The Caregiver" in archetypes:
            boundaries["allow_direct_advice"] = True
    
    def _calculate_fusion_confidence(self, blueprint: PersonaBlueprint, features: Dict[str, Any]) -> None:
        """Calculate confidence score for the fusion process"""
        confidence_factors = []
        
        # Text content availability
        if "word_count" in features:
            word_count = features["word_count"]
            if word_count > 1000:
                confidence_factors.append(0.3)
            elif word_count > 500:
                confidence_factors.append(0.2)
            elif word_count > 100:
                confidence_factors.append(0.1)
        
        # Personality trait detection
        personality_count = len(blueprint.schema["traits"].get("personality_scores", {}))
        confidence_factors.append(min(personality_count * 0.05, 0.2))
        
        # Archetype detection
        archetype_count = len(blueprint.schema["archetypes"])
        confidence_factors.append(min(archetype_count * 0.1, 0.2))
        
        # Domain detection
        domain_count = len(blueprint.schema["domain"])
        confidence_factors.append(min(domain_count * 0.1, 0.15))
        
        # Memory seed richness
        memory_count = len(blueprint.schema["memory_seeds"])
        confidence_factors.append(min(memory_count * 0.02, 0.15))
        
        total_confidence = sum(confidence_factors)
        blueprint.schema["fusion_metadata"]["fusion_confidence"] = min(total_confidence, 1.0)
    
    def _generate_suggestions(self, blueprint: PersonaBlueprint, features: Dict[str, Any]) -> None:
        """Generate suggestions for improving the persona"""
        suggestions = []
        
        confidence = blueprint.schema["fusion_metadata"]["fusion_confidence"]
        
        if confidence < 0.3:
            suggestions.append("Consider adding more source material for better personality detection")
        
        if not blueprint.schema["archetypes"]:
            suggestions.append("No clear archetypes detected - consider adding more descriptive content")
        
        if len(blueprint.schema["domain"]) == 1 and blueprint.schema["domain"][0] == "general":
            suggestions.append("No specific expertise domains detected - consider adding professional/interest content")
        
        if len(blueprint.schema["memory_seeds"]) < 5:
            suggestions.append("Few memory seeds extracted - consider adding more experiential content")
        
        personality_scores = blueprint.schema["traits"].get("personality_scores", {})
        if len(personality_scores) < 3:
            suggestions.append("Limited personality traits detected - consider adding more personal writing samples")
        
        blueprint.schema["fusion_metadata"]["suggested_improvements"] = suggestions
    
    def preview_persona(self, blueprint: PersonaBlueprint) -> Dict[str, Any]:
        """Generate a preview of the persona for user review"""
        preview = {
            "name": blueprint.schema["name"],
            "summary": self._generate_summary(blueprint),
            "sample_quote": self._generate_sample_quote(blueprint),
            "sample_response": self._generate_sample_response(blueprint),
            "key_traits": self._extract_key_traits(blueprint),
            "confidence": blueprint.schema["fusion_metadata"]["fusion_confidence"],
            "suggestions": blueprint.schema["fusion_metadata"]["suggested_improvements"]
        }
        
        return preview
    
    def _generate_summary(self, blueprint: PersonaBlueprint) -> str:
        """Generate a descriptive summary of the persona"""
        name = blueprint.schema["name"]
        archetypes = blueprint.schema["archetypes"]
        domains = blueprint.schema["domain"]
        tone = blueprint.schema["traits"]["tone"]
        
        summary_parts = [f"{name} is"]
        
        if tone:
            summary_parts.append(f"a {tone} persona")
        
        if archetypes:
            archetype_str = " and ".join(archetypes)
            summary_parts.append(f"embodying {archetype_str}")
        
        if domains and domains != ["general"]:
            domain_str = ", ".join(domains)
            summary_parts.append(f"with expertise in {domain_str}")
        
        return " ".join(summary_parts) + "."
    
    def _generate_sample_quote(self, blueprint: PersonaBlueprint) -> str:
        """Generate a sample quote that represents the persona"""
        archetypes = blueprint.schema["archetypes"]
        domains = blueprint.schema["domain"]
        
        quotes = {
            "The Sage": "True wisdom comes from understanding that we never stop learning.",
            "The Caregiver": "Everyone deserves compassion and support on their journey.",
            "The Hero": "Every challenge is an opportunity to grow stronger.",
            "The Creator": "Imagination is the beginning of all meaningful change.",
            "therapy": "Healing happens when we create a safe space for authentic expression.",
            "coaching": "Your potential is unlimited when you commit to growth.",
            "spiritual": "Inner peace is the foundation of all external harmony."
        }
        
        # Select quote based on primary archetype or domain
        if archetypes:
            return quotes.get(archetypes[0], "Every moment is an opportunity for growth and understanding.")
        elif domains and domains[0] in quotes:
            return quotes[domains[0]]
        else:
            return "Authentic connection is the foundation of meaningful relationships."
    
    def _generate_sample_response(self, blueprint: PersonaBlueprint) -> str:
        """Generate a sample response to demonstrate communication style"""
        tone = blueprint.schema["traits"]["tone"]
        comm_style = blueprint.schema["traits"].get("communication_style", {})
        
        base_response = "I appreciate you sharing that with me."
        
        if "warm" in tone:
            base_response = "Thank you for trusting me with that."
        
        if comm_style.get("expressiveness") == "high":
            base_response += " It takes courage to be so open!"
        elif comm_style.get("expressiveness") == "restrained":
            base_response += " I can sense the significance of what you've shared."
        
        if comm_style.get("vocabulary") == "sophisticated":
            base_response += " This presents an intriguing opportunity for deeper exploration."
        else:
            base_response += " Let's explore this together."
        
        return base_response
    
    def _extract_key_traits(self, blueprint: PersonaBlueprint) -> List[str]:
        """Extract the most important traits for display"""
        traits = []
        
        # Add dominant personality traits
        personality = blueprint.schema["traits"].get("personality_scores", {})
        for trait, level in personality.items():
            if level in ["high", "moderate"]:
                traits.append(f"{trait.title()}: {level}")
        
        # Add primary archetype
        archetypes = blueprint.schema["archetypes"]
        if archetypes:
            traits.append(f"Primary Archetype: {archetypes[0]}")
        
        # Add domains
        domains = blueprint.schema["domain"]
        if domains and domains != ["general"]:
            traits.append(f"Domains: {', '.join(domains)}")
        
        return traits[:5]  # Limit to top 5 traits


# Example usage and testing
if __name__ == "__main__":
    print("=== VALIS MR. FISSION FUSION ENGINE ===")
    
    # Create test ingestion results
    test_results = {
        "files": {
            "jane_bio.txt": {
                "source_file": "jane_bio.txt",
                "features": {
                    "type": "text",
                    "word_count": 150,
                    "personality_traits": {
                        "agreeableness": 0.020,
                        "conscientiousness": 0.015,
                        "openness": 0.012,
                        "extraversion": 0.008
                    },
                    "archetypes": {
                        "The Caregiver": 0.018,
                        "The Sage": 0.014,
                        "The Healer": 0.010
                    },
                    "emotional_tone": {
                        "positive": 0.015,
                        "neutral": 0.008
                    },
                    "writing_style": {
                        "avg_sentence_length": 15,
                        "complexity_score": 1.3,
                        "first_person_usage": 5,
                        "question_count": 2,
                        "exclamation_count": 1
                    },
                    "key_phrases": [
                        ("caring therapist", 2),
                        ("human connection", 2),
                        ("mindfulness practices", 1)
                    ],
                    "named_entities": [
                        ("Jane", "PERSON"),
                        ("15 years", "DATE")
                    ]
                }
            }
        }
    }
    
    # Initialize fusion engine
    fusioner = FissionFusionEngine()
    
    # Fuse persona
    blueprint = fusioner.fuse_persona(test_results, "Jane")
    
    # Generate preview
    preview = fusioner.preview_persona(blueprint)
    
    print(f"Persona Name: {preview['name']}")
    print(f"Summary: {preview['summary']}")
    print(f"Sample Quote: \"{preview['sample_quote']}\"")
    print(f"Sample Response: \"{preview['sample_response']}\"")
    print(f"Confidence: {preview['confidence']:.2f}")
    
    print("\nKey Traits:")
    for trait in preview['key_traits']:
        print(f"  - {trait}")
    
    if preview['suggestions']:
        print("\nSuggestions:")
        for suggestion in preview['suggestions']:
            print(f"  - {suggestion}")
    
    print("\n=== FUSION ENGINE ONLINE ===")
