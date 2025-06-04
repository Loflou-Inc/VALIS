#!/usr/bin/env python3
"""
VALIS 2.0 Inference Entrypoint
Clean, simple entry point for all inference requests
"""

import logging
from core.provider_manager import ProviderManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VALIS2")

# Global provider manager
provider_manager = None

def initialize():
    """Initialize VALIS 2.0 system"""
    global provider_manager
    
    logger.info("🧠 VALIS 2.0 BOOTSTRAPPING...")
    
    try:
        provider_manager = ProviderManager()
        status = provider_manager.get_status()
        
        logger.info(f"✓ Cascade: {status['cascade']}")
        logger.info(f"✓ Providers: {status['providers_loaded']}")
        logger.info("🧠 VALIS 2.0 BOOTSTRAPPED")
        return True
        
    except Exception as e:
        logger.error(f"✗ Bootstrap failed: {e}")
        return False

def run_inference(prompt: str, client_id: str = "default", 
                 persona_id: str = "kai") -> dict:
    """
    Main inference function - the one clean entry point
    
    Args:
        prompt: User input message
        client_id: Client identifier  
        persona_id: Persona to use
        
    Returns:
        Response dictionary with success/error info
    """
    
    if provider_manager is None:
        if not initialize():
            return {"success": False, "error": "System not initialized"}
    
    logger.info(f"=== INFERENCE REQUEST ===")
    logger.info(f"Prompt: {prompt[:100]}...")
    logger.info(f"Client: {client_id}, Persona: {persona_id}")
    
    # Route through provider manager
    result = provider_manager.ask(prompt, client_id, persona_id)
    
    logger.info(f"Result: {result.get('success')} via {result.get('provider_used')}")
    
    return result

if __name__ == "__main__":
    # Test the system
    print("Testing VALIS 2.0...")
    
    result = run_inference(
        "Hello! Can you explain how your memory system works?",
        client_id="test_client",
        persona_id="kai"
    )
    
    print(f"Success: {result['success']}")
    print(f"Provider: {result.get('provider_used')}")
    print(f"Response: {result.get('response', '')[:200]}...")
