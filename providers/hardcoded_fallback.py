"""
Hardcoded Fallback Provider
The "never fail" provider that always returns intelligent responses

This provider ensures VALIS always works, even when all AI systems are down.
Uses persona JSON data to generate intelligent responses based on tone, background, and common phrases.
"""

import re
import random
from typing import Dict, Optional, Any, List
from providers.base_provider import BaseProvider, register_provider

@register_provider("hardcoded_fallback")
class HardcodedFallbackProvider(BaseProvider):
    """Hardcoded fallback provider that never fails and uses persona data"""
    
    def __init__(self):
        super().__init__()
        self.name = "Hardcoded Fallback"
        self.cost = "FREE"
        self._load_response_templates()
        
    async def is_available(self) -> bool:
        """Always available - that's the point!"""
        return True
    
    def _load_response_templates(self):
        """Load response templates that can be filled with persona data"""
        self.response_templates = {
            "greetings": [
                "Hello! I'm {name}. {description}. How can I help you today?",
                "Hi there! I'm {name}. With my background in {background_brief}, I'm here to assist you.",
                "Hello! {name} here. {approach_brief} What brings you to me?"
            ],
            "conflict": [
                "{greeting} {approach_brief} Tell me more about the situation.",
                "I understand you're dealing with a conflict. {approach_brief} What's happening?",
                "{common_phrase} Let's work through this challenge together."
            ],
            "stress": [
                "I can see you're feeling stressed. {approach_brief} What's your biggest stressor?",
                "{greeting} Stress is something I help with regularly. {common_phrase}",
                "Work stress is really common. {approach_brief} Let's talk about it."
            ],
            "general": [
                "{greeting} {common_phrase} What would you like to explore?",
                "I'm here to help. {approach_brief} What's on your mind?",
                "{common_phrase} How can I support you today?"
            ]
        }        
        # Keywords for matching user messages to response categories
        self.keywords = {
            "greetings": ["hello", "hi", "hey", "introduce", "who are you", "nice to meet"],
            "conflict": ["conflict", "argument", "disagreement", "fight", "dispute", "tension"],
            "stress": ["stressed", "pressure", "overwhelmed", "anxious", "burnout", "tired"],
            "general": ["help", "support", "advice", "guidance", "assist"]
        }

    async def get_response(self, persona: Dict[str, Any], message: str, session_id: Optional[str] = None, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get a hardcoded response using persona JSON data (DEV-501)"""
        
        try:
            # SPRINT 2.9: DEV-502 - Handle unknown personas gracefully
            persona_id = persona.get("id", "unknown")
            persona_name = persona.get("name", "Unknown")
            
            # Check if this is a known persona with proper data
            has_minimal_data = persona.get("tone") and persona.get("approach")
            
            if persona_id == "unknown" or not has_minimal_data:
                return self._handle_unknown_persona(persona_id, persona_name, message)
            
            # NEURAL CONTEXT AWARENESS (Task 2.3)
            # Check for neural context from provider cascade
            neural_context = None
            context_awareness = ""
            
            if context and "neural_context" in context:
                neural_context = context["neural_context"]
                
                # Create context awareness message
                if neural_context.get("conversation_summary"):
                    context_awareness = f" I remember our previous conversations: {neural_context['conversation_summary'][:200]}..."
                
                # Add session continuity if available
                if context.get("session_info"):
                    session_info = context["session_info"]
                    context_awareness += f" This is our {session_info['request_count']} interaction in this session."
            
            # Categorize the message
            category = self._categorize_message(message)
            
            # Generate response using persona data instead of hardcoded patterns
            response = self._generate_persona_response(persona, category, message)
            
            # Enhance response with neural context if available
            if context_awareness:
                enhanced_response = response.replace(".", f".{context_awareness}", 1)
            else:
                enhanced_response = response
            
            return {
                "success": True,
                "response": enhanced_response,
                "provider": "Hardcoded Fallback",
                "cost": "FREE",
                "category_detected": category,
                "neural_context_used": bool(neural_context),
                "context_handoff_successful": bool(context_awareness),
                "persona_data_used": True
            }            
        except Exception as e:
            # Even the fallback has a fallback! (DEV-502 - graceful handling)
            return {
                "success": True,
                "response": "I'm here to help you. Could you tell me more about what you're looking for?",
                "provider": "Hardcoded Fallback (Emergency)",
                "cost": "FREE",
                "error_handled": str(e),
                "persona_data_used": False
            }

    def _generate_persona_response(self, persona: Dict[str, Any], category: str, message: str) -> str:
        """
        SPRINT 2.9: Generate response using persona JSON data with perfect authenticity (DEV-501)
        
        Transforms generic responses into persona-specific patterns that maintain character integrity!
        """
        
        # Extract persona characteristics
        name = persona.get("name", "Assistant")
        persona_id = persona.get("id", "unknown")
        tone = persona.get("tone", "helpful and professional")
        background = persona.get("background", "")
        approach = persona.get("approach", "I help solve problems thoughtfully.")
        specialties = persona.get("specialties", [])
        
        # Get language patterns for authentic voice
        language_patterns = persona.get("language_patterns", {})
        common_phrases = language_patterns.get("common_phrases", [])
        question_style = language_patterns.get("question_style", "thoughtful")
        
        # Select persona-appropriate response pattern based on category and personality
        response_templates = self._get_persona_response_templates(persona_id, tone, common_phrases)
        
        # Get appropriate template for the category
        template_category = category if category in response_templates else "general"
        templates = response_templates[template_category]
        
        # Build template variables for authentic persona voice
        template_vars = {
            "name": name,
            "persona_greeting": self._get_persona_greeting(name, tone, common_phrases),
            "approach_phrase": self._get_approach_phrase(approach, tone),
            "specialty_mention": self._get_specialty_mention(specialties),
            "common_phrase": random.choice(common_phrases) if common_phrases else "How can I help?",
            "tone_modifier": self._get_tone_modifier(tone)
        }
        
        # Select random template and fill with persona data
        template = random.choice(templates)
        
        try:
            response = template.format(**template_vars)
        except KeyError as e:
            # Emergency fallback with persona characteristics preserved
            greeting = template_vars["persona_greeting"]
            phrase = template_vars["common_phrase"]
            response = f"{greeting} {phrase}"
        
        return response    
    def _categorize_message(self, message: str) -> str:
        """Categorize user message based on keywords"""
        message_lower = message.lower()
        
        # Count keyword matches for each category
        category_scores = {}
        for category, keywords in self.keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score, or 'general' as default (DEV-502)
        if category_scores:
            return max(category_scores, key=category_scores.get)
        else:
            return "general"  # Changed from 'greetings' to 'general' for better unknown handling
    def _get_persona_greeting(self, name: str, tone: str, common_phrases: List[str]) -> str:
        """Generate persona-appropriate greeting based on their personality"""
        tone_lower = tone.lower()
        
        if "energetic" in tone_lower or "motivational" in tone_lower:
            greetings = [f"Hey there! I'm {name}!", f"Hi! {name} here, ready to help!", f"Hello! I'm {name} and I'm excited to work with you!"]
        elif "analytical" in tone_lower or "thoughtful" in tone_lower:
            greetings = [f"Hello, I'm {name}.", f"Hi there, {name} here.", f"Good to meet you - I'm {name}."]
        elif "direct" in tone_lower or "focused" in tone_lower:
            greetings = [f"I'm {name}.", f"Hi, {name} here.", f"{name} speaking."]
        elif "zen" in tone_lower or "calm" in tone_lower:
            greetings = [f"Hello, I'm {name}.", f"Greetings, {name} here.", f"Peace, I'm {name}."]
        else:
            greetings = [f"Hello! I'm {name}.", f"Hi there, I'm {name}.", f"Nice to meet you, I'm {name}."]
        
        return random.choice(greetings)
    
    def _get_approach_phrase(self, approach: str, tone: str) -> str:
        """Convert approach description to first-person authentic voice"""
        # Convert third-person approach to first-person
        approach_cleaned = approach.replace("Alex uses", "I use").replace("Sam uses", "I use").replace("Emma uses", "I use")
        approach_cleaned = approach_cleaned.replace("They help", "I help").replace("clients", "you")
        
        # Truncate if too long
        if len(approach_cleaned) > 100:
            approach_cleaned = approach_cleaned[:97] + "..."
        
        return approach_cleaned
    
    def _get_specialty_mention(self, specialties: List[str]) -> str:
        """Create natural mention of specialties"""
        if not specialties:
            return ""
        
        if len(specialties) == 1:
            return f"I specialize in {specialties[0].lower()}."
        elif len(specialties) <= 3:
            specialty_list = ", ".join(specialties[:-1]) + f", and {specialties[-1]}"
            return f"My areas of focus include {specialty_list.lower()}."
        else:
            # Just mention first 2 for brevity
            return f"I focus on {specialties[0].lower()}, {specialties[1].lower()}, and more."
    
    def _get_tone_modifier(self, tone: str) -> str:
        """Get tone-appropriate response modifier"""
        tone_lower = tone.lower()
        
        if "energetic" in tone_lower or "motivational" in tone_lower:
            return "Let's dive in!"
        elif "analytical" in tone_lower:
            return "Let's examine this systematically."
        elif "direct" in tone_lower:
            return "Let's get to the point."
        elif "zen" in tone_lower or "calm" in tone_lower:
            return "Let's explore this together."
        else:
            return "How can I assist you?"

    def _get_persona_response_templates(self, persona_id: str, tone: str, common_phrases: List[str]) -> Dict[str, List[str]]:
        """
        SPRINT 2.9: Create persona-specific response templates that maintain character authenticity
        """
        # Base templates that work for all personas
        base_templates = {
            "general": [
                "{persona_greeting} {common_phrase}",
                "{persona_greeting} {approach_phrase} {tone_modifier}",
                "{persona_greeting} {specialty_mention} {common_phrase}",
                "{persona_greeting} {tone_modifier}"
            ],
            "greeting": [
                "{persona_greeting} {common_phrase}",
                "{persona_greeting} {tone_modifier}",
                "{persona_greeting} Great to connect with you!"
            ],
            "question": [
                "{persona_greeting} {common_phrase}",
                "{persona_greeting} {approach_phrase}",
                "That's a great question! {approach_phrase} {tone_modifier}"
            ],
            "help": [
                "{persona_greeting} {specialty_mention} {tone_modifier}",
                "{persona_greeting} {approach_phrase} {common_phrase}",
                "I'm here to help! {approach_phrase}"
            ]
        }
        
        # Persona-specific enhancements based on their unique characteristics
        if persona_id == "coach_emma":
            base_templates["motivation"] = [
                "{persona_greeting} {common_phrase} You've got this!",
                "{persona_greeting} I believe in your potential! {tone_modifier}",
                "I can hear the determination in your question! {approach_phrase}"
            ]
            base_templates["general"].extend([
                "{persona_greeting} I'm excited to support your growth! {common_phrase}",
                "{persona_greeting} Your potential is unlimited! {tone_modifier}"
            ])
        elif persona_id == "advisor_alex":
            base_templates["analysis"] = [
                "{persona_greeting} {common_phrase} {approach_phrase}",
                "{persona_greeting} {specialty_mention} {tone_modifier}",
                "Interesting question. {approach_phrase} {common_phrase}"
            ]
            base_templates["general"].extend([
                "{persona_greeting} {approach_phrase} {common_phrase}",
                "{persona_greeting} {specialty_mention} What factors should we consider?"
            ])
        elif persona_id == "guide_sam":
            base_templates["goals"] = [
                "{persona_greeting} {common_phrase} {tone_modifier}",
                "{persona_greeting} {approach_phrase} What's your specific target?",
                "I hear you're ready to take action. {approach_phrase}"
            ]
            base_templates["general"].extend([
                "{persona_greeting} {common_phrase} Let's get clear on what you want to achieve.",
                "{persona_greeting} {approach_phrase} {tone_modifier}"
            ])
        
        return base_templates

    def _handle_unknown_persona(self, persona_id: str, persona_name: str, message: str) -> Dict[str, Any]:
        """
        SPRINT 2.9: DEV-502 - Handle unknown personas gracefully without defaulting to Jane
        """
        # List of available personas (could be made dynamic by reading personas directory)
        available_personas = [
            "jane (HR Professional)",
            "advisor_alex (Strategic Advisor)", 
            "guide_sam (Goal-Focused Coach)",
            "coach_emma (Motivational Coach)",
            "billy_corgan (Alternative Music Perspective)"
        ]
        
        persona_list = ", ".join(available_personas)
        
        if persona_id == "unknown" or not persona_id:
            unknown_message = (
                f"Hello! I don't recognize the persona you're trying to reach. "
                f"I have access to these personas: {persona_list}. "
                f"Which one would you like to interact with?"
            )
        else:
            unknown_message = (
                f"I apologize, but I don't recognize the persona '{persona_id}'. "
                f"Available personas include: {persona_list}. "
                f"Would you like to connect with one of them instead?"
            )
        
        return {
            "success": True,
            "response": unknown_message,
            "provider": "Hardcoded Fallback",
            "cost": "FREE",
            "persona_found": False,
            "available_personas": available_personas,
            "requested_persona": persona_id
        }
