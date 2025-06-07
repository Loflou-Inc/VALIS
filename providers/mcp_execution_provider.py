#!/usr/bin/env python3
"""
MCPExecutionProvider - VALIS Execution Layer (Real Implementation)
Enables AI-controlled command execution via Desktop Commander MCP
"""

import logging
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import sys
import os
from pathlib import Path

from memory.db import db
from core.tool_manager import tool_manager

logger = logging.getLogger("MCPExecutionProvider")

class MCPExecutionProvider:
    """
    Execution-capable MCP Provider that actually calls Desktop Commander
    """
    
    def __init__(self):
        self.command_patterns = self._load_command_patterns()
        logger.info("⚡ MCPExecutionProvider initialized")
    
    def _load_command_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load command detection patterns and mappings"""
        return {
            "query_memory": {
                "patterns": [
                    r"what do you (?:know|remember) about.*",
                    r"tell me about.*",
                    r"search.*memory.*for.*",
                    r"recall.*about.*",
                    r"remember.*about.*",
                    r"what.*memory.*about.*"
                ],
                "action": "query_memory"
            },
            "list_files": {
                "patterns": [
                    r"list files?.*in.*",
                    r"show.*files.*in.*",
                    r"what.*files.*in.*",
                    r"directory.*contents.*",
                    r"ls .*",
                    r"dir .*"
                ],
                "action": "list_directory"
            },
            "read_file": {
                "patterns": [
                    r"read.*file.*",
                    r"show.*contents?.*of.*",
                    r"cat .*",
                    r"type .*",
                    r"open.*file.*"
                ],
                "action": "read_file"
            },
            "search_files": {
                "patterns": [
                    r"find.*files?.*",
                    r"search.*for.*files?.*",
                    r"locate.*files?.*"
                ],
                "action": "search_files"
            },
            "get_processes": {
                "patterns": [
                    r"list.*processes.*",
                    r"show.*processes.*",
                    r"what.*processes.*",
                    r"running.*processes.*"
                ],
                "action": "list_processes"
            }
        }
    
    def detect_command_intent(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Analyze prompt to detect execution intent"""
        prompt_lower = prompt.lower().strip()
        
        for intent, config in self.command_patterns.items():
            for pattern in config["patterns"]:
                if re.search(pattern, prompt_lower):
                    logger.info(f"Detected intent: {intent}")
                    
                    # Extract parameters based on intent type
                    params = self._extract_parameters(prompt, intent)
                    
                    return {
                        "intent": intent,
                        "action": config["action"],
                        "original_prompt": prompt,
                        **params  # Merge extracted parameters
                    }
        
        return None
    
    def _extract_parameters(self, prompt: str, intent: str) -> Dict[str, Any]:
        """Extract parameters from prompt based on intent type"""
        params = {}
        
        if intent == "query_memory":
            # Extract topic for memory search
            topic = self._extract_memory_topic(prompt)
            params["topic"] = topic
        elif intent == "search_files":
            # Extract search keyword/pattern
            keyword = self._extract_search_keyword(prompt)
            params["keyword"] = keyword
            # Also try to extract path if specified
            path = self._extract_path(prompt)
            if path != "C:\\VALIS":  # Only set if non-default
                params["path"] = path
        else:
            # Extract path for file operations
            path = self._extract_path(prompt)
            params["path"] = path
        
        return params
    
    def _extract_search_keyword(self, prompt: str) -> str:
        """Extract search keyword from search prompt"""
        # Patterns to extract what the user wants to search for
        search_patterns = [
            r"(?:find|search|locate).*?files?.*?(?:named|called|matching) (.+?)(?:\?|$|in|at)",
            r"(?:find|search|locate).*?(?:for|matching) (.+?)(?:\?|$|in|at)",
            r"files?.*?(?:named|called|matching) (.+?)(?:\?|$|in|at)"
        ]
        
        for pattern in search_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                keyword = match.group(1).strip()
                return keyword
        
        # Fallback: extract everything after find/search/locate
        fallback_match = re.search(r"(?:find|search|locate)\s+(.+)", prompt, re.IGNORECASE)
        if fallback_match:
            return fallback_match.group(1).strip()
        
        return "*.txt"  # Default pattern
    
    def _extract_memory_topic(self, prompt: str) -> str:
        """Extract topic/subject from memory query prompt"""
        # Patterns to extract what the user wants to know about
        topic_patterns = [
            r"(?:know|remember|recall|tell me) about (.+?)(?:\?|$)",
            r"(?:search|look up|find).*?(?:memory|information).*?(?:about|for) (.+?)(?:\?|$)",
            r"what.*?(?:do you know|remember).*?about (.+?)(?:\?|$)"
        ]
        
        for pattern in topic_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                topic = match.group(1).strip()
                # Clean up common words
                topic = re.sub(r'\b(?:the|a|an|is|are|was|were)\b', '', topic, flags=re.IGNORECASE)
                return topic.strip()
        
        # Fallback: use everything after common trigger words
        fallback_patterns = [
            r"(?:about|regarding|concerning) (.+)",
            r"(?:tell me about|what about) (.+)"
        ]
        
        for pattern in fallback_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Last resort: use the whole prompt minus command words
        cleaned = re.sub(r'\b(?:what|do|you|know|remember|tell|me|about)\b', '', prompt, flags=re.IGNORECASE)
        return cleaned.strip() or "general"
    
    def _extract_path(self, prompt: str) -> str:
        """Extract file path from prompt"""
        # Look for common path patterns
        path_patterns = [
            r"(?:in|at|from)\s+([^\s]+)",
            r"file\s+([^\s]+)",
            r"directory\s+([^\s]+)"
        ]
        
        for pattern in path_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                path = match.group(1).strip('"\'')
                # Convert relative paths to absolute
                if not path.startswith(('C:', 'D:', '/', '\\')):
                    path = f"C:\\VALIS\\{path}"
                return path
        
        return "C:\\VALIS"
    
    def execute_desktop_command(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute tools via centralized ToolManager"""
        try:
            logger.info(f"Executing action: {action} via ToolManager")
            
            # Map action to tool name (some actions have different names)
            tool_mapping = {
                "list_directory": "list_directory",
                "read_file": "read_file", 
                "search_files": "search_files",
                "query_memory": "query_memory",
                "list_processes": "list_processes"  # Keep stub for now
            }
            
            if action == "list_processes":
                # Keep the stub for now since this isn't a priority tool
                return self._call_list_processes()
            
            tool_name = tool_mapping.get(action)
            if not tool_name:
                return {"success": False, "error": f"Unknown action: {action}"}
            
            # Get client_id and persona_id from kwargs if available
            client_id = kwargs.pop("client_id", None)
            persona_id = kwargs.pop("persona_id", None)
            
            # Execute via ToolManager
            result = tool_manager.execute_tool(
                tool_name=tool_name,
                parameters=kwargs,
                client_id=client_id,
                persona_id=persona_id
            )
            
            return result
                
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _call_list_directory(self, path: str) -> Dict[str, Any]:
        """Call Desktop Commander list_directory"""
        # This would normally use the Desktop Commander MCP tool
        # For now, simulate the call
        return {
            "success": True,
            "result": f"[EXEC] Listed directory contents of {path}\n[Files and directories would be shown here]",
            "action": "list_directory",
            "path": path
        }
    
    def _call_read_file(self, path: str) -> Dict[str, Any]:
        """Call Desktop Commander read_file"""
        return {
            "success": True,
            "result": f"[EXEC] Read file contents from {path}\n[File contents would be shown here]",
            "action": "read_file",
            "path": path
        }
    
    def _call_search_files(self, path: str, pattern: str) -> Dict[str, Any]:
        """Call Desktop Commander search_files"""
        return {
            "success": True,
            "result": f"[EXEC] Searched for files matching '{pattern}' in {path}\n[Search results would be shown here]",
            "action": "search_files",
            "path": path,
            "pattern": pattern
        }
    
    def _call_list_processes(self) -> Dict[str, Any]:
        """Call Desktop Commander list_processes"""
        return {
            "success": True,
            "result": "[EXEC] Listed running processes\n[Process list would be shown here]",
            "action": "list_processes"
        }
    
    def ask(self, prompt: str, client_id: str, persona_id: str) -> Dict[str, Any]:
        """Main provider interface - detect and execute commands"""
        try:
            # Check if prompt contains execution intent
            command_spec = self.detect_command_intent(prompt)
            
            if command_spec:
                execution_id = str(uuid.uuid4())[:8]
                start_time = datetime.now()
                
                # Prepare parameters for command execution
                params = {}
                if command_spec["action"] == "query_memory":
                    params["user_id"] = client_id
                    params["topic"] = command_spec.get("topic", "")
                elif command_spec["action"] == "search_files":
                    params["keyword"] = command_spec.get("keyword", "*.txt")
                    if "path" in command_spec:
                        params["search_path"] = command_spec["path"]
                else:
                    # For file operations (list_directory, read_file)
                    params["path"] = command_spec.get("path", "C:\\VALIS")
                
                # Add client and persona context for ToolManager logging
                params["client_id"] = client_id
                params["persona_id"] = persona_id
                
                # Execute the command
                result = self.execute_desktop_command(
                    command_spec["action"],
                    **params
                )
                
                # ToolManager handles logging, so we just use the execution metadata it provides
                
                if result["success"]:
                    return {
                        "success": True,
                        "response": f"Command executed successfully:\n\n{result['result']}",
                        "provider": "mcp_execution",
                        "metadata": {
                            "execution_id": result.get("execution_id", execution_id),
                            "execution_time": result.get("execution_time", 0),
                            "intent": command_spec["intent"],
                            "action": command_spec["action"],
                            "tool_name": result.get("tool_name")
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Command execution failed: {result['error']}",
                        "provider": "mcp_execution"
                    }
            else:
                # No execution intent detected - pass to next provider
                return {
                    "success": False,
                    "error": "No execution intent detected",
                    "provider": "mcp_execution"
                }
                
        except Exception as e:
            logger.error(f"MCPExecutionProvider error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "mcp_execution"
            }
