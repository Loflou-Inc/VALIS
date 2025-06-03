#!/usr/bin/env python3
"""
VALIS Prompt Composer - Sprint 7
Transforms structured memory payload into natural language prompts for AI providers

This is the critical bridge between our 5-layer memory system and provider APIs.
Takes structured JSON memory and creates immersive narrative prompts.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class PromptComposer:
    """
    Transforms VALIS memory payload into natural language prompts
    
    Converts structured memory data into immersive narrative prompts that make
    AI providers feel like they're truly embodying the persona with full context.
    """
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent  # VALIS root
        
        self.base_path = Path(base_path)
        self.templates_path = self.base_path / "templates"
        
        # Ensure templates directory exists
        self.templates_path.mkdir(exist_ok=True)
        
        # Template cache
        self._template_cache = {}
    
    def compose_prompt(self, memory_payload: Dict[str, Any], 
                      template_name: str = "claude_prompt_template.txt",
                      provider_type: str = "claude") -> str:
        """
        Main method: Transform memory payload into natural language prompt
        
        Args:
            memory_payload: Full memory dict from MemoryRouter
            template_name: Template file to use
            provider_type: Provider-specific optimizations
            
        Returns:
            Natural language prompt string ready for provider
        """
        try:
            # Load template
            template_content = self._load_template(template_name)
            
            # Extract and format memory components
            formatted_components = self._format_memory_components(memory_payload)
            
            # Apply provider-specific formatting
            if provider_type == "claude":
                formatted_components = self._apply_claude_formatting(formatted_components)
            elif provider_type == "openai":
                formatted_components = self._apply_openai_formatting(formatted_components)
            
            # Fill template with formatted components
            prompt = self._fill_template(template_content, formatted_components)
            
            # Final cleanup and validation
            prompt = self._finalize_prompt(prompt, memory_payload)
            
            logger.debug(f"Prompt composed for {memory_payload.get('persona_id', 'unknown')} using {template_name}")
            return prompt
            
        except Exception as e:
            logger.error(f"Error composing prompt: {e}")
            # Return fallback prompt
            return self._create_fallback_prompt(memory_payload)
    
    def _load_template(self, template_name: str) -> str:
        """Load and cache template file"""
        if template_name not in self._template_cache:
            template_path = self.templates_path / template_name
            
            if not template_path.exists():
                logger.warning(f"Template {template_name} not found, creating default")
                self._create_default_template(template_path)
            
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    self._template_cache[template_name] = f.read()
            except Exception as e:
                logger.error(f"Error loading template {template_name}: {e}")
                self._template_cache[template_name] = self._get_basic_template()
        
        return self._template_cache[template_name]
    
    def _format_memory_components(self, memory_payload: Dict[str, Any]) -> Dict[str, str]:
        """Extract and format each memory layer into natural language"""
        components = {}
        
        # Basic persona info
        persona_id = memory_payload.get('persona_id', 'Unknown')
        components['persona_id'] = persona_id
        
        # Layer 1: Core Biography
        core_bio = memory_payload.get('core_biography', {})
        components['persona_introduction'] = self._format_core_biography(core_bio)
        
        # Layer 2: Canonized Identity  
        canon_memory = memory_payload.get('canonized_identity', [])
        components['canon_experiences'] = self._format_canonized_identity(canon_memory)
        
        # Layer 3: Client Profile
        client_profile = memory_payload.get('client_profile', {})
        components['client_context'] = self._format_client_profile(client_profile)
        
        # Layer 4: Working Memory
        working_memory = memory_payload.get('working_memory', [])
        components['recent_observations'] = self._format_working_memory(working_memory)
        
        # Layer 5: Session History
        session_history = memory_payload.get('session_history', [])
        components['conversation_context'] = self._format_session_history(session_history)
        
        # Current message
        current_message = memory_payload.get('message', '')
        components['current_message'] = current_message
        
        # Timestamp for context
        components['current_time'] = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        return components
    
    def _format_core_biography(self, core_bio: Dict[str, Any]) -> str:
        """Format Layer 1: Core persona into narrative introduction"""
        if not core_bio:
            return "You are an AI assistant ready to help."
        
        name = core_bio.get('name', 'Assistant')
        description = core_bio.get('description', '')
        background = core_bio.get('background', '')
        approach = core_bio.get('approach', '')
        
        bio_parts = [f"You are {name}."]
        
        if description:
            bio_parts.append(f"{description}")
        
        if background:
            bio_parts.append(f"Your background: {background}")
            
        if approach:
            bio_parts.append(f"Your approach: {approach}")
        
        # Add specialties if available
        specialties = core_bio.get('specialties', [])
        if specialties:
            specialties_text = ", ".join(specialties)
            bio_parts.append(f"You specialize in: {specialties_text}.")
        
        return " ".join(bio_parts)
    
    def _format_canonized_identity(self, canon_entries: List[Dict[str, Any]]) -> str:
        """Format Layer 2: Canonized experiences into key memories"""
        if not canon_entries:
            return "You have a clean slate of professional experiences to draw from."
        
        canon_parts = ["Your key professional experiences and learnings:"]
        
        # Show most recent canon entries (limit to avoid prompt bloat)
        recent_canon = canon_entries[-5:] if len(canon_entries) > 5 else canon_entries
        
        for i, entry in enumerate(recent_canon, 1):
            content = entry.get('content', '').replace('#canon', '').strip()
            # Truncate very long entries
            if len(content) > 200:
                content = content[:200] + "..."
            canon_parts.append(f"{i}. {content}")
        
        return "\n".join(canon_parts)
    
    def _format_client_profile(self, client_profile: Dict[str, Any]) -> str:
        """Format Layer 3: Client-specific context"""
        if not client_profile or not client_profile.get('facts'):
            return "This is a new client interaction with no prior context."
        
        facts = client_profile.get('facts', {})
        context_parts = ["About your current client:"]
        
        for key, value in facts.items():
            # Format key to be more readable
            readable_key = key.replace('_', ' ').title()
            context_parts.append(f"- {readable_key}: {value}")
        
        return "\n".join(context_parts)
    
    def _format_working_memory(self, working_memory: List[Dict[str, Any]]) -> str:
        """Format Layer 4: Recent observations and insights"""
        if not working_memory:
            return "No recent observations to note."
        
        memory_parts = ["Your recent observations and insights:"]
        
        # Show most recent working memories (limit to 3-5)
        recent_memories = working_memory[-5:] if len(working_memory) > 5 else working_memory
        
        for memory in recent_memories:
            content = memory.get('content', '')
            memory_type = memory.get('type', 'observation')
            
            # Truncate long memories
            if len(content) > 150:
                content = content[:150] + "..."
            
            memory_parts.append(f"- ({memory_type.title()}) {content}")
        
        return "\n".join(memory_parts)
    
    def _format_session_history(self, session_history: List[Dict[str, str]]) -> str:
        """Format Layer 5: Recent conversation context"""
        if not session_history:
            return "This is the start of your conversation."
        
        history_parts = ["Recent conversation context:"]
        
        # Show last few exchanges (limit to avoid prompt bloat)
        recent_history = session_history[-6:] if len(session_history) > 6 else session_history
        
        for msg in recent_history:
            role = msg.get('role', '').upper()
            content = msg.get('content', '')
            
            # Truncate long messages
            if len(content) > 100:
                content = content[:100] + "..."
            
            history_parts.append(f"{role}: {content}")
        
        return "\n".join(history_parts)
    
    def _apply_claude_formatting(self, components: Dict[str, str]) -> Dict[str, str]:
        """Apply Claude-specific formatting optimizations"""
        # Claude likes narrative, conversational prompts
        # Add some Claude-specific touches
        
        if components.get('persona_introduction'):
            # Make it more immersive for Claude
            intro = components['persona_introduction']
            if not intro.startswith('You are '):
                components['persona_introduction'] = f"You are {intro}"
        
        # Claude responds well to explicit instruction about staying in character
        components['character_instruction'] = (
            "Respond as this persona with full awareness of your background, experiences, "
            "and current context. Stay true to your professional style and approach."
        )
        
        return components
    
    def _apply_openai_formatting(self, components: Dict[str, str]) -> Dict[str, str]:
        """Apply OpenAI-specific formatting optimizations"""
        # OpenAI models sometimes prefer more structured instructions
        
        if components.get('persona_introduction'):
            intro = components['persona_introduction']
            components['persona_introduction'] = f"System: {intro}"
        
        components['character_instruction'] = (
            "Maintain consistent character throughout the conversation. "
            "Use your background knowledge and context appropriately."
        )
        
        return components
    
    def _fill_template(self, template_content: str, components: Dict[str, str]) -> str:
        """Fill template with formatted components using Python Template"""
        try:
            template = Template(template_content)
            
            # Ensure all template variables have values (avoid KeyError)
            safe_components = {key: value or f"[{key} not available]" 
                             for key, value in components.items()}
            
            return template.safe_substitute(safe_components)
            
        except Exception as e:
            logger.error(f"Template filling error: {e}")
            # Fallback to basic string formatting if Template fails
            return self._basic_template_fill(template_content, components)
    
    def _basic_template_fill(self, template_content: str, components: Dict[str, str]) -> str:
        """Fallback template filling method"""
        result = template_content
        for key, value in components.items():
            placeholder = f"${{{key}}}"
            result = result.replace(placeholder, str(value))
        return result
    
    def _finalize_prompt(self, prompt: str, memory_payload: Dict[str, Any]) -> str:
        """Final cleanup and validation of composed prompt"""
        
        # Remove excessive whitespace
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        prompt = '\n'.join(lines)
        
        # Ensure prompt isn't too short or too long
        if len(prompt) < 100:
            logger.warning("Generated prompt is very short, may lack context")
        elif len(prompt) > 4000:
            logger.warning("Generated prompt is very long, may hit token limits")
            # Could implement truncation logic here if needed
        
        # Add proper assistant instruction
        if not prompt.endswith('\n'):
            prompt += '\n'
        
        prompt += "\nAssistant:"
        
        return prompt
    
    def _create_fallback_prompt(self, memory_payload: Dict[str, Any]) -> str:
        """Create minimal fallback prompt if template system fails"""
        persona_id = memory_payload.get('persona_id', 'Assistant')
        current_message = memory_payload.get('message', '')
        
        core_bio = memory_payload.get('core_biography', {})
        name = core_bio.get('name', persona_id)
        description = core_bio.get('description', 'AI assistant')
        
        fallback = f"""You are {name}, {description}.
        
