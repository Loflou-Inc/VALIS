#!/usr/bin/env python3
"""VALIS Persistent MCP Server - Simplified for Sprint 1"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any

class VALISPersistentMCPServer:
    def __init__(self, port: int = 8765):
        self.port = port
        self.personas = self.load_personas()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("VALISPersistentMCP")
        
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
        if not personas:
            personas['jane'] = {'id': 'jane', 'name': 'Jane'}
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
        persona_id = params.get("persona_id", "jane")
        message = params.get("message", "")
        
        # Find the best matching persona
        persona = self.personas.get(persona_id)
        if not persona:
            # Try partial matching
            for pid, p in self.personas.items():
                if persona_id.lower() in pid.lower() or pid.lower() in persona_id.lower():
                    persona = p
                    break
            if not persona:
                persona = self.personas.get("jane", {'id': 'jane', 'name': 'Jane'})
        
        response = self.generate_response(persona, message)
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"response": response, "persona_id": persona_id, "persona_name": persona.get("name", persona_id)}}
    
    def generate_response(self, persona, message):
        persona_id = persona.get('id', '').lower()
        
        # Handle exact matches first
        if persona_id in self.personas:
            actual_persona = self.personas[persona_id]
        else:
            # Handle partial matches for common names
            actual_persona = None
            for pid, p in self.personas.items():
                if ('jane' in persona_id and 'jane' in pid.lower()) or \
                   ('emma' in persona_id and 'emma' in pid.lower()) or \
                   ('billy' in persona_id and 'billy' in pid.lower()) or \
                   ('alex' in persona_id and 'alex' in pid.lower()) or \
                   ('sam' in persona_id and 'sam' in pid.lower()):
                    actual_persona = p
                    persona_id = pid.lower()
                    break
            
            if not actual_persona:
                actual_persona = persona
        
        # Generate persona-specific responses
        if 'jane' in persona_id:
            return f"Hi! As an HR professional, I can help you work through this challenge: {message}"
        elif 'emma' in persona_id:
            return f"YES! Let's tackle '{message}' and get amazing results!"
        elif 'billy' in persona_id:
            return f"*adjusts glasses* There's a deeper angle to '{message}' worth exploring..."
        elif 'alex' in persona_id:
            return f"Strategic analysis of '{message}': Let me break this down with actionable insights."
        elif 'sam' in persona_id:
            return f"Wisdom perspective on '{message}': Let's explore this thoughtfully together."
        else:
            return f"Thank you for reaching out about '{message}'. I'm here to help!"
    
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
