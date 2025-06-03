"""
DEPRECATED: This provider has been replaced by desktop_commander_mcp_persistent.py

This legacy provider uses brittle subprocess spawning and stdout parsing.
It has been replaced with a robust persistent JSON-RPC approach.

DO NOT USE - Kept for reference only.
For Claude integration, use: desktop_commander_mcp_persistent

Sprint 2 Provider Cleanup: DEPRECATED
"""

import json
import subprocess
import tempfile
import asyncio
import os
from typing import Dict, Optional, Any
from pathlib import Path
from providers.base_provider import BaseProvider, register_provider

@register_provider("desktop_commander_mcp")
class DesktopCommanderProvider(BaseProvider):
    """Provider that connects to Desktop Commander MCP for persona responses"""
    
    def __init__(self):
        super().__init__()
        self.name = "Desktop Commander MCP"
        self.cost = "FREE"
        self.mcp_interface_path = Path(__file__).parent.parent / "mcp_integration" / "dc_persona_interface.py"
        
    async def is_available(self) -> bool:
        """Check if Desktop Commander MCP is available (DEV-601: Now fully async!)"""
        try:
            # Check if the MCP interface script exists
            if not self.mcp_interface_path.exists():
                return False
            
            # Try to run a simple test using async subprocess (DEV-601)
            process = await asyncio.create_subprocess_exec(
                "python", str(self.mcp_interface_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5.0)
                output = stdout.decode('utf-8') + stderr.decode('utf-8')
                
                # If it returns usage info, it's working
                return "Usage:" in output or "error" in output
                
            except asyncio.TimeoutError:
                # Kill the process if it takes too long
                process.kill()
                await process.wait()
                return False
            
        except Exception:
            return False    
    async def get_response(self, persona: Dict[str, Any], message: str, session_id: Optional[str] = None, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get a persona response via Desktop Commander MCP"""
        
        try:
            # Get persona ID from persona data
            persona_id = persona.get("id", "jane")
            if not persona_id:
                # Try to infer from name
                persona_name = persona.get("name", "").lower()
                if "emma" in persona_name or "coach" in persona_name:
                    persona_id = "coach_emma"
                elif "billy" in persona_name or "corgan" in persona_name:
                    persona_id = "billy_corgan"
                else:
                    persona_id = "jane"
            
            # Prepare context file if needed
            context_file = None
            if context:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                    json.dump(context, tmp)
                    context_file = tmp.name
            
            # Build command
            cmd = ["python", str(self.mcp_interface_path), persona_id, message]
            if context_file:
                cmd.append(context_file)
            
            # Execute the MCP interface
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Clean up context file
            if context_file:
                try:
                    os.unlink(context_file)
                except:
                    pass            
            if process.returncode == 0:
                output = stdout.decode('utf-8')
                
                # Look for the fallback JSON response
                if "FALLBACK_RESPONSE_JSON:" in output:
                    json_start = output.find("FALLBACK_RESPONSE_JSON:") + len("FALLBACK_RESPONSE_JSON:")
                    json_text = output[json_start:].strip()
                    
                    try:
                        response_data = json.loads(json_text)
                        return {
                            "success": True,
                            "response": response_data.get("response", "I'm here to help!"),
                            "provider": "Desktop Commander MCP",
                            "cost": "FREE",
                            "persona_used": response_data.get("persona_name", persona_id)
                        }
                    except json.JSONDecodeError:
                        pass
                
                # If no JSON found, look for Claude's direct response
                lines = output.split('\n')
                for i, line in enumerate(lines):
                    if "Claude:" in line and i + 1 < len(lines):
                        response = '\n'.join(lines[i+1:]).strip()
                        if response:
                            return {
                                "success": True,
                                "response": response,
                                "provider": "Desktop Commander MCP (Direct)",
                                "cost": "FREE"
                            }
            
            # If we get here, something went wrong - return a basic fallback
            return {
                "success": True,
                "response": self._get_basic_fallback(persona, message),
                "provider": "Desktop Commander MCP (Basic Fallback)",
                "cost": "FREE"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "Desktop Commander MCP"
            }    
    def _get_basic_fallback(self, persona: Dict[str, Any], message: str) -> str:
        """Basic fallback response based on persona"""
        persona_name = persona.get("name", "Assistant")
        persona_id = persona.get("id", "").lower()
        
        if 'jane' in persona_id or 'jane' in persona_name.lower():
            return f"Hi! As an HR professional, I understand you're asking about '{message[:50]}...' Let me help you work through this workplace challenge systematically."
        elif 'emma' in persona_id or 'emma' in persona_name.lower():
            return f"I love your energy around '{message[:50]}...' Let's turn this into actionable steps and get results!"
        elif 'billy' in persona_id or 'corgan' in persona_name.lower():
            return f"Interesting perspective on '{message[:50]}...' You know, there's often a deeper creative angle to consider here..."
        else:
            return f"Thanks for reaching out about this. As {persona_name}, I'm here to help you work through this challenge."