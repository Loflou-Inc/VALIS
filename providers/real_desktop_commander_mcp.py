"""
REAL Desktop Commander MCP Client Provider
Actually connects to MCP server via JSON-RPC protocol
"""

import json
import asyncio
import subprocess
from typing import Dict, Optional, Any
from pathlib import Path
from providers.base_provider import BaseProvider, register_provider

@register_provider("desktop_commander_mcp_real")
class RealDesktopCommanderMCPProvider(BaseProvider):
    """REAL MCP Provider that connects to actual MCP server"""
    
    def __init__(self):
        super().__init__()
        self.name = "Desktop Commander MCP (REAL)"
        self.cost = "FREE"
        self.mcp_server_path = Path(__file__).parent.parent / "mcp_server" / "desktop_commander_mcp_server.py"
        self.request_counter = 0
        
    async def is_available(self) -> bool:
        """Check if MCP server can be started"""
        try:
            return self.mcp_server_path.exists()
        except Exception:
            return False
    
    async def get_response(self, persona: Dict[str, Any], message: str, session_id: Optional[str] = None, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get response via REAL MCP protocol"""
        
        try:
            persona_id = persona.get("id", "jane")
            
            # Start MCP server process
            process = await asyncio.create_subprocess_exec(
                "python", str(self.mcp_server_path),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Initialize MCP connection
            self.request_counter += 1
            init_request = {
                "jsonrpc": "2.0",
                "id": f"init_{self.request_counter}",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "valis-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send initialize request
            process.stdin.write((json.dumps(init_request) + '\n').encode())
            await process.stdin.drain()
            
            # Read initialize response
            init_response_line = await process.stdout.readline()
            init_response = json.loads(init_response_line.decode().strip())
            
            # Send persona response request  
            self.request_counter += 1
            persona_request = {
                "jsonrpc": "2.0",
                "id": f"persona_{self.request_counter}",
                "method": "tools/call",
                "params": {
                    "name": "get_persona_response",
                    "arguments": {
                        "persona_id": persona_id,
                        "message": message,
                        "context": context or {}
                    }
                }
            }
            
            # Send request
            process.stdin.write((json.dumps(persona_request) + '\n').encode())
            await process.stdin.drain()
            
            # Read response
            response_line = await process.stdout.readline()
            response = json.loads(response_line.decode().strip())
            
            # Close MCP connection
            process.stdin.close()
            await process.wait()
            
            # Extract response text
            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"]
                if content and len(content) > 0:
                    response_text = content[0].get("text", "")
                    
                    return {
                        "success": True,
                        "response": response_text,
                        "provider": "Desktop Commander MCP (REAL)",
                        "cost": "FREE",
                        "persona_used": persona.get("name", persona_id)
                    }
            
            # Fallback if response parsing fails
            return {
                "success": False,
                "error": "Failed to parse MCP response",
                "provider": "Desktop Commander MCP (REAL)"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "Desktop Commander MCP (REAL)"
            }