User: {current_message}

Respond helpfully as {name}:"""
        
        logger.info("Using fallback prompt due to template system failure")
        return fallback
    
    def _create_default_template(self, template_path: Path):
        """Create default Claude template if none exists"""
        default_template = '''$persona_introduction

$canon_experiences

$client_context

$recent_observations

$conversation_context

Current time: $current_time

$character_instruction

$current_message'''
        
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(default_template)
            logger.info(f"Created default template at {template_path}")
        except Exception as e:
            logger.error(f"Could not create default template: {e}")
    
    def _get_basic_template(self) -> str:
        """Get basic template as last resort"""
        return '''$persona_introduction

$current_message'''
    
    # Utility Methods
    def get_prompt_stats(self, prompt: str) -> Dict[str, Any]:
        """Get statistics about the generated prompt"""
        lines = prompt.split('\n')
        words = prompt.split()
        
        return {
            "character_count": len(prompt),
            "word_count": len(words),
            "line_count": len(lines),
            "estimated_tokens": len(words) * 1.3,  # Rough estimation
            "has_persona_context": "You are" in prompt,
            "has_memory_context": any(keyword in prompt.lower() for keyword in 
                                    ['experience', 'observation', 'client', 'recent'])
        }
    
    def debug_prompt_composition(self, memory_payload: Dict[str, Any], 
                               template_name: str = "claude_prompt_template.txt") -> Dict[str, Any]:
        """Debug version that returns detailed composition info"""
        
        # Get components
        components = self._format_memory_components(memory_payload)
        
        # Load template
        template_content = self._load_template(template_name)
        
        # Compose prompt
        final_prompt = self.compose_prompt(memory_payload, template_name)
        
        # Get stats
        stats = self.get_prompt_stats(final_prompt)
        
        return {
            "memory_payload": memory_payload,
            "formatted_components": components,
            "template_content": template_content,
            "final_prompt": final_prompt,
            "prompt_stats": stats,
            "component_lengths": {key: len(str(value)) for key, value in components.items()}
        }


# Factory function for easy import
def create_prompt_composer(base_path: str = None) -> PromptComposer:
    """Factory function to create PromptComposer instance"""
    return PromptComposer(base_path)


if __name__ == "__main__":
    # Basic test
    composer = create_prompt_composer()
    
    # Test with sample memory payload
    test_payload = {
        "persona_id": "jane",
        "core_biography": {
            "name": "Jane Thompson", 
            "description": "HR Business Partner"
        },
        "canonized_identity": [],
        "client_profile": {},
        "working_memory": [],
        "session_history": [],
        "message": "Hello, I need help with team conflicts"
    }
    
    prompt = composer.compose_prompt(test_payload)
    print("Test prompt generated:")
    print(prompt)
