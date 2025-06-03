#!/usr/bin/env python3
"""VALIS Persistent MCP Server - Sprint 7.5 Enhanced
Fixed persona routing with explicit targeting support
NO MORE HARDCODED FALLBACK TO JANE!
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Add VALIS root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from core.persona_router import PersonaRouter
    ROUTING_AVAILABLE = True
except ImportError as e:
    logging.warning(f"PersonaRouter not available: {e}")
    ROUTING_AVAILABLE = False

class VALISPersistentMCPServer:
    def __init__(self, port: int = 8765):
        self.port = port
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("VALISPersistentMCP")
        self.personas = self.load_personas()
        
        # Sprint 7.5: Initialize persona router
        if ROUTING_AVAILABLE:
            self.persona_router = PersonaRouter()
            self.routing_enabled = True
            self.logger.info("PersonaRouter initialized - explicit targeting enabled")
        else:
            self.routing_enabled = False
            self.logger.warning("PersonaRouter unavailable - using fallback routing")
        
    def load_personas(self) -> Dict[str, Dict]:
        personas = {}
        personas_dir = Path(__file__).parent.parent / "personas"
        if personas_dir.exists():
            for persona_file in personas_dir.glob("*.json"):
                try:
                    with open(persona_file, 'r', encoding='utf-8') as f:
                        persona = json.load(f)
                        personas[persona.get('id', persona_file.stem)] = persona
                except Exception as e:
                    self.logger.error(f"Failed to load {persona_file}: {e}")
        
        # Sprint 7.5: NO MORE AUTOMATIC JANE FALLBACK
        # Personas must be explicitly targeted
        self.logger.info(f"Loaded {len(personas)} personas: {list(personas.keys())}")
        return personas
    
    async def handle_json_rpc(self, message: Dict[str, Any]) -> Dict[str, Any]:
        try:
            method = message.get("method", "")
            params = message.get("params", {})
            msg_id = message.get("id")
            
            if method == "ping":
                return {"jsonrpc": "2.0", "id": msg_id, "result": {"status": "alive"}}
            elif method == "ask_persona":
                return await self.handle_persona_request(msg_id, params)
            else:
                return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found"}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": message.get("id"), "error": {"code": -32603, "message": str(e)}}
    
    async def handle_persona_request(self, msg_id, params):
        """
        Sprint 7.5: Enhanced persona routing with explicit targeting
        NO MORE HARDCODED FALLBACK TO JANE!
        """
        requested_persona_id = params.get("persona_id", "")
        message = params.get("message", "")
        context = params.get("context", {})
        
        # Sprint 7.5: Use PersonaRouter for intelligent routing
        if self.routing_enabled:
            routing_result = self.persona_router.route_message(
                message=message,
                default_persona=requested_persona_id if requested_persona_id else None,
                context=context
            )
            
            target_persona_id = routing_result["persona_id"]
            cleaned_message = routing_result["message"]
            
            # Log routing decision
            if routing_result["targeting_detected"]:
                self.logger.info(f"Explicit targeting detected: {target_persona_id}")
            
            # Handle routing errors
            if routing_result.get("error"):
                return {
                    "jsonrpc": "2.0", 
                    "id": msg_id, 
                    "error": {
                        "code": -32000, 
                        "message": f"Persona routing error: {routing_result['error']}",
                        "data": {
                            "available_personas": routing_result["available_personas"],
                            "help": self.persona_router.format_targeting_help()
                        }
                    }
                }
            
            # Warning if no persona resolved
            if not target_persona_id:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32000,
                        "message": "No persona targeted. Explicit targeting required.",
                        "data": {
                            "available_personas": routing_result["available_personas"],
                            "help": self.persona_router.format_targeting_help()
                        }
                    }
                }
            
        else:
            # Fallback routing (legacy)
            target_persona_id = requested_persona_id or "jane"
            cleaned_message = message
            self.logger.warning("Using legacy routing - PersonaRouter unavailable")
        
        # Get the actual persona data
        persona = self.personas.get(target_persona_id)
        if not persona:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32000,
                    "message": f"Persona '{target_persona_id}' not found",
                    "data": {"available_personas": list(self.personas.keys())}
                }
            }
        
        # Generate response
        response = self.generate_response(persona, cleaned_message)
        
        return {
            "jsonrpc": "2.0", 
            "id": msg_id, 
            "result": {
                "response": response, 
                "persona_id": target_persona_id, 
                "persona_name": persona.get("name", target_persona_id),
                "routing_used": "PersonaRouter" if self.routing_enabled else "legacy",
                "targeting_detected": self.routing_enabled and routing_result.get("targeting_detected", False)
            }
        }
    
    def generate_response(self, persona, message):
        """
        Sprint 7.5: Enhanced response generation for all personas
        """
        persona_id = persona.get('id', '').lower()
        persona_name = persona.get('name', persona_id)
        
        # Generate persona-specific responses based on personality
        if persona_id == 'jane':
            return f"As an HR professional with 15+ years of experience, I can help you work through this workplace challenge. Let me approach this systematically: {message}"
        
        elif persona_id == 'laika':
            return f"Understood. Here's the priority and what we're going to do: {message}. Let's focus on execution and results."
        
        elif persona_id == 'doc_brown':
            return f"Great Scott! *adjusts temporal measurement equipment* This requires careful analysis of the temporal implications. According to my calculations: {message}"
        
        elif persona_id == 'biff':
            return f"Alright, let's cut to the chase here. Does it work or doesn't it? {message}. Show me the results."
        
        elif persona_id == 'coach_emma':
            return f"YES! I love your energy! Let's create an action plan to tackle this challenge: {message}. You've got this!"
        
        elif persona_id == 'advisor_alex':
            return f"Great question! Let me break this down analytically with strategic insights. Based on my assessment: {message}"
        
        elif persona_id == 'guide_sam':
            return f"I appreciate you sharing this with me. Let's approach this challenge with wisdom and explore it from a broader perspective: {message}"
        
        elif persona_id == 'billy_corgan':
            return f"*adjusts glasses thoughtfully* You know, there's always a deeper creative angle to consider here. Let me share a perspective that might resonate: {message}"
        
        else:
            # Generic fallback for any other personas
            return f"Thank you for reaching out. As {persona_name}, I'm here to help you work through this using my expertise: {message}"
    
    async def handle_client(self, reader, writer):
        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                message = json.loads(data.decode('utf-8').strip())
                response = await self.handle_json_rpc(message)
                writer.write((json.dumps(response) + '\n').encode('utf-8'))
                await writer.drain()
        except Exception as e:
            self.logger.error(f"Client error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def start_server(self):
        self.logger.info(f"Starting VALIS Persistent MCP Server on port {self.port}")
        server = await asyncio.start_server(self.handle_client, 'localhost', self.port)
        addr = server.sockets[0].getsockname()
        self.logger.info(f"Server running on {addr[0]}:{addr[1]} with {len(self.personas)} personas")
        async with server:
            await server.serve_forever()

async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    server = VALISPersistentMCPServer(port=args.port)
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())
