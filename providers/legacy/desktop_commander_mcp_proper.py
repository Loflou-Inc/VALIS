"""
DEPRECATED: This provider has been replaced by desktop_commander_mcp_persistent.py

This was an attempt at "proper" MCP integration but still used subprocess spawning.
It has been replaced with a robust persistent JSON-RPC approach.

DO NOT USE - Kept for reference only.
For Claude integration, use: desktop_commander_mcp_persistent

Sprint 2 Provider Cleanup: DEPRECATED
"""

import json
import asyncio
import subprocess
import tempfile
import os
from typing import Dict, Optional, Any
from pathlib import Path
from providers.base_provider import BaseProvider, register_provider

@register_provider("desktop_commander_mcp_proper")
class ProperDesktopCommanderMCPProvider(BaseProvider):
    """Proper MCP Provider that communicates with Claude Desktop via JSON-RPC stdin/stdout"""
    
    def __init__(self):
        super().__init__()
        self.name = "Desktop Commander MCP (Proper)"
        self.cost = "FREE"
        self.request_counter = 0
        
    async def is_available(self) -> bool:
        """Check if Claude Desktop MCP server is available via proper protocol"""
        try:
            # Test MCP connection by attempting initialize handshake
            result = await self._send_mcp_request({
                "jsonrpc": "2.0",
                "id": "test_availability",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "valis-test",
                        "version": "1.0.0"
                    }
                }
            })
            
            # If we get a valid initialize response, MCP is available
            return result is not None and "result" in result
            
        except Exception:
            # Fallback check - if personas directory exists, we can use basic fallbacks
            personas_dir = Path(__file__).parent.parent / "personas"
            return personas_dir.exists() and (personas_dir / "jane.json").exists()
