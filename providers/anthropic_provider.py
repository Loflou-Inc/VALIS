"""
Anthropic Provider for VALIS
Real Anthropic Claude API integration for premium persona responses
"""

import os
import json
import asyncio
import aiohttp
import logging
from typing import Dict, Optional, Any
from providers.base_provider import BaseProvider, register_provider

@register_provider("anthropic_api")
class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider for premium persona responses"""
    
    def __init__(self):
        super().__init__()
        self.name = "Anthropic API"
        self.cost = "PAID"
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude model
        self.max_tokens = 1024
        
    async def is_available(self) -> bool:
        """Check if Anthropic API is available with REAL connectivity test"""
        # Check for required dependencies
        try:
            import aiohttp
        except ImportError:
            self.logger.warning("AnthropicProvider requires aiohttp: pip install aiohttp")
            return False
        
        # Check for API key
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key or len(api_key.strip()) == 0:
            return False
        
        # REAL CONNECTIVITY TEST - Make lightweight API call
        try:
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            # Test with minimal request - just try to validate API key
            test_payload = {
                "model": self.model,
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "test"}]
            }
            
            timeout = aiohttp.ClientTimeout(total=5)  # 5 second timeout for availability check
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.api_url, headers=headers, json=test_payload) as response:
                    if response.status == 200:
                        self.logger.info("Anthropic API connectivity verified")
                        return True
                    elif response.status == 401:
                        self.logger.warning("Anthropic API key is invalid")
                        return False
                    else:
                        self.logger.warning(f"Anthropic API returned status {response.status}")
                        return False
                        
        except asyncio.TimeoutError:
            self.logger.warning("Anthropic API connectivity test timed out")
            return False
        except Exception as e:
            self.logger.warning(f"Anthropic API connectivity test failed: {e}")
            return False
    
    def _create_system_prompt(self, persona: Dict[str, Any], context: Optional[Dict] = None) -> str:
        """Create system prompt from persona data and neural context"""
        
        # Base persona information
        persona_name = persona.get('name', 'Assistant')
        persona_role = persona.get('role', 'AI Assistant')
        persona_background = persona.get('background', '')
        persona_tone = persona.get('tone', 'helpful and professional')
        persona_approach = persona.get('approach', 'systematic and thorough')
        persona_traits = persona.get('traits', [])
        persona_expertise = persona.get('expertise', [])
        
        # Build comprehensive system prompt
        system_prompt = f"""You are {persona_name}, {persona_role}.

PERSONALITY & BACKGROUND:
{persona_background}

COMMUNICATION STYLE:
- Tone: {persona_tone}
- Approach: {persona_approach}
"""
        
        if persona_traits:
            traits_text = ", ".join(persona_traits) if isinstance(persona_traits, list) else str(persona_traits)
            system_prompt += f"- Key traits: {traits_text}\n"
        
        if persona_expertise:
            expertise_text = ", ".join(persona_expertise) if isinstance(persona_expertise, list) else str(persona_expertise)
            system_prompt += f"- Areas of expertise: {expertise_text}\n"
        
        # Add neural context if available
        if context and 'neural_context' in context:
            neural_context = context['neural_context']
            
            if neural_context.get('conversation_summary'):
                system_prompt += f"\nCONVERSATION CONTEXT:\n{neural_context['conversation_summary']}\n"
            
            if neural_context.get('persona_continuity'):
                system_prompt += f"\nCONTINUITY: {neural_context['persona_continuity']}\n"
        
        # Add session context if available
        if context and 'session_info' in context:
            session_info = context['session_info']
            if session_info.get('session_continuity'):
                system_prompt += f"\nSESSION: {session_info['session_continuity']}\n"
        
        system_prompt += f"\nPlease respond as {persona_name}, maintaining your character, expertise, and communication style consistently."
        
        return system_prompt
    
    async def get_response(self, persona: Dict[str, Any], message: str, session_id: Optional[str] = None, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get response from Anthropic Claude API with persona context and neural enhancement"""
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return {
                "success": False,
                "error": "Anthropic API key not found in environment variables",
                "provider": "Anthropic API"
            }
        
        try:
            # Create persona-aware system prompt
            system_prompt = self._create_system_prompt(persona, context)
            
            # Prepare API request
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            }
            
            # Make API call with timeout and retry logic
            timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.api_url, headers=headers, json=payload) as response:
                    
                    if response.status == 200:
                        response_data = await response.json()
                        
                        # Extract Claude's response
                        if 'content' in response_data and len(response_data['content']) > 0:
                            claude_response = response_data['content'][0].get('text', '')
                            
                            self.logger.info(f"Anthropic API response received: {len(claude_response)} characters")
                            
                            return {
                                "success": True,
                                "response": claude_response,
                                "provider": "Anthropic API",
                                "model": self.model,
                                "cost": "PAID",
                                "tokens_used": response_data.get('usage', {}).get('output_tokens', 0),
                                "neural_context_used": bool(context and 'neural_context' in context)
                            }
                        else:
                            return {
                                "success": False,
                                "error": "No content in Anthropic API response",
                                "provider": "Anthropic API"
                            }
                    
                    elif response.status == 401:
                        return {
                            "success": False,
                            "error": "Invalid Anthropic API key",
                            "provider": "Anthropic API"
                        }
                    
                    elif response.status == 429:
                        return {
                            "success": False,
                            "error": "Anthropic API rate limit exceeded",
                            "provider": "Anthropic API"
                        }
                    
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Anthropic API error {response.status}: {error_text}",
                            "provider": "Anthropic API"
                        }
        
        except asyncio.TimeoutError:
            self.logger.warning("Anthropic API request timed out")
            return {
                "success": False,
                "error": "Anthropic API request timed out",
                "provider": "Anthropic API"
            }
        
        except Exception as e:
            self.logger.error(f"Anthropic API request failed: {e}")
            return {
                "success": False,
                "error": f"Anthropic API request failed: {str(e)}",
                "provider": "Anthropic API"
            }