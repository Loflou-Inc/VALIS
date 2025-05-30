"""
OpenAI Provider for VALIS
OpenAI GPT API integration for persona responses
"""

import os
import json
import asyncio
import aiohttp
import logging
from typing import Dict, Optional, Any
from providers.base_provider import BaseProvider, register_provider

@register_provider("openai_api")
class OpenAIProvider(BaseProvider):
    """OpenAI GPT provider for persona responses"""
    
    def __init__(self):
        super().__init__()
        self.name = "OpenAI API"
        self.cost = "PAID"
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4o"  # Latest GPT-4 Omni model
        self.max_tokens = 1024
        self.temperature = 0.7
        
    async def is_available(self) -> bool:
        """Check if OpenAI API is available with REAL connectivity test"""
        # Check for required dependencies
        try:
            import aiohttp
        except ImportError:
            self.logger.warning("OpenAIProvider requires aiohttp: pip install aiohttp")
            return False
        
        # Check for API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or len(api_key.strip()) == 0:
            return False
        
        # REAL CONNECTIVITY TEST - Make lightweight API call
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Test with minimal request to models endpoint
            test_url = "https://api.openai.com/v1/models"
            timeout = aiohttp.ClientTimeout(total=5)  # 5 second timeout for availability check
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(test_url, headers=headers) as response:
                    if response.status == 200:
                        self.logger.info("OpenAI API connectivity verified")
                        return True
                    elif response.status == 401:
                        self.logger.warning("OpenAI API key is invalid")
                        return False
                    else:
                        self.logger.warning(f"OpenAI API returned status {response.status}")
                        return False
                        
        except asyncio.TimeoutError:
            self.logger.warning("OpenAI API connectivity test timed out")
            return False
        except Exception as e:
            self.logger.warning(f"OpenAI API connectivity test failed: {e}")
            return False
    
    def _create_system_message(self, persona: Dict[str, Any], context: Optional[Dict] = None) -> str:
        """Create system message from persona data and neural context"""
        
        # Base persona information
        persona_name = persona.get('name', 'Assistant')
        persona_role = persona.get('role', 'AI Assistant')
        persona_background = persona.get('background', '')
        persona_tone = persona.get('tone', 'helpful and professional')
        persona_approach = persona.get('approach', 'systematic and thorough')
        persona_traits = persona.get('traits', [])
        persona_expertise = persona.get('expertise', [])
        
        # Build comprehensive system message
        system_message = f"""You are {persona_name}, {persona_role}.

PERSONALITY & BACKGROUND:
{persona_background}

COMMUNICATION STYLE:
- Tone: {persona_tone}
- Approach: {persona_approach}
"""
        
        if persona_traits:
            traits_text = ", ".join(persona_traits) if isinstance(persona_traits, list) else str(persona_traits)
            system_message += f"- Key traits: {traits_text}\n"
        
        if persona_expertise:
            expertise_text = ", ".join(persona_expertise) if isinstance(persona_expertise, list) else str(persona_expertise)
            system_message += f"- Areas of expertise: {expertise_text}\n"
        
        # Add neural context if available
        if context and 'neural_context' in context:
            neural_context = context['neural_context']
            
            if neural_context.get('conversation_summary'):
                system_message += f"\nCONVERSATION CONTEXT:\n{neural_context['conversation_summary']}\n"
            
            if neural_context.get('persona_continuity'):
                system_message += f"\nCONTINUITY: {neural_context['persona_continuity']}\n"
        
        # Add session context if available
        if context and 'session_info' in context:
            session_info = context['session_info']
            if session_info.get('session_continuity'):
                system_message += f"\nSESSION: {session_info['session_continuity']}\n"
        
        system_message += f"\nRespond as {persona_name}, maintaining your character, expertise, and communication style consistently."
        
        return system_message
    
    async def get_response(self, persona: Dict[str, Any], message: str, session_id: Optional[str] = None, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get response from OpenAI GPT API with persona context and neural enhancement"""
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {
                "success": False,
                "error": "OpenAI API key not found in environment variables",
                "provider": "OpenAI API"
            }
        
        try:
            # Create persona-aware system message
            system_message = self._create_system_message(persona, context)
            
            # Prepare API request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": [
                    {
                        "role": "system",
                        "content": system_message
                    },
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
                        
                        # Extract GPT's response
                        if 'choices' in response_data and len(response_data['choices']) > 0:
                            gpt_response = response_data['choices'][0]['message']['content']
                            
                            self.logger.info(f"OpenAI API response received: {len(gpt_response)} characters")
                            
                            return {
                                "success": True,
                                "response": gpt_response,
                                "provider": "OpenAI API",
                                "model": self.model,
                                "cost": "PAID",
                                "tokens_used": response_data.get('usage', {}).get('completion_tokens', 0),
                                "neural_context_used": bool(context and 'neural_context' in context)
                            }
                        else:
                            return {
                                "success": False,
                                "error": "No choices in OpenAI API response",
                                "provider": "OpenAI API"
                            }
                    
                    elif response.status == 401:
                        return {
                            "success": False,
                            "error": "Invalid OpenAI API key",
                            "provider": "OpenAI API"
                        }
                    
                    elif response.status == 429:
                        return {
                            "success": False,
                            "error": "OpenAI API rate limit exceeded",
                            "provider": "OpenAI API"
                        }
                    
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"OpenAI API error {response.status}: {error_text}",
                            "provider": "OpenAI API"
                        }
        
        except asyncio.TimeoutError:
            self.logger.warning("OpenAI API request timed out")
            return {
                "success": False,
                "error": "OpenAI API request timed out",
                "provider": "OpenAI API"
            }
        
        except Exception as e:
            self.logger.error(f"OpenAI API request failed: {e}")
            return {
                "success": False,
                "error": f"OpenAI API request failed: {str(e)}",
                "provider": "OpenAI API"
            }