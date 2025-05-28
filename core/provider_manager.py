"""
VALIS Provider Manager
Handles the cascade of AI providers with graceful fallbacks and temporal stabilization

Provider Priority:
1. Desktop Commander MCP (FREE - uses Claude via MCP)
2. Anthropic API (PAID - direct API calls)
3. OpenAI API (PAID - direct API calls) 
4. Hardcoded Fallback (FREE - intelligent hardcoded responses)
"""

import asyncio
import logging
import time
import uuid
from collections import defaultdict
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class TemporalError(Exception):
    """Base class for temporal stabilization errors"""
    pass

class TemporaryError(TemporalError):
    """Errors that might resolve with retry (network issues, timeouts)"""
    pass

class PermanentError(TemporalError):
    """Errors that won't resolve with retry (auth failures, missing configs)"""
    pass

class ProviderManager:
    """Manages the cascade of AI providers with temporal stabilization"""
    
    def __init__(self, provider_names: List[str]):
        self.providers = []
        self.logger = logging.getLogger('VALIS.ProviderManager')
        
        # Temporal stabilization components
        self.request_semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
        self.provider_failures = defaultdict(int)  # Track failure counts
        self.provider_circuit_breakers = defaultdict(datetime)  # Circuit breaker timestamps
        self.circuit_breaker_threshold = 3  # Failures before circuit opens
        self.circuit_breaker_timeout = timedelta(minutes=5)  # How long circuit stays open
        self.retry_delays = [1, 2, 4]  # Exponential backoff for retries
        
        # Request tracking
        self.active_requests = {}
        self.request_stats = defaultdict(list)
        
        # Initialize providers in order
        for provider_name in provider_names:
            try:
                provider = self._create_provider(provider_name)
                if provider:
                    self.providers.append(provider)
                    self.logger.info(f"Initialized provider: {provider_name}")
            except Exception as e:
                self.logger.warning(f"Failed to initialize provider {provider_name}: {e}")
                
        self.logger.info(f"Temporal stabilization active with {len(self.providers)} providers")
    
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
    
    def _is_circuit_breaker_open(self, provider_name: str) -> bool:
        """Check if circuit breaker is open for this provider"""
        if provider_name not in self.provider_circuit_breakers:
            return False
            
        breaker_time = self.provider_circuit_breakers[provider_name]
        if datetime.now() - breaker_time > self.circuit_breaker_timeout:
            # Circuit breaker timeout expired, reset
            del self.provider_circuit_breakers[provider_name]
            self.provider_failures[provider_name] = 0
            self.logger.info(f"Circuit breaker reset for provider: {provider_name}")
            return False
            
        return True
    
    def _record_provider_failure(self, provider_name: str):
        """Record a provider failure and possibly open circuit breaker"""
        self.provider_failures[provider_name] += 1
        
        if self.provider_failures[provider_name] >= self.circuit_breaker_threshold:
            self.provider_circuit_breakers[provider_name] = datetime.now()
            self.logger.warning(f"Circuit breaker opened for provider: {provider_name} (failures: {self.provider_failures[provider_name]})")
    
    def _record_provider_success(self, provider_name: str):
        """Record a provider success and reset failure count"""
        if provider_name in self.provider_failures:
            self.provider_failures[provider_name] = 0
            self.logger.debug(f"Provider failure count reset for: {provider_name}")
    
    def _classify_error(self, error: Exception) -> str:
        """Classify errors as temporary or permanent for retry logic"""
        error_str = str(error).lower()
        
        # Temporary errors that might resolve with retry
        temporary_indicators = [
            'timeout', 'connection', 'network', 'socket', 'dns',
            'rate limit', 'busy', 'unavailable', 'overloaded'
        ]
        
        # Permanent errors that won't resolve with retry
        permanent_indicators = [
            'authentication', 'unauthorized', 'forbidden', 'api key',
            'invalid request', 'not found', 'bad request', 'malformed'
        ]
        
        for indicator in temporary_indicators:
            if indicator in error_str:
                return 'temporary'
                
        for indicator in permanent_indicators:
            if indicator in error_str:
                return 'permanent'
                
        # Default to temporary for unknown errors
        return 'temporary'    
    async def get_response(
        self,
        persona: Dict[str, Any],
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Get a response using the provider cascade with temporal stabilization"""
        
        # Generate unique request ID for tracking
        request_id = str(uuid.uuid4())[:8]
        request_start = time.time()
        
        self.logger.info(f"[{request_id}] Starting request for persona {persona.get('id', 'unknown')}")
        
        # Use semaphore to limit concurrent requests
        async with self.request_semaphore:
            self.active_requests[request_id] = {
                'start_time': request_start,
                'persona_id': persona.get('id'),
                'message_preview': message[:50] + '...' if len(message) > 50 else message
            }
            
            try:
                return await self._execute_cascade(request_id, persona, message, session_id, context)
            finally:
                # Clean up request tracking
                if request_id in self.active_requests:
                    del self.active_requests[request_id]
                
                total_time = time.time() - request_start
                self.logger.info(f"[{request_id}] Request completed in {total_time:.2f}s")    
    async def _execute_cascade(self, request_id: str, persona: Dict[str, Any], message: str, 
                              session_id: Optional[str], context: Optional[Dict]) -> Dict[str, Any]:
        """Execute the provider cascade with temporal stabilization"""
        
        failed_providers = []
        
        for provider in self.providers:
            provider_name = provider.__class__.__name__
            provider_start = time.time()
            
            try:
                self.logger.debug(f"[{request_id}] Attempting provider: {provider_name}")
                
                # Check circuit breaker
                if self._is_circuit_breaker_open(provider_name):
                    self.logger.warning(f"[{request_id}] Provider {provider_name} circuit breaker is open")
                    failed_providers.append({
                        'provider': provider_name,
                        'error': 'Circuit breaker open',
                        'type': 'circuit_breaker'
                    })
                    continue
                
                # Check if provider is available
                if not await provider.is_available():
                    self.logger.debug(f"[{request_id}] Provider {provider_name} not available")
                    failed_providers.append({
                        'provider': provider_name,
                        'error': 'Provider not available',
                        'type': 'availability'
                    })
                    continue
                
                # Try with retry logic for temporary errors
                result = await self._try_provider_with_retries(
                    request_id, provider, persona, message, session_id, context
                )
                
                provider_time = time.time() - provider_start
                
                if result.get("success"):
                    # Success! Record metrics and return
                    self._record_provider_success(provider_name)
                    result["provider_used"] = provider_name
                    result["response_time"] = provider_time
                    result["request_id"] = request_id
                    
                    self.logger.info(f"[{request_id}] SUCCESS with {provider_name} in {provider_time:.2f}s")
                    
                    # Store success stats
                    self.request_stats[provider_name].append({
                        'timestamp': datetime.now(),
                        'response_time': provider_time,
                        'success': True
                    })
                    
                    return result
                else:
                    # Provider failed
                    error_msg = result.get('error', 'Unknown error')
                    self._record_provider_failure(provider_name)
                    
                    failed_providers.append({
                        'provider': provider_name,
                        'error': error_msg,
                        'type': 'provider_error',
                        'response_time': provider_time
                    })
                    
                    self.logger.warning(f"[{request_id}] Provider {provider_name} failed: {error_msg}")
                    
            except Exception as e:
                provider_time = time.time() - provider_start
                error_type = self._classify_error(e)
                
                self._record_provider_failure(provider_name)
                
                failed_providers.append({
                    'provider': provider_name,
                    'error': str(e),
                    'type': f'exception_{error_type}',
                    'response_time': provider_time
                })
                
                self.logger.error(f"[{request_id}] Provider {provider_name} exception: {e}")
                continue
        
        # All providers failed - return comprehensive failure report
        return {
            "success": False,
            "error": "All providers failed to generate a response",
            "provider_used": "none",
            "request_id": request_id,
            "failed_providers": failed_providers,
            "total_providers_attempted": len(failed_providers)
        }
    
    async def _try_provider_with_retries(self, request_id: str, provider, persona: Dict[str, Any], 
                                        message: str, session_id: Optional[str], 
                                        context: Optional[Dict]) -> Dict[str, Any]:
        """Try a provider with retry logic for temporary errors"""
        
        provider_name = provider.__class__.__name__
        
        for attempt in range(len(self.retry_delays) + 1):  # Original attempt + retries
            try:
                if attempt > 0:
                    delay = self.retry_delays[attempt - 1]
                    self.logger.debug(f"[{request_id}] Retrying {provider_name} in {delay}s (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                
                # Make the actual provider call
                result = await provider.get_response(
                    persona=persona,
                    message=message,
                    session_id=session_id,
                    context=context
                )
                
                return result
                
            except Exception as e:
                error_type = self._classify_error(e)
                
                if error_type == 'permanent' or attempt >= len(self.retry_delays):
                    # Don't retry permanent errors or if we've exhausted retries
                    self.logger.debug(f"[{request_id}] Not retrying {provider_name}: {error_type} error or max attempts reached")
                    raise e
                
                self.logger.debug(f"[{request_id}] Temporary error in {provider_name}, will retry: {e}")
        
        # This shouldn't be reached, but just in case
        return {"success": False, "error": "Max retries exceeded"}
    
    def get_cascade_status(self) -> Dict[str, Any]:
        """Get current status of the provider cascade for monitoring"""
        return {
            "providers": [p.__class__.__name__ for p in self.providers],
            "active_requests": len(self.active_requests),
            "circuit_breakers": {
                name: str(timestamp) for name, timestamp in self.provider_circuit_breakers.items()
            },
            "failure_counts": dict(self.provider_failures),
            "recent_stats": {
                provider: len([s for s in stats if datetime.now() - s['timestamp'] < timedelta(minutes=5)])
                for provider, stats in self.request_stats.items()
            }
        }
