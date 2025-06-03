#!/usr/bin/env python3
"""
VALIS Persona Router - Sprint 7.5
Handles persona targeting, message parsing, and routing logic

Fixes the identity misrouting issues by implementing explicit persona targeting
and removing hardcoded fallbacks to "jane".
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class PersonaRouter:
    """
    Handles persona routing and message targeting
    
    Supports multiple targeting patterns:
    - *** PersonaName (Discord/Slack style)
    - @PersonaName (mention style)  
    - persona: "name" (explicit JSON style)
    - CLI --persona=name flag
    """
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent  # VALIS root
        
        self.base_path = Path(base_path)
        self.personas_path = self.base_path / "personas"
        
        # Targeting patterns
        self.targeting_patterns = [
            r'^\*\*\*\s*(\w+)',              # *** PersonaName
            r'^@(\w+)',                       # @PersonaName  
            r'persona:\s*["\'](\w+)["\']',    # persona: "name"
            r'--persona[=\s]+(\w+)',          # --persona=name or --persona name
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.targeting_patterns]
        
        # Valid persona cache
        self._persona_cache = {}
        self._refresh_persona_cache()
    
    def _refresh_persona_cache(self):
        """Refresh the cache of available personas"""
        self._persona_cache = {}
        
        if self.personas_path.exists():
            for persona_file in self.personas_path.glob("*.json"):
                persona_id = persona_file.stem
                self._persona_cache[persona_id.lower()] = persona_id
                
                # Also cache common aliases
                if persona_id == "doc_brown":
                    self._persona_cache["doc"] = persona_id
                    self._persona_cache["brown"] = persona_id
                elif persona_id == "advisor_alex":
                    self._persona_cache["alex"] = persona_id
                elif persona_id == "coach_emma":
                    self._persona_cache["emma"] = persona_id
                elif persona_id == "guide_sam":
                    self._persona_cache["sam"] = persona_id
                elif persona_id == "billy_corgan":
                    self._persona_cache["billy"] = persona_id
                    self._persona_cache["corgan"] = persona_id
        
        logger.debug(f"Persona cache refreshed: {list(self._persona_cache.keys())}")
    
    def parse_persona_target(self, message: str, context: Optional[Dict] = None) -> Tuple[Optional[str], str]:
        """
        Parse message for persona targeting patterns
        
        Returns:
            (persona_id, cleaned_message) - persona_id is None if no targeting found
        """
        
        # Check for explicit context override first
        if context and 'persona_override' in context:
            return context['persona_override'], message
        
        # Check each targeting pattern
        for pattern in self.compiled_patterns:
            match = pattern.search(message)
            if match:
                target_name = match.group(1).lower()
                
                # Resolve persona name
                persona_id = self._resolve_persona_name(target_name)
                if persona_id:
                    # Clean the targeting syntax from message
                    cleaned_message = pattern.sub('', message).strip()
                    logger.info(f"Persona targeting detected: {target_name} -> {persona_id}")
                    return persona_id, cleaned_message
                else:
                    logger.warning(f"Invalid persona target: {target_name}")
        
        return None, message
    
    def _resolve_persona_name(self, target_name: str) -> Optional[str]:
        """
        Resolve a target name to a valid persona ID
        
        Handles aliases and partial matching
        """
        target_lower = target_name.lower()
        
        # Direct match
        if target_lower in self._persona_cache:
            return self._persona_cache[target_lower]
        
        # Partial matching for common cases
        for cached_name, persona_id in self._persona_cache.items():
            if target_lower in cached_name or cached_name in target_lower:
                return persona_id
        
        return None
    
    def route_message(self, message: str, default_persona: Optional[str] = None, 
                     context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Route a message to the appropriate persona
        
        Returns routing information including persona_id and cleaned message
        """
        
        # Parse for explicit targeting
        target_persona, cleaned_message = self.parse_persona_target(message, context)
        
        result = {
            "persona_id": target_persona or default_persona,
            "message": cleaned_message,
            "targeting_detected": target_persona is not None,
            "original_message": message,
            "available_personas": list(self._persona_cache.values())
        }
        
        # Validation
        if result["persona_id"]:
            if not self.is_valid_persona(result["persona_id"]):
                result["error"] = f"Invalid persona: {result['persona_id']}"
                result["persona_id"] = None
        
        # Warning if no persona resolved
        if not result["persona_id"]:
            result["warning"] = "No valid persona targeted - explicit targeting required"
            logger.warning(f"No persona resolved for message: {message[:50]}...")
        
        return result
    
    def is_valid_persona(self, persona_id: str) -> bool:
        """Check if a persona ID is valid"""
        if not persona_id:
            return False
        
        persona_file = self.personas_path / f"{persona_id}.json"
        return persona_file.exists()
    
    def get_available_personas(self) -> List[str]:
        """Get list of available persona IDs"""
        self._refresh_persona_cache()
        return list(set(self._persona_cache.values()))
    
    def suggest_persona_from_context(self, message: str) -> Optional[str]:
        """
        Suggest a persona based on message content analysis
        
        This is for cases where no explicit targeting is found
        """
        message_lower = message.lower()
        
        # Content-based suggestions
        if any(word in message_lower for word in ['hr', 'conflict', 'team', 'workplace', 'employee']):
            return 'jane'
        elif any(word in message_lower for word in ['coach', 'motivation', 'goals', 'achievement']):
            return 'coach_emma'
        elif any(word in message_lower for word in ['strategy', 'business', 'advice', 'planning']):
            return 'advisor_alex'
        elif any(word in message_lower for word in ['guide', 'wisdom', 'philosophy', 'life']):
            return 'guide_sam'
        elif any(word in message_lower for word in ['creative', 'art', 'music', 'expression']):
            return 'billy_corgan'
        elif any(word in message_lower for word in ['technical', 'system', 'architecture', 'code']):
            return 'doc_brown'
        elif any(word in message_lower for word in ['test', 'validate', 'check', 'quality']):
            return 'biff'
        elif any(word in message_lower for word in ['decision', 'priority', 'strategy', 'business']):
            return 'laika'
        
        return None
    
    def format_targeting_help(self) -> str:
        """Generate help text for persona targeting"""
        available = self.get_available_personas()
        
        help_text = """
VALIS Persona Targeting:

Targeting Patterns:
  *** PersonaName    (Discord style)
  @PersonaName       (Mention style)  
  persona: "name"    (JSON style)
  --persona=name     (CLI flag)

Available Personas:
"""
        
        for persona_id in sorted(available):
            help_text += f"  - {persona_id}\n"
        
        help_text += "\nExample: *** laika What's the priority for today?"
        
        return help_text


# Factory function for easy import
def create_persona_router(base_path: str = None) -> PersonaRouter:
    """Factory function to create PersonaRouter instance"""
    return PersonaRouter(base_path)


if __name__ == "__main__":
    # Test the persona router
    router = create_persona_router()
    
    test_messages = [
        "*** laika What's the priority?",
        "@jane I need help with team conflicts", 
        "persona: \"doc_brown\" Review this system",
        "--persona=biff Test this feature",
        "Just a regular message with no targeting"
    ]
    
    print("Persona Router Test:")
    print("=" * 40)
    
    for message in test_messages:
        result = router.route_message(message)
        print(f"Message: {message}")
        print(f"  -> Persona: {result['persona_id']}")
        print(f"  -> Cleaned: {result['message']}")
        print(f"  -> Targeted: {result['targeting_detected']}")
        print()
