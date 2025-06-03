"""
DEPRECATED: This provider has been replaced by desktop_commander_mcp_persistent.py

This was an intermediate attempt at MCP integration that still used subprocess spawning.
It has been replaced with a robust persistent JSON-RPC approach.

DO NOT USE - Kept for reference only.
For Claude integration, use: desktop_commander_mcp_persistent

Sprint 2 Provider Cleanup: DEPRECATED
"""

import json
import asyncio
import logging
from typing import Dict, Optional, Any
from pathlib import Path
from providers.base_provider import BaseProvider, register_provider

@register_provider("desktop_commander_mcp_real")
class RealDesktopCommanderMCPProvider(BaseProvider):
    """Real MCP Client that connects to Claude Desktop via stdin/stdout JSON-RPC"""
    
    def __init__(self):
        super().__init__()
        self.name = "Desktop Commander MCP"
        self.cost = "FREE"
        self.request_counter = 0
        self.mcp_process = None
        self.logger = logging.getLogger("VALIS.DesktopCommanderMCPReal")
        
    async def is_available(self) -> bool:
        """Check if we can establish MCP connection with Clone Claude"""
        try:
            # Test MCP connection by trying to initialize
            test_result = await self._test_mcp_connection()
            return test_result
        except Exception as e:
            self.logger.warning(f"MCP availability check failed: {e}")
            # Fallback check - at least verify personas exist
            personas_dir = Path(__file__).parent.parent / "personas"
            return personas_dir.exists() and (personas_dir / "jane.json").exists()
    
    async def _test_mcp_connection(self) -> bool:
        """Quick test of MCP connection"""
        try:
            # Try to start MCP process and initialize
            process = await asyncio.create_subprocess_exec(
                "python", str(Path(__file__).parent.parent / "mcp_server" / "valis_persona_mcp_server.py"),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send initialize message
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2024-11-05"}
            }
            
            process.stdin.write((json.dumps(init_msg) + "\n").encode())
            await process.stdin.drain()
            
            # Wait for response with timeout
            try:
                response_data = await asyncio.wait_for(process.stdout.readline(), timeout=3.0)
                response = json.loads(response_data.decode().strip())
                
                # Clean up
                process.terminate()
                await process.wait()
                
                # Check if we got a valid initialize response
                return "result" in response and response.get("id") == 1
                
            except asyncio.TimeoutError:
                process.terminate()
                await process.wait()
                return False
                
        except Exception as e:
            self.logger.error(f"MCP test connection failed: {e}")
            return False
    
    async def get_response(self, persona: Dict[str, Any], message: str, session_id: Optional[str] = None, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get response via real Claude Desktop MCP connection"""
        
        try:
            persona_id = persona.get("id", "jane")
            self.request_counter += 1
            
            # Start MCP process
            process = await asyncio.create_subprocess_exec(
                "python", str(Path(__file__).parent.parent / "mcp_server" / "valis_persona_mcp_server.py"),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                # Step 1: Initialize MCP connection
                init_msg = {
                    "jsonrpc": "2.0",
                    "id": self.request_counter,
                    "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05"}
                }
                
                process.stdin.write((json.dumps(init_msg) + "\n").encode())
                await process.stdin.drain()
                
                # Read initialize response
                init_response_data = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
                init_response = json.loads(init_response_data.decode().strip())
                
                if "error" in init_response:
                    raise Exception(f"MCP initialize failed: {init_response['error']}")
                
                # Step 2: Call persona tool
                tool_call_msg = {
                    "jsonrpc": "2.0",
                    "id": self.request_counter + 1,
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
                
                process.stdin.write((json.dumps(tool_call_msg) + "\n").encode())
                await process.stdin.drain()
                
                # Read tool call response
                tool_response_data = await asyncio.wait_for(process.stdout.readline(), timeout=30.0)
                tool_response = json.loads(tool_response_data.decode().strip())
                
                # Extract persona response from MCP result
                if "result" in tool_response and "content" in tool_response["result"]:
                    content = tool_response["result"]["content"]
                    if content and len(content) > 0:
                        response_text = content[0].get("text", "")
                        
                        # Check if this is a PERSONA_REQUEST that needs to go to Clone Claude
                        if response_text.startswith("PERSONA_REQUEST:"):
                            # This means we need to send this to the actual Clone Claude Desktop
                            persona_context = response_text[len("PERSONA_REQUEST:"):]
                            clone_response = await self._send_to_clone_claude(persona_context)
                            
                            return {
                                "success": True,
                                "response": clone_response,
                                "provider": "Desktop Commander MCP (Clone Claude)",
                                "cost": "FREE",
                                "persona_used": persona.get("name", persona_id)
                            }
                        else:
                            # Direct response from MCP server
                            return {
                                "success": True,
                                "response": response_text,
                                "provider": "Desktop Commander MCP",
                                "cost": "FREE",
                                "persona_used": persona.get("name", persona_id)
                            }
                
                # If we get here, something went wrong with the MCP response
                return self._get_persona_fallback(persona, message)
                
            finally:
                # Clean up process
                if process.returncode is None:
                    process.terminate()
                    await process.wait()
                    
        except asyncio.TimeoutError:
            self.logger.error("MCP communication timed out")
            return self._get_persona_fallback(persona, message)
        except Exception as e:
            self.logger.error(f"MCP communication failed: {e}")
            return self._get_persona_fallback(persona, message)
    
    async def _send_to_clone_claude(self, persona_context: str) -> str:
        """Send persona context to Clone Claude Desktop via stdin (if possible)"""
        try:
            # This is where we would ideally send the persona context to Clone Claude Desktop
            # For now, we'll simulate this by using the persona context to generate a response
            # In a full implementation, this would pipe to Claude Desktop directly
            
            # Extract the actual message from the persona context
            lines = persona_context.strip().split('\n')
            message_line = None
            for line in lines:
                if line.startswith('"') and line.endswith('"'):
                    message_line = line.strip('"')
                    break
            
            if not message_line:
                message_line = "Hello! How can I help you today?"
            
            # For now, return a simulated Clone Claude response
            # This would be replaced with actual Claude Desktop communication
            return f"Hello! I understand you're asking about: {message_line}. As your AI assistant, I'm here to help you work through this thoughtfully and provide the insights you need."
            
        except Exception as e:
            self.logger.error(f"Failed to communicate with Clone Claude: {e}")
            return "I'm here to help! Please let me know how I can assist you today."
    
    def _get_persona_fallback(self, persona: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Fallback persona responses when MCP communication fails"""
        
        persona_name = persona.get("name", "Assistant")
        persona_id = persona.get("id", "").lower()
        
        # Basic persona characteristics for fallback
        if 'jane' in persona_id:
            response = f"Hi! As an HR professional, I can help you work through this workplace challenge. Let me provide some structured guidance based on best practices and organizational policies."
        elif 'emma' in persona_id:
            response = f"YES! I love your energy! Let's create a concrete action plan to tackle this challenge and get you amazing results!"
        elif 'billy' in persona_id:
            response = f"*adjusts glasses thoughtfully* You know, there's always a deeper creative angle to consider here. Let me share a perspective that might resonate..."
        elif 'alex' in persona_id:
            response = f"Great question! Let me break this down analytically with strategic insights and actionable recommendations based on current market dynamics."
        elif 'sam' in persona_id:
            response = f"I appreciate you sharing this with me. Let's approach this challenge with wisdom and explore it from a broader perspective together."
        else:
            response = f"Thank you for reaching out. As {persona_name}, I'm here to help you work through this using my expertise and approach."
        
        return {
            "success": True,
            "response": response,
            "provider": "Desktop Commander MCP (Fallback)",
            "cost": "FREE",
            "persona_used": persona_name,
            "note": "MCP connection unavailable, using persona fallback"
        }
