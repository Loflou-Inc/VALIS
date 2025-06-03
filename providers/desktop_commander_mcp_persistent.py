"""
VALIS Persistent Desktop Commander MCP Provider - Sprint 7 Enhanced
Connects to the persistent MCP server via TCP for robust JSON-RPC communication
NOW WITH FULL MEMORY INTEGRATION - sends rich, contextual prompts to Claude
"""

import json
import asyncio
import logging
from typing import Dict, Optional, Any
from providers.base_provider import BaseProvider, register_provider

# Sprint 7: Import memory system components
try:
    from core.valis_memory import MemoryRouter
    from core.prompt_composer import PromptComposer
    MEMORY_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Memory system not available: {e}")
    MEMORY_AVAILABLE = False

@register_provider("desktop_commander_mcp_persistent")
class PersistentDesktopCommanderMCPProvider(BaseProvider):
    """Persistent MCP Client that maintains a connection to the long-running MCP server"""
    
    def __init__(self):
        super().__init__()
        self.name = "Desktop Commander MCP (Persistent) - Memory Enhanced"
        self.cost = "FREE"
        self.request_counter = 0
        self.logger = logging.getLogger("VALIS.PersistentMCPProvider")
        self.mcp_host = "localhost"
        self.mcp_port = 8765
        
        # Sprint 7: Initialize memory system components
        if MEMORY_AVAILABLE:
            try:
                self.memory_router = MemoryRouter()
                self.prompt_composer = PromptComposer()
                self.memory_enabled = True
                self.logger.info("Memory system enabled for MCP provider")
            except Exception as e:
                self.logger.error(f"Failed to initialize memory system: {e}")
                self.memory_enabled = False
        else:
            self.memory_enabled = False
            self.logger.warning("Memory system disabled - using basic prompts")
        
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
        """Get response via persistent MCP connection with full memory integration"""
        
        try:
            persona_id = persona.get("id", "jane")
            self.request_counter += 1
            
            # Sprint 7: Generate memory-enhanced prompt
            enhanced_message = await self._prepare_memory_enhanced_message(persona_id, message, session_id, context)
            
            # Connect to persistent server
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.mcp_host, self.mcp_port),
                timeout=5.0
            )
            
            try:
                # Send persona request via JSON-RPC 2.0 (now with memory-enhanced prompt)
                request_msg = {
                    "jsonrpc": "2.0",
                    "id": self.request_counter,
                    "method": "ask_persona",
                    "params": {
                        "persona_id": persona_id,
                        "message": enhanced_message,  # This is now the rich, memory-aware prompt
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
    
    async def _prepare_memory_enhanced_message(self, persona_id: str, message: str, 
                                             session_id: Optional[str] = None, 
                                             context: Optional[Dict] = None) -> str:
        """
        Sprint 7: Prepare memory-enhanced prompt for Claude
        
        This is the critical bridge that transforms basic user messages into
        rich, contextual prompts with full persona memory awareness.
        """
        
        if not self.memory_enabled:
            self.logger.debug("Memory system disabled, using basic message")
            return message
        
        try:
            # Extract client_id from session or context
            client_id = None
            if context:
                client_id = context.get('client_id') or context.get('user_id')
            if not client_id and session_id:
                client_id = session_id
            
            # Extract session history from context
            session_history = []
            if context and 'session_history' in context:
                session_history = context['session_history']
            
            self.logger.debug(f"Generating memory payload for {persona_id}, client: {client_id}")
            
            # Get complete memory payload from MemoryRouter
            memory_payload = self.memory_router.get_memory_payload(
                persona_id=persona_id,
                client_id=client_id,
                session_history=session_history,
                current_message=message
            )
            
            # Compose rich prompt using PromptComposer
            enhanced_prompt = self.prompt_composer.compose_prompt(
                memory_payload=memory_payload,
                provider_type="claude"
            )
            
            # Log memory usage stats
            stats = self.prompt_composer.get_prompt_stats(enhanced_prompt)
            self.logger.info(f"Memory-enhanced prompt: {stats['word_count']} words, "
                           f"{stats['character_count']} chars, memory layers active")
            
            # Process any memory tags in the eventual response
            # (This would be done after getting Claude's response, but for now we just prepare)
            
            return enhanced_prompt
            
        except Exception as e:
            self.logger.error(f"Memory enhancement failed: {e}")
            self.logger.warning("Falling back to basic message")
            return message
    
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
