#!/usr/bin/env python3
"""
VALIS Tool RPC Server - Sprint 8 Phase 2
Remote interface for tools via JSON-RPC and REST API
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import sys
import os
from pathlib import Path
from flask import Flask, request, jsonify, abort
from functools import wraps

from core.tool_manager import tool_manager

logger = logging.getLogger("ToolRPC")

class ToolRPCServer:
    """
    Remote tool interface for VALIS
    Supports both JSON-RPC and REST API access to tools
    """
    
    def __init__(self, app: Flask = None):
        self.app = app or Flask(__name__)
        self.auth_tokens = {
            "valis_tool_access_2025": {
                "name": "VALIS Tool Access",
                "permissions": ["all_tools"],
                "rate_limit": 100  # requests per minute
            }
        }
        self.setup_routes()
        logger.info("ToolRPCServer initialized")
    
    def require_auth(self, f):
        """Decorator to require authentication for tool access"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check for Authorization header
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Remove 'Bearer ' prefix
            else:
                # Check for API key in headers
                token = request.headers.get('X-API-Key')
            
            if not token or token not in self.auth_tokens:
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Valid API key required for tool access"
                }), 401
            
            # Add auth context to request
            request.auth_context = {
                "token": token,
                "permissions": self.auth_tokens[token]["permissions"],
                "name": self.auth_tokens[token]["name"]
            }
            
            return f(*args, **kwargs)
        return decorated_function
    
    def setup_routes(self):
        """Setup all RPC and REST routes"""
        
        @self.app.route('/v1/tools', methods=['POST'])
        @self.require_auth
        def json_rpc_endpoint():
            """JSON-RPC 2.0 endpoint for tool execution"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": "Parse error"},
                        "id": None
                    }), 400
                
                # Validate JSON-RPC format
                if data.get("jsonrpc") != "2.0":
                    return jsonify({
                        "jsonrpc": "2.0", 
                        "error": {"code": -32600, "message": "Invalid Request"},
                        "id": data.get("id")
                    }), 400
                
                method = data.get("method")
                params = data.get("params", {})
                request_id = data.get("id")
                
                if not method:
                    return jsonify({
                        "jsonrpc": "2.0",
                        "error": {"code": -32602, "message": "Invalid params"},
                        "id": request_id
                    }), 400
                
                # Execute tool via ToolManager
                result = tool_manager.execute_tool(
                    tool_name=method,
                    parameters=params,
                    request_id=str(request_id),
                    auth_context=request.auth_context
                )
                
                if result["success"]:
                    return jsonify({
                        "jsonrpc": "2.0",
                        "result": result,
                        "id": request_id
                    })
                else:
                    return jsonify({
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": result["error"]
                        },
                        "id": request_id
                    }), 500
                
            except Exception as e:
                logger.error(f"JSON-RPC error: {e}")
                return jsonify({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603, 
                        "message": "Internal error",
                        "data": str(e)
                    },
                    "id": data.get("id") if 'data' in locals() else None
                }), 500
        
        @self.app.route('/v1/tools/<tool_name>', methods=['POST'])
        @self.require_auth
        def rest_tool_endpoint(tool_name):
            """REST endpoint for individual tool execution"""
            try:
                data = request.get_json() or {}
                
                # Execute tool via ToolManager
                result = tool_manager.execute_tool(
                    tool_name=tool_name,
                    parameters=data,
                    auth_context=request.auth_context
                )
                
                if result["success"]:
                    return jsonify(result)
                else:
                    return jsonify(result), 400
                    
            except Exception as e:
                logger.error(f"REST tool error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/v1/tools', methods=['GET'])
        @self.require_auth 
        def list_tools():
            """List available tools and their schemas"""
            try:
                info = tool_manager.get_tool_info()
                return jsonify(info)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/v1/tools/<tool_name>', methods=['GET'])
        @self.require_auth
        def get_tool_info(tool_name):
            """Get information about a specific tool"""
            try:
                info = tool_manager.get_tool_info(tool_name)
                if "error" in info:
                    return jsonify(info), 404
                return jsonify(info)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/v1/health', methods=['GET'])
        def health_check():
            """Health check endpoint (no auth required)"""
            try:
                health = tool_manager.health_check()
                status_code = 200 if health["status"] == "healthy" else 503
                return jsonify(health), status_code
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": str(e)
                }), 500
        
        @self.app.route('/v1/openai/functions', methods=['GET'])
        @self.require_auth
        def openai_function_schemas():
            """Get OpenAI-compatible function schemas"""
            try:
                schemas = tool_manager.get_tool_schemas()
                return jsonify({
                    "functions": schemas,
                    "total": len(schemas)
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500


# Create RPC server instance
rpc_server = ToolRPCServer()

# Function to start the server
def start_rpc_server(host="127.0.0.1", port=3002, debug=False):
    """Start the RPC server"""
    logger.info(f"Starting Tool RPC Server on {host}:{port}")
    rpc_server.app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    start_rpc_server(debug=True)
