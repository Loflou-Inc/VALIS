#!/usr/bin/env python3
"""
VALIS Persona MCP Server
MCP server for Claude Desktop to handle VALIS persona requests
This creates the "clone Claude" that VALIS connects to
"""

import asyncio
import json
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# MCP Server for Claude Desktop
class VALISPersonaMCPServer:
    """MCP Server for VALIS persona interactions"""
    
    def __init__(self):
        self.personas = self.load_personas()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("VALISPersonaMCP")
    
    def load_personas(self) -> Dict[str, Dict]:
        """Load persona definitions"""
        personas = {}
        personas_dir = Path(__file__).parent.parent / "personas"
        
        if personas_dir.exists():
            for persona_file in personas_dir.glob("*.json"):
                try:
                    with open(persona_file, 'r') as f:
                        persona = json.load(f)
                        personas[persona.get('id', persona_file.stem)] = persona
                except Exception as e:
                    self.logger.error(f"Failed to load {persona_file}: {e}")
        
        return personas
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP messages"""
        
        method = message.get("method", "")
        params = message.get("params", {})
        msg_id = message.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "valis-persona-server",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [
                        {
                            "name": "get_persona_response",
                            "description": "Get AI response as a specific VALIS persona",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "persona_id": {"type": "string"},
                                    "message": {"type": "string"},
                                    "context": {"type": "object"}
                                },
                                "required": ["persona_id", "message"]
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            if tool_name == "get_persona_response":
                return await self.handle_persona_request(msg_id, params.get("arguments", {}))
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }
    
    async def handle_persona_request(self, msg_id: Any, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle persona response request"""
        
        persona_id = args.get("persona_id", "jane")
        message = args.get("message", "")
        context = args.get("context", {})
        
        # Get persona data
        persona = self.personas.get(persona_id, self.personas.get("jane", {}))
        
        # Build persona context for Claude
        persona_prompt = self.build_persona_context(persona, message, context)
        
        # This gets sent to Claude via MCP - Claude will respond AS the persona
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [
                    {
                        "type": "text", 
                        "text": f"PERSONA_REQUEST:{persona_prompt}"
                    }
                ],
                "isError": False
            }
        }
    
    def build_persona_context(self, persona: Dict, message: str, context: Dict) -> str:
        """Build context for Claude to respond as persona"""
        
        name = persona.get('name', 'Assistant')
        description = persona.get('description', '')
        background = persona.get('background', '')
        tone = persona.get('tone', 'Professional')
        traits = ', '.join(persona.get('personality_traits', []))
        expertise = ', '.join(persona.get('expertise_areas', []))
        phrases = persona.get('language_patterns', {}).get('common_phrases', [])
        
        context_str = f"""
You are now {name}. {description}

Your background: {background}
Your personality traits: {traits}
Your expertise: {expertise}
Your tone: {tone}

Common phrases you use: {', '.join(phrases[:3])}

Respond to this user message AS {name}, using your personality and expertise:
"{message}"

Remember: You ARE {name}, not Claude roleplaying. Respond naturally in character.
"""
        
        return context_str.strip()

async def main():
    """Main server loop"""
    server = VALISPersonaMCPServer()
    
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            
            if not line:
                break
                
            message = json.loads(line.strip())
            response = await server.handle_message(message)
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            server.logger.error(f"Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
