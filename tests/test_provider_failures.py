"""
VALIS Provider Failure Testing
Tests specific provider failure scenarios

"When this baby hits 88 failures per second, you're gonna see some serious stuff!" - Doc Brown
"""

import asyncio
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Add VALIS to path
sys.path.append(str(Path(__file__).parent.parent))

from core.provider_manager import ProviderManager, TemporaryError, PermanentError
from providers.hardcoded_fallback import HardcodedFallbackProvider

class MockFailingProvider:
    """Mock provider that always fails for testing"""
    
    def __init__(self, failure_type='temporary'):
        self.failure_type = failure_type
        self.call_count = 0
    
    async def is_available(self):
        return True
    
    async def get_response(self, persona, message, session_id=None, context=None):
        self.call_count += 1
        
        if self.failure_type == 'temporary':
            raise Exception("Network timeout - temporary error")
        elif self.failure_type == 'permanent':
            raise Exception("Authentication failed - permanent error")
        elif self.failure_type == 'success_after_retries':
            if self.call_count < 3:
                raise Exception("Temporary network error")
            else:
                return {"success": True, "response": "Success after retries!"}
        else:
            return {"success": False, "error": f"Mock failure: {self.failure_type}"}

class TestProviderFailures:
    """Test provider failure scenarios"""
    
    @pytest.mark.asyncio
    async def test_temporary_error_retry(self):
        """Test that temporary errors are retried"""
        provider_manager = ProviderManager([])
        provider_manager.providers = [MockFailingProvider('success_after_retries')]
        
        persona = {'id': 'test', 'name': 'Test'}
        result = await provider_manager.get_response(persona, "test message")
        
        assert result.get('success') == True
        assert "Success after retries" in result.get('response', '')
        assert provider_manager.providers[0].call_count >= 3
    
    @pytest.mark.asyncio
    async def test_permanent_error_no_retry(self):
        """Test that permanent errors are not retried excessively"""
        provider_manager = ProviderManager([])
        provider_manager.providers = [
            MockFailingProvider('permanent'),
            HardcodedFallbackProvider()
        ]
        
        persona = {'id': 'jane', 'name': 'Jane Thompson'}
        result = await provider_manager.get_response(persona, "test message")
        
        # Should fallback to hardcoded provider
        assert result.get('success') == True
        assert result.get('provider_used') == 'HardcodedFallbackProvider'
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_pattern(self):
        """Test that circuit breaker opens after multiple failures"""
        provider_manager = ProviderManager([])
        failing_provider = MockFailingProvider('temporary')
        provider_manager.providers = [failing_provider, HardcodedFallbackProvider()]
        
        persona = {'id': 'jane', 'name': 'Jane Thompson'}
        
        # Make multiple requests to trigger circuit breaker
        for i in range(5):
            result = await provider_manager.get_response(persona, f"test message {i}")
            # Should eventually use fallback when circuit breaker opens
        
        # Check that circuit breaker is open
        provider_name = failing_provider.__class__.__name__
        assert provider_manager._is_circuit_breaker_open(provider_name)
    
    @pytest.mark.asyncio
    async def test_all_providers_fail(self):
        """Test behavior when all providers fail"""
        provider_manager = ProviderManager([])
        provider_manager.providers = [
            MockFailingProvider('permanent'),
            MockFailingProvider('temporary')
        ]
        
        persona = {'id': 'test', 'name': 'Test'}
        result = await provider_manager.get_response(persona, "test message")
        
        assert result.get('success') == False
        assert "All providers failed" in result.get('error', '')
        assert 'failed_providers' in result
    
    @pytest.mark.asyncio
    async def test_provider_cascade_order(self):
        """Test that providers are tried in the correct order"""
        class OrderTrackingProvider(MockFailingProvider):
            order_log = []
            
            def __init__(self, name, should_succeed=False):
                super().__init__('permanent')
                self.name = name
                self.should_succeed = should_succeed
            
            async def get_response(self, persona, message, session_id=None, context=None):
                OrderTrackingProvider.order_log.append(self.name)
                if self.should_succeed:
                    return {"success": True, "response": f"Response from {self.name}"}
                else:
                    return {"success": False, "error": f"Failed from {self.name}"}
        
        # Clear order log
        OrderTrackingProvider.order_log = []
        
        provider_manager = ProviderManager([])
        provider_manager.providers = [
            OrderTrackingProvider("First", False),
            OrderTrackingProvider("Second", False), 
            OrderTrackingProvider("Third", True)
        ]
        
        persona = {'id': 'test', 'name': 'Test'}
        result = await provider_manager.get_response(persona, "test message")
        
        assert result.get('success') == True
        assert "Response from Third" in result.get('response', '')
        assert OrderTrackingProvider.order_log == ["First", "Second", "Third"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
