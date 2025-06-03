#!/usr/bin/env python3
"""
MCP Backend - External Memory Version
Integrates MCP memory bridge with frontend
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
import json
from pathlib import Path
from datetime import datetime
from core.mcp_valis_engine import create_mcp_valis_engine

app = Flask(__name__)
CORS(app)

logger = logging.getLogger(__name__)

# Global MCP engine
mcp_engine = None

def init_mcp_components():
    """Initialize MCP VALIS components"""
    global mcp_engine
    try:
        mcp_engine = create_mcp_valis_engine()
        logger.info("MCP VALIS Engine initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize MCP components: {e}")
        return False

# API Routes
@app.route('/api/health')
def health_check():
    """Health check with MCP status"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mcp_engine": mcp_engine is not None,
        "external_memory": True
    })

@app.route('/api/personas')
def get_personas():
    """Get available personas"""
    personas_dir = Path(__file__).parent / "personas"
    personas = []
    
    for persona_dir in personas_dir.iterdir():
        if persona_dir.is_dir():
            persona_id = persona_dir.name
            personas.append({
                "id": persona_id,
                "name": persona_id.title(),
                "available": True,
                "memory_source": f"C:\\VALIS\\memory\\personas\\{persona_id}\\memories.json"
            })
    
    return jsonify(personas)

@app.route('/api/memory/status/<persona_id>')
def get_memory_status(persona_id):
    """Get memory system diagnostic status"""
    if not mcp_engine:
        return jsonify({"error": "MCP engine not available"}), 503
    
    status = mcp_engine.get_memory_status(persona_id)
    return jsonify(status)

@app.route('/api/persona/initialize/<persona_id>')
def initialize_persona(persona_id):
    """Initialize persona with external memory"""
    if not mcp_engine:
        return jsonify({"error": "MCP engine not available"}), 503
    
    result = mcp_engine.initialize_persona(persona_id)
    return jsonify(result)

@app.route('/api/sessions')
def get_sessions():
    """Get active sessions"""
    return jsonify([])

@app.route('/api/sessions/<session_id>/history')
def get_session_history(session_id):
    """Get session history"""
    return jsonify([])

@app.route('/api/memory/<persona_id>')
def get_memory_data(persona_id):
    """Get memory data with session parameter"""
    session_id = request.args.get('session')
    
    if not mcp_engine:
        return jsonify({"error": "MCP engine not available"}), 503
    
    # Get memory status from MCP system
    status = mcp_engine.get_memory_status(persona_id)
    
    # Also try to read persona biography 
    persona_file = Path(__file__).parent / "personas" / persona_id / f"{persona_id}.json"
    biography = {}
    if persona_file.exists():
        try:
            with open(persona_file, 'r') as f:
                biography = json.load(f)
        except:
            pass
    
    return jsonify({
        "persona_id": persona_id,
        "session_id": session_id,
        "memory_loaded": status.get("memory_accessible", False),
        "external_source": True,
        "biography": biography,
        "memory_stats": status.get("memory_stats", {}),
        "layers": [
            {"name": "Core Biography", "count": 1 if biography else 0},
            {"name": "Canonized Identity", "count": status.get("memory_stats", {}).get("total_memories", 0)},
            {"name": "Client Profile", "count": 0},
            {"name": "Working Memory", "count": 0},
            {"name": "Session History", "count": 0}
        ]
    })

@app.route('/api/dev/command', methods=['POST'])
def dev_command():
    """Handle dev introspection commands"""
    if not mcp_engine:
        return jsonify({"error": "MCP engine not available"}), 503
    
    data = request.get_json()
    command = data.get('command')
    persona_id = data.get('persona_id', 'jane')
    
    result = mcp_engine.handle_dev_command(command, persona_id)
    
    return jsonify({
        "command": command,
        "persona_id": persona_id,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat with minimal prompts"""
    if not mcp_engine:
        return jsonify({"error": "MCP engine not available"}), 503
    
    data = request.get_json()
    persona_id = data.get('persona', 'jane')
    message = data.get('message')
    client_id = data.get('client_id', 'default')
    session_id = data.get('session_id')
    
    if not message:
        return jsonify({"error": "Message required"}), 400
    
    # Process with minimal prompt
    prompt = mcp_engine.process_message(
        persona_id=persona_id,
        message=message,
        client_id=client_id,
        session_id=session_id
    )
    
    return jsonify({
        "response": f"[MCP Mode] Processed with minimal prompt: {len(prompt)} chars",
        "persona": persona_id,
        "external_memory": True,
        "prompt_length": len(prompt),
        "timestamp": datetime.now().isoformat()
    })

# Frontend routes
@app.route('/')
def index():
    """Serve React frontend"""
    frontend_dir = Path(__file__).parent / "frontend" / "dist"
    if frontend_dir.exists() and (frontend_dir / "index.html").exists():
        return send_from_directory(frontend_dir, 'index.html')
    else:
        return jsonify({
            "error": "Frontend not built",
            "mcp_mode": True,
            "available_endpoints": [
                "/api/health", "/api/personas", "/api/memory/status/<persona>",
                "/api/persona/initialize/<persona>", "/api/dev/command", "/api/chat"
            ]
        }), 404

@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend static files"""
    if path.startswith('api/'):
        return jsonify({"error": f"API endpoint /{path} not found"}), 404
    
    frontend_dir = Path(__file__).parent / "frontend" / "dist"
    if frontend_dir.exists():
        file_path = frontend_dir / path
        if file_path.exists() and file_path.is_file():
            return send_from_directory(frontend_dir, path)
    
    if frontend_dir.exists() and (frontend_dir / 'index.html').exists():
        return send_from_directory(frontend_dir, 'index.html')
    else:
        return jsonify({"error": "Frontend files not found"}), 404

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP VALIS Backend")
    parser.add_argument('--port', type=int, default=3001)
    parser.add_argument('--debug', action='store_true')
    
    args = parser.parse_args()
    
    # Initialize MCP components
    if init_mcp_components():
        print("MCP VALIS Backend starting with external memory")
        print(f"Running on http://127.0.0.1:{args.port}")
        print("External memory via Desktop Commander MCP")
    else:
        print("MCP initialization failed - limited functionality")
    
    app.run(host='127.0.0.1', port=args.port, debug=args.debug)
