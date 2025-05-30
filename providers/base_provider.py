"""
SPRINT 2.7: Provider Registry Evolution - Base Provider & Registry System
===========================================================================

This module establishes the foundation for VALIS's extensible provider ecosystem.
Providers can now be registered dynamically without modifying core code.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
import logging

# Global provider registry - the heart of our extensible architecture
_PROVIDER_REGISTRY: Dict[str, Type['BaseProvider']] = {}

def register_provider(provider_name: str):
    """
    Decorator to register providers in the global registry.
    
    Usage:
        @register_provider("my_custom_provider")
        class MyCustomProvider(BaseProvider):
            # Implementation...
    """
    def decorator(provider_class):
        if not issubclass(provider_class, BaseProvider):
            raise TypeError(f"Provider {provider_class.__name__} must inherit from BaseProvider")
        
        _PROVIDER_REGISTRY[provider_name] = provider_class
        logging.getLogger('VALIS').info(f"Registered provider: {provider_name} -> {provider_class.__name__}")
        return provider_class
    return decorator

def get_registered_providers() -> Dict[str, Type['BaseProvider']]:
    """Get all registered providers for discovery and debugging"""
    return _PROVIDER_REGISTRY.copy()

def create_provider(provider_name: str) -> Optional['BaseProvider']:
    """Create a provider instance from the registry."""
    if provider_name not in _PROVIDER_REGISTRY:
        return None
    
    provider_class = _PROVIDER_REGISTRY[provider_name]
    try:
        return provider_class()
    except Exception as e:
        logging.getLogger('VALIS').error(f"Failed to create provider {provider_name}: {e}")
        return None

class BaseProvider(ABC):
    """
    Abstract base class for all VALIS providers.
    
    Establishes the consistent interface that enables temporal stabilization
    across any intelligence source - from enterprise APIs to "the junkie under the bridge"!
    """
    
    def __init__(self):
        self.name = "Base Provider"
        self.cost = "UNKNOWN"
        self.logger = logging.getLogger(f'VALIS.{self.__class__.__name__}')
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if this provider is currently available for use.
        
        Should verify:
        - API keys/credentials if required
        - Network connectivity if needed
        - Service health status
        - Dependencies installed
        
        Returns:
            bool: True if provider can handle requests, False otherwise
        """
        raise NotImplementedError("Providers must implement is_available()")
    
    @abstractmethod
    async def get_response(
        self, 
        persona: Dict[str, Any], 
        message: str, 
        session_id: Optional[str] = None, 
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using this provider's intelligence source.
        
        Args:
            persona: Persona data (name, description, traits, etc.)
            message: User's message to process
            session_id: Optional session identifier for context
            context: Optional additional context for the request
        
        Returns:
            Dict containing:
            - success: bool (True if successful)
            - response: str (the generated response) 
            - provider: str (provider identifier)
            - error: str (error message if success=False)
            - metadata: dict (optional additional info)
        """
        raise NotImplementedError("Providers must implement get_response()")
    
    def __str__(self):
        return f"{self.__class__.__name__}(name='{self.name}', cost='{self.cost}')"
    
    def __repr__(self):
        return f"<{self.__class__.__name__} at {hex(id(self))}>"

class BaseProvider(ABC):
    """
    Abstract base class for all VALIS providers.
    
    Establishes the consistent interface that enables temporal stabilization
    across any intelligence source - from enterprise APIs to "the junkie under the bridge"!
    """
    
    def __init__(self):
        self.name = "Base Provider"
        self.cost = "UNKNOWN"
        self.logger = logging.getLogger(f'VALIS.{self.__class__.__name__}')
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if this provider is currently available for use.
        Should verify API keys, connectivity, service health, dependencies.
        """
        raise NotImplementedError("Providers must implement is_available()")
    
    @abstractmethod
    async def get_response(
        self, 
        persona: Dict[str, Any], 
        message: str, 
        session_id: Optional[str] = None, 
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using this provider's intelligence source.
        
        Returns dict with: success, response, provider, error, metadata
        """
        raise NotImplementedError("Providers must implement get_response()")
    
    def __str__(self):
        return f"{self.__class__.__name__}(name='{self.name}', cost='{self.cost}')"
    
    def __repr__(self):
        return f"<{self.__class__.__name__} at {hex(id(self))}>"
