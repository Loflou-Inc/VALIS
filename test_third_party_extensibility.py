#!/usr/bin/env python3
"""SPRINT 2.7: Third-Party Provider Extensibility Test"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create third-party provider WITHOUT touching core code
from providers.base_provider import BaseProvider, register_provider

@register_provider("demo_third_party")
class DemoThirdPartyProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self.name = "Demo Third Party AI"
        self.cost = "FREE"
    
    async def is_available(self) -> bool:
        return True
    
    async def get_response(self, persona, message, session_id=None, context=None):
        return {
            "success": True,
            "response": f"Third-party response for {persona.get('name', 'Unknown')}: {message}",
            "provider": self.name,
            "metadata": {"third_party": True}
        }

async def test_extensibility():
    print("SPRINT 2.7: THIRD-PARTY EXTENSIBILITY TEST")
    print("=" * 50)
    
    try:
        from providers.base_provider import get_registered_providers, create_provider
        from core.provider_manager import ProviderManager
        
        # Test registration
        registered = get_registered_providers()
        reg_success = "demo_third_party" in registered
        
        # Test creation
        provider = create_provider("demo_third_party")
        create_success = provider is not None
        
        # Test integration
        manager = ProviderManager(["demo_third_party", "hardcoded_fallback"])
        integration_success = len(manager.providers) == 2
        
        print(f"Registered: {reg_success}")
        print(f"Created: {create_success}")
        print(f"Integrated: {integration_success}")
        
        success = reg_success and create_success and integration_success
        print(f"RESULT: {'SUCCESS' if success else 'FAILURE'}")
        return success
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_extensibility())
    print(f"EXTENSIBILITY: {'PROVEN' if result else 'BROKEN'}")
