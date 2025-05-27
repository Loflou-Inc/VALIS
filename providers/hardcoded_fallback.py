"""
Hardcoded Fallback Provider
The "never fail" provider that always returns intelligent responses

This provider ensures VALIS always works, even when all AI systems are down.
Uses intelligent hardcoded responses based on keyword matching and persona context.
"""

import re
import random
from typing import Dict, Optional, Any, List

class HardcodedFallbackProvider:
    """Hardcoded fallback provider that never fails"""
    
    def __init__(self):
        self.name = "Hardcoded Fallback"
        self.cost = "FREE"
        self._load_response_database()
        
    async def is_available(self) -> bool:
        """Always available - that's the point!"""
        return True
    
    def _load_response_database(self):
        """Load hardcoded response patterns for each persona"""
        self.responses = {
            "jane": {
                "greetings": [
                    "Hi! I'm Jane from HR. How can I help you today?",
                    "Hello! Jane here. What can I assist you with?",
                    "Hi there! I'm Jane, and I'm here to support you."
                ],
                "conflict": [
                    "Conflict resolution is one of my specialities. Help me understand the situation better.",
                    "I've handled many workplace conflicts. Let's work through this step by step.",
                    "As an HR professional, I know we can find a good solution. Tell me more about what's happening."
                ],
                "stress": [
                    "Work stress is really common, and there are definitely strategies that can help.",
                    "I understand you're feeling stressed. Let's talk about some practical approaches.",
                    "Stress management is important for both performance and wellbeing. What's your biggest stressor right now?"
                ],
                "communication": [
                    "Clear communication is so important in the workplace. What specific challenge are you facing?",
                    "I help people improve their workplace communication all the time. What's going on?",
                    "Communication skills can really make a difference. Let me help you work through this."
                ]
            },            "coach_emma": {
                "greetings": [
                    "Hey there! Coach Emma here. Ready to tackle some challenges together?",
                    "Hi! I'm Coach Emma, and I love helping teams and individuals grow. What's on your mind?",
                    "Hello! Emma here. What opportunity are we working on today?"
                ],
                "leadership": [
                    "Great teams start with great leadership. What's your biggest leadership challenge right now?",
                    "Leadership is a skill we can always develop. Tell me what you're working on.",
                    "I love helping people become better leaders. What situation are you dealing with?"
                ],
                "motivation": [
                    "Motivation comes from connecting with purpose. What drives you and your team?",
                    "Let's find what lights you up! What's your team's biggest opportunity?",
                    "I've found that the best motivation comes from within. What matters most to you?"
                ],
                "teamwork": [
                    "Great teamwork doesn't happen by accident. What's happening with your team?",
                    "Team dynamics can be tricky, but they're so worth investing in. Tell me more.",
                    "I specialize in helping teams work better together. What's your situation?"
                ]
            },
            "billy_corgan": {
                "greetings": [
                    "*adjusts guitar* Hey there. Billy Corgan here. What's stirring in your creative soul?",
                    "Hello. There's always a deeper creative angle to explore. What brings you here?",
                    "Hey. Life's too complex for simple answers, but that's where art comes in. What's on your mind?"
                ],
                "creativity": [
                    "Creativity requires embracing the contradictions. What are you trying to create?",
                    "The best art comes from the struggle. What's challenging you creatively?",
                    "There's beauty in the complexity. Tell me about your creative vision."
                ],
                "struggle": [
                    "Pain and beauty often go hand in hand. What are you working through?",
                    "The struggle is where we find our authentic voice. What's your experience?",
                    "Sometimes we have to go through the darkness to find the light. Where are you in that journey?"
                ]
            }
        }        
        # Keywords for matching user messages to response categories
        self.keywords = {
            "greetings": ["hello", "hi", "hey", "introduce", "who are you", "nice to meet"],
            "conflict": ["conflict", "argument", "disagreement", "fight", "dispute", "tension"],
            "stress": ["stressed", "pressure", "overwhelmed", "anxious", "burnout", "tired"],
            "communication": ["communicate", "talk", "speaking", "conversation", "message"],
            "leadership": ["lead", "manage", "team", "boss", "supervisor", "direct"],
            "motivation": ["motivate", "inspire", "encourage", "drive", "passion"],
            "teamwork": ["team", "group", "collaborate", "together", "cooperation"],
            "creativity": ["creative", "art", "music", "design", "artistic", "inspiration"],
            "struggle": ["difficult", "hard", "challenge", "problem", "issue", "trouble"]
        }
    
    async def get_response(self, persona: Dict[str, Any], message: str, session_id: Optional[str] = None, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get a hardcoded response based on persona and message content"""
        
        try:
            # Determine persona type
            persona_name = persona.get("name", "").lower()
            persona_id = "jane"  # default
            
            if "emma" in persona_name or "coach" in persona_name:
                persona_id = "coach_emma"
            elif "billy" in persona_name or "corgan" in persona_name:
                persona_id = "billy_corgan"
            
            # Categorize the message
            category = self._categorize_message(message)
            
            # Get appropriate response
            response = self._get_response_for_category(persona_id, category)
            
            return {
                "success": True,
                "response": response,
                "provider": "Hardcoded Fallback",
                "cost": "FREE",
                "category_detected": category
            }
            
        except Exception as e:
            # Even the fallback has a fallback!
            return {
                "success": True,
                "response": "I'm here to help you. Could you tell me more about what you're looking for?",
                "provider": "Hardcoded Fallback (Emergency)",
                "cost": "FREE",
                "error_handled": str(e)
            }    
    def _categorize_message(self, message: str) -> str:
        """Categorize user message based on keywords"""
        message_lower = message.lower()
        
        # Count keyword matches for each category
        category_scores = {}
        for category, keywords in self.keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score, or 'greetings' as default
        if category_scores:
            return max(category_scores, key=category_scores.get)
        else:
            return "greetings"
    
    def _get_response_for_category(self, persona_id: str, category: str) -> str:
        """Get a random response from the appropriate category"""
        
        persona_responses = self.responses.get(persona_id, self.responses["jane"])
        
        # Get responses for this category, or fall back to greetings
        if category in persona_responses:
            responses = persona_responses[category]
        else:
            responses = persona_responses["greetings"]
        
        # Return a random response from the category
        return random.choice(responses)