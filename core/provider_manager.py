"""
VALIS Provider Manager
Handles the cascade of AI providers with graceful fallbacks

Provider Priority:
1. Desktop Commander MCP (FREE - uses Claude via MCP)
2. Anthropic API (PAID - direct API calls)
3. OpenAI API (PAID - direct API calls) 
4. Hardcoded Fallback (FREE - intelligent hardcoded responses)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

class ProviderManager:
    """Manages the cascade of AI providers"""
    
    def __init__(self, provider_names: List[str]):
        self.providers = []
        self.logger = logging.getLogger('VALIS.ProviderManager')
        
        # Initialize providers in order
        for provider_name in provider_names:
            try:
                provider = self._create_provider(provider_name)
                if provider:
                    self.providers.append(provider)
                    self.logger.info(f"Initialized provider: {provider_name}")
            except Exception as e:
                self.logger.warning(f"Failed to initialize provider {provider_name}: {e}")
    
    def _create_provider(self, provider_name: str):
        """Factory method to create providers"""
        try:
            if provider_name == "desktop_commander_mcp":
                from providers.desktop_commander_provider import DesktopCommanderProvider
                return DesktopCommanderProvider()
            elif provider_name == "anthropic_api":
                from providers.anthropic_provider import AnthropicProvider
                return AnthropicProvider()
            elif provider_name == "openai_api":
                from providers.openai_provider import OpenAIProvider
                return OpenAIProvider()
            elif provider_name == "hardcoded_fallback":
                from providers.hardcoded_fallback import HardcodedFallbackProvider
                return HardcodedFallbackProvider()
            else:
                self.logger.warning(f"Unknown provider: {provider_name}")
                return None
        except ImportError as e:
            self.logger.warning(f"Failed to import provider {provider_name}: {e}")
            return None    
    async def get_response(
        self,
        persona: Dict[str, Any],
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Get a response using the provider cascade - tries each provider in order until one succeeds"""
        
        for provider in self.providers:
            try:
                self.logger.debug(f"Trying provider: {provider.__class__.__name__}")
                
                # Check if provider is available
                if not await provider.is_available():
                    self.logger.debug(f"Provider {provider.__class__.__name__} not available")
                    continue
                
                # Try to get response
                result = await provider.get_response(
                    persona=persona,
                    message=message,
                    session_id=session_id,
                    context=context
                )
                
                if result.get("success"):
                    result["provider_used"] = provider.__class__.__name__
                    self.logger.info(f"Success with provider: {provider.__class__.__name__}")
                    return result
                else:
                    self.logger.debug(f"Provider {provider.__class__.__name__} failed: {result.get('error')}")
                    
            except Exception as e:
                self.logger.warning(f"Provider {provider.__class__.__name__} error: {e}")
                continue
        
        # All providers failed
        return {
            "success": False,
            "error": "All providers failed to generate a response",
            "provider_used": "none"
        }