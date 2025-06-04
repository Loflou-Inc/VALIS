#!/usr/bin/env python3
"""
ProviderManager - Cascade Router for VALIS 2.0
Routes requests through configurable provider cascade with fallback logic
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger("ProviderManager")

class ProviderManager:
    """
    Provider cascade router with fallback logic
    
    Manages provider selection and failure handling
    """
    
    def __init__(self, config_path: str = "config"):
        self.config_path = config_path
        self.providers = {}
        self.cascade = []
        
        # Load cascade configuration
        self._load_cascade_config()
        
        # Initialize providers
        self._initialize_providers()
        
        logger.info(f"🎛️ ProviderManager initialized with cascade: {self.cascade}")
    
    def ask(self, prompt: str, client_id: str, persona_id: str) -> Dict[str, Any]:
        """
        Route request through provider cascade
        
        Returns:
        {
            "success": bool,
            "response": str,
            "provider_used": str,
            "processing_time": float,
            "cascade_trace": list
        }
        """
        
        start_time = time.time()
        cascade_trace = []
        
        logger.info(f"=== PROVIDER CASCADE REQUEST ===")
        logger.info(f"Prompt: {prompt[:100]}...")
        logger.info(f"Client: {client_id}, Persona: {persona_id}")
        logger.info(f"Cascade: {self.cascade}")
        
        for provider_name in self.cascade:
            if provider_name not in self.providers:
                logger.warning(f"Provider {provider_name} not available")
                cascade_trace.append(f"{provider_name}: not_available")
                continue
            
            provider = self.providers[provider_name]
            
            try:
                logger.info(f"Trying provider: {provider_name}")
                
                result = provider.ask(prompt, client_id, persona_id)
                
                if result.get("success"):
                    processing_time = time.time() - start_time
                    cascade_trace.append(f"{provider_name}: success")
                    
                    logger.info(f"✓ Success with {provider_name}")
                    logger.info(f"Processing time: {processing_time:.2f}s")
                    
                    return {
                        "success": True,
                        "response": result["response"],
                        "provider_used": provider_name,
                        "processing_time": processing_time,
                        "cascade_trace": cascade_trace
                    }
                else:
                    error = result.get("error", "Unknown error")
                    logger.warning(f"✗ {provider_name} failed: {error}")
                    cascade_trace.append(f"{provider_name}: failed - {error}")
                    
            except Exception as e:
                logger.error(f"✗ {provider_name} exception: {e}")
                cascade_trace.append(f"{provider_name}: exception - {str(e)}")
        
        # All providers failed
        processing_time = time.time() - start_time
        logger.error("All providers failed")
        
        return {
            "success": False,
            "response": "I apologize, but I'm experiencing technical difficulties. All providers failed.",
            "provider_used": "none",
            "processing_time": processing_time,
            "cascade_trace": cascade_trace
        }
    
    def _load_cascade_config(self):
        """Load provider cascade from config"""
        try:
            config_file = Path(self.config_path) / "providers.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.cascade = config.get("cascade", ["mcp", "local_mistral"])
            else:
                # Default cascade
                self.cascade = ["mcp", "local_mistral"]
                logger.info("Using default provider cascade")
        except Exception as e:
            logger.error(f"Failed to load cascade config: {e}")
            self.cascade = ["mcp", "local_mistral"]
    
    def _initialize_providers(self):
        """Initialize available providers"""
        try:
            # Import providers dynamically
            from providers.mcp_provider import MCPProvider
            from providers.local_mistral import LocalMistralProvider
            
            self.providers["mcp"] = MCPProvider()
            self.providers["local_mistral"] = LocalMistralProvider()
            
            logger.info(f"Initialized providers: {list(self.providers.keys())}")
            
        except ImportError as e:
            logger.error(f"Failed to import providers: {e}")
            logger.error("Provider modules may not exist yet")
    
    def get_status(self) -> Dict[str, Any]:
        """Get provider manager status"""
        return {
            "cascade": self.cascade,
            "providers_loaded": list(self.providers.keys()),
            "total_providers": len(self.providers)
        }
