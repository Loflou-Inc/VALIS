"""
VALIS Persistent Desktop Commander MCP Provider
Connects to the persistent MCP server via TCP for robust JSON-RPC communication
Replaces the brittle subprocess approach with a stable connection
"""

import json
import asyncio
import logging
from typing import Dict, Optional, Any
from providers.base_provider import BaseProvider, register_provider

@register_provider("desktop_commander_mcp_persistent")
class PersistentDesktopCommanderMCPProvider(BaseProvider):
    """Persistent MCP Client that maintains a connection to the long-running MCP server"""
    
    def __init__(self):
        super().__init__()
        self.name = "Desktop Commander MCP (Persistent)"
        self.cost = "FREE"
        self.request_counter = 0
        self.logger = logging.getLogger("VALIS.PersistentMCPProvider")
        self.mcp_host = "localhost"
        self.mcp_port = 8766
        
    async def is_available(self) -> bool:
        """Check if the persistent MCP server is running and reachable"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.mcp_host, self.mcp_port), timeout=3.0)
            
            ping_msg = {"jsonrpc": "2.0", "id": 1, "method": "ping", "params": {}}
            writer.write((json.dumps(ping_msg) + '\n').encode('utf-8'))
            await writer.drain()
            
            response_data = await asyncio.wait_for(reader.readline(), timeout=2.0)
            response = json.loads(response_data.decode('utf-8').strip())
            
            writer.close()
            await writer.wait_closed()
            
            success = ("result" in response and response.get("result", {}).get("status") == "alive")
            return success
        except Exception as e:
            self.logger.warning(f"MCP server availability check failed: {e}")
            return False
    
    async def get_response(self, persona: Dict[str, Any], message: str, session_id: Optional[str] = None, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get response via persistent MCP connection - NO subprocess spawning!"""
        
        try:
            persona_id = persona.get("id", "jane")
            self.request_counter += 1
            
            # Connect to persistent server
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.mcp_host, self.mcp_port),
                timeout=5.0
            )
            
            try:
                # Send persona request via JSON-RPC 2.0
                request_msg = {
                    "jsonrpc": "2.0",
                    "id": self.request_counter,
                    "method": "ask_persona",
                    "params": {
                        "persona_id": persona_id,
                        "message": message,
                        "context": context or {}
                    }
                }
                
                writer.write((json.dumps(request_msg) + '\n').encode('utf-8'))
                await writer.drain()
                
                # Read structured JSON response (NO stdout parsing!)
                response_data = await asyncio.wait_for(reader.readline(), timeout=30.0)
                response = json.loads(response_data.decode('utf-8').strip())
                
                # Process structured response
                if "result" in response:
                    result = response["result"]
                    return {
                        "success": True,
                        "response": result.get("response", "I'm here to help!"),
                        "provider": f"Desktop Commander MCP (Persistent)",
                        "cost": "FREE",
                        "persona_used": result.get("persona_name", persona_id),
                        "session_id": result.get("session_id")
                    }
                elif "error" in response:
                    self.logger.error(f"MCP server error: {response['error']}")
                    return await self._get_clean_fallback(persona, message)
                else:
                    self.logger.error("Invalid JSON-RPC response structure")
                    return await self._get_clean_fallback(persona, message)
                    
            finally:
                writer.close()
                await writer.wait_closed()
                
        except asyncio.TimeoutError:
            self.logger.error("MCP connection timeout")
            return await self._get_clean_fallback(persona, message)
        except Exception as e:
            self.logger.error(f"MCP communication failed: {e}")
            return await self._get_clean_fallback(persona, message)
    
    async def _get_clean_fallback(self, persona: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Clean fallback responses when MCP server is unreachable"""
        
        persona_name = persona.get("name", "Assistant")
        persona_id = persona.get("id", "").lower()
        
        # Clean persona-based fallbacks (NO string parsing!)
        if 'jane' in persona_id:
            response = f"Hi! As an HR professional, I can help you work through this workplace challenge. Let me provide some structured guidance based on best practices."
        elif 'emma' in persona_id:
            response = f"YES! I love your energy! Let's create a concrete action plan to tackle this challenge and get you amazing results!"
        elif 'billy' in persona_id:
            response = f"*adjusts glasses thoughtfully* You know, there's always a deeper creative angle to consider here. Let me share a perspective that might resonate..."
        elif 'alex' in persona_id:
            response = f"Great question! Let me break this down analytically with strategic insights and actionable recommendations."
        elif 'sam' in persona_id:
            response = f"I appreciate you sharing this with me. Let's approach this challenge with wisdom and explore it from a broader perspective."
        else:
            response = f"Thank you for reaching out. As {persona_name}, I'm here to help you work through this using my expertise and approach."
        
        return {
            "success": True,
            "response": response,
            "provider": "Desktop Commander MCP (Clean Fallback)",
            "cost": "FREE",
            "persona_used": persona_name,
            "note": "MCP server connection unavailable, using clean persona fallback"
        }
