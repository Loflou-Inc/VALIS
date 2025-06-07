#!/usr/bin/env python3
"""
MCPProvider - Wrapper that uses MCPRuntime + LocalMistral
Combines intelligent prompt composition with local LLM
"""

import logging
from typing import Dict, Any
from core.mcp_runtime import MCPRuntime
from providers.local_mistral import LocalMistralProvider

logger = logging.getLogger("MCPProvider")

class MCPProvider:
    """MCP Provider that combines MCPRuntime with LocalMistral"""
    
    def __init__(self):
        self.mcp_runtime = MCPRuntime()
        self.mistral_provider = LocalMistralProvider()
        logger.info("🔌 MCPProvider initialized")
    
    def ask(self, prompt: str, client_id: str, persona_id: str) -> Dict[str, Any]:
        """
        Use MCPRuntime to compose prompt, then send to LocalMistral
        """
        
        try:
            # Step 1: Compose prompt using MCPRuntime
            composition = self.mcp_runtime.compose_prompt(
                prompt, client_id, persona_id, context_mode="balanced"
            )
            
            final_prompt = composition["final_prompt"]
            metadata = composition["metadata"]
            
            logger.info(f"Composed prompt: {metadata['token_estimate']} tokens")
            
            # Step 2: Send to LocalMistral
            result = self.mistral_provider.ask(final_prompt, client_id, persona_id)
            
            if result["success"]:
                logger.info("✓ MCP chain successful")
                return {
                    "success": True,
                    "response": result["response"],
                    "metadata": metadata,
                    "latency": result.get("latency", 0)
                }
            else:
                logger.error(f"✗ LocalMistral failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"✗ MCP chain failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
