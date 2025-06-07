#!/usr/bin/env python3
"""
VALIS ToolManager - Sprint 8 Implementation
Centralized tool access layer for all providers (local + remote)
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import sys
from pathlib import Path

from memory.db import db
from tools.valis_tools import valis_tools

logger = logging.getLogger("ToolManager")

class ToolManager:
    """
    Centralized tool manager for VALIS
    Provides unified interface for all tool operations across local and remote providers
    """
    
    def __init__(self):
        # Security and constraint configuration
        self.config = {
            "max_file_size_bytes": 1024 * 1024,  # 1MB
            "max_file_lines": 100,
            "max_search_results": 10,
            "max_directory_entries": 100,
            "max_tokens_output": 1500,
            "allowed_directories": [
                "C:\\VALIS",
                "C:\\VALIS\\valis2", 
                "C:\\VALIS\\logs",
                "C:\\VALIS\\data"
            ],
            "rate_limit_per_minute": 60,  # Future rate limiting
            "require_auth": True  # For remote access
        }
        
        # Tool registry - all available tools
        self.tools = {
            "query_memory": {
                "handler": self._query_memory,
                "description": "Search memory spine for relevant information about a topic",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "Client UUID for scoped search"},
                        "topic": {"type": "string", "description": "Search term or keyword"}
                    },
                    "required": ["user_id", "topic"]
                }
            },
            "read_file": {
                "handler": self._read_file,
                "description": "Read file contents with security constraints",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to read"}
                    },
                    "required": ["path"]
                }
            },
            "search_files": {
                "handler": self._search_files, 
                "description": "Search for files by name or content within allowed directories",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string", "description": "Search term or filename pattern"},
                        "search_path": {"type": "string", "description": "Optional specific path to search"}
                    },
                    "required": ["keyword"]
                }
            },
            "list_directory": {
                "handler": self._list_directory,
                "description": "List directory contents with security constraints", 
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path to list"}
                    },
                    "required": ["path"]
                }
            }
        }
        
        logger.info(f"ToolManager initialized with {len(self.tools)} tools")
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get OpenAI-compatible function schemas for all tools"""
        schemas = []
        for tool_name, tool_config in self.tools.items():
            schema = {
                "name": tool_name,
                "description": tool_config["description"],
                "parameters": tool_config["parameters"]
            }
            schemas.append(schema)
        return schemas
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any], 
                    client_id: str = None, persona_id: str = None,
                    request_id: str = None, auth_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a tool with full logging and security
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            client_id: Client UUID for logging
            persona_id: Persona UUID for logging  
            request_id: Request tracking ID
            auth_context: Authentication/authorization context
            
        Returns:
            Tool execution result with metadata
        """
        execution_id = request_id or str(uuid.uuid4())[:8]
        start_time = datetime.now()
        
        try:
            logger.info(f"Executing tool: {tool_name} with params: {parameters}")
            
            # Validate tool exists
            if tool_name not in self.tools:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                    "execution_id": execution_id
                }
            
            # Validate parameters
            validation_result = self._validate_parameters(tool_name, parameters)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Invalid parameters: {validation_result['error']}",
                    "execution_id": execution_id
                }
            
            # Execute tool
            tool_handler = self.tools[tool_name]["handler"]
            result = tool_handler(**parameters)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log execution
            self._log_execution(
                execution_id, client_id, persona_id, tool_name,
                parameters, result, execution_time, result.get("success", False)
            )
            
            # Add metadata
            result["execution_id"] = execution_id
            result["execution_time"] = execution_time
            result["tool_name"] = tool_name
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_result = {
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
                "execution_id": execution_id,
                "execution_time": execution_time
            }
            
            # Log failed execution
            self._log_execution(
                execution_id, client_id, persona_id, tool_name,
                parameters, error_result, execution_time, False
            )
            
            logger.error(f"Tool execution failed: {e}")
            return error_result
    
    def _validate_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool parameters against schema"""
        try:
            tool_schema = self.tools[tool_name]["parameters"]
            required_params = tool_schema.get("required", [])
            properties = tool_schema.get("properties", {})
            
            # Check required parameters
            for param in required_params:
                if param not in parameters:
                    return {
                        "valid": False,
                        "error": f"Missing required parameter: {param}"
                    }
            
            # Check parameter types
            for param_name, param_value in parameters.items():
                if param_name in properties:
                    expected_type = properties[param_name].get("type")
                    if expected_type == "string" and not isinstance(param_value, str):
                        return {
                            "valid": False,
                            "error": f"Parameter {param_name} must be string"
                        }
            
            return {"valid": True}
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Parameter validation error: {str(e)}"
            }
    
    def _query_memory(self, user_id: str, topic: str) -> Dict[str, Any]:
        """Execute memory query tool"""
        return valis_tools.query_memory(user_id, topic)
    
    def _read_file(self, path: str) -> Dict[str, Any]:
        """Execute file read tool"""
        return valis_tools.read_file(path)
    
    def _search_files(self, keyword: str, search_path: str = None) -> Dict[str, Any]:
        """Execute file search tool"""
        return valis_tools.search_files(keyword, search_path)
    
    def _list_directory(self, path: str) -> Dict[str, Any]:
        """Execute directory listing tool"""
        return valis_tools.list_directory(path)
    
    def _log_execution(self, execution_id: str, client_id: str, persona_id: str,
                      tool_name: str, parameters: Dict[str, Any], result: Dict[str, Any],
                      execution_time: float, success: bool):
        """Log tool execution to database"""
        try:
            db.execute("""
                INSERT INTO execution_logs 
                (execution_id, client_id, persona_id, intent, function_name, 
                 parameters, success, result_preview, execution_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                execution_id,
                client_id,
                persona_id, 
                f"tool_{tool_name}",
                tool_name,
                json.dumps(parameters),
                success,
                str(result)[:200] + "..." if len(str(result)) > 200 else str(result),
                execution_time
            ))
            
            logger.info(f"Logged tool execution {execution_id}: {tool_name} ({execution_time:.3f}s)")
            
        except Exception as e:
            logger.error(f"Failed to log tool execution: {e}")
    
    def get_tool_info(self, tool_name: str = None) -> Dict[str, Any]:
        """Get information about available tools"""
        if tool_name:
            if tool_name in self.tools:
                return {
                    "tool": tool_name,
                    "description": self.tools[tool_name]["description"],
                    "parameters": self.tools[tool_name]["parameters"]
                }
            else:
                return {"error": f"Tool {tool_name} not found"}
        else:
            return {
                "available_tools": list(self.tools.keys()),
                "total_tools": len(self.tools),
                "tool_schemas": self.get_tool_schemas()
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for tool manager"""
        try:
            # Test database connection
            db.query("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # Test ValisToolSuite
        try:
            test_result = valis_tools.list_directory("C:\\VALIS")
            tools_status = "healthy" if test_result.get("success") else "degraded"
        except Exception as e:
            tools_status = f"error: {str(e)}"
        
        return {
            "status": "healthy" if db_status == "healthy" and tools_status == "healthy" else "degraded",
            "components": {
                "database": db_status,
                "tools": tools_status
            },
            "available_tools": len(self.tools),
            "config": {
                "max_file_size_mb": self.config["max_file_size_bytes"] // (1024 * 1024),
                "max_tokens": self.config["max_tokens_output"],
                "allowed_dirs": len(self.config["allowed_directories"])
            }
        }


# Global instance for use across VALIS
tool_manager = ToolManager()
