#!/usr/bin/env python3
"""
VALIS Backend - Fixed routing
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add VALIS root to path
sys.path.append(str(Path(__file__).parent))

try:
    from core.valis_engine import VALISEngine
    from core.valis_memory import MemoryRouter
    from core.persona_router import PersonaRouter
    from core.prompt_composer import PromptComposer
    VALIS_AVAILABLE = True
except ImportError as e:
    logging.error(f"VALIS components not available: {e}")
    VALIS_AVAILABLE = False

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VALISBackend")

# Global components
valis_engine = None
memory_router = None
persona_router = None
prompt_composer = None

def init_valis_components():
    """Initialize VALIS components"""
    global valis_engine, memory_router, persona_router, prompt_composer
    
    if not VALIS_AVAILABLE:
        return False
    
    try:
        logger.info("Initializing VALIS components...")
        
        # Initialize components
        valis_engine = VALISEngine()
        memory_router = MemoryRouter()
        persona_router = PersonaRouter()
        prompt_composer = PromptComposer()
        
        logger.info("All VALIS components initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize VALIS components: {e}")
        return False

# API Routes
@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_info": {
            "valis_available": VALIS_AVAILABLE,
            "engine_loaded": valis_engine is not None,
            "memory_loaded": memory_router is not None,
            "routing_loaded": persona_router is not None
        },
        "personas_loaded": len(valis_engine.persona_manager.personas) if valis_engine else 0,
        "providers_available": ["MCP", "Anthropic", "OpenAI", "Fallback"],
        "active_sessions": 0,
        "message_history_stats": {
            "total_messages": 0,
            "unique_sessions": 0,
            "max_total": 10000,
            "max_per_session": 0,
            "cleanup_hours": 24
        }
    })

@app.route('/api/personas')
def get_personas():
    """Get available personas"""
    if not valis_engine:
        return jsonify({"error": "VALIS engine not available"}), 503
    
    personas = []
    for persona_id, persona_data in valis_engine.persona_manager.personas.items():
        personas.append({
            "id": persona_id,
            "name": persona_data.get("name", persona_id.title()),
            "description": persona_data.get("description", f"AI Assistant persona: {persona_id}"),
            "role": persona_data.get("role", "AI Assistant"),
            "available": True
        })
    
    return jsonify(personas)

@app.route('/api/memory/<persona_id>')
def get_memory(persona_id):
    """Get memory for persona"""
    client_id = request.args.get('client_id', 'default_client')
    
    if not memory_router:
        return jsonify({"error": "Memory system not available"}), 503
    
    try:
        memory_data = memory_router.get_memory_for_persona(persona_id, client_id)
        return jsonify({
            "persona_id": persona_id,
            "client_id": client_id,
            "layers": memory_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        logger.error(f"Memory retrieval error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        persona = data.get('persona', 'jane')
        message = data.get('message')
        client_id = data.get('client_id', 'default_client')
        
        if not message:
            return jsonify({"error": "Message required"}), 400
        
        if not valis_engine:
            return jsonify({"error": "VALIS engine not available"}), 503
        
        # Process message through VALIS
        response = valis_engine.process_message(
            message=message,
            persona_id=persona,
            client_id=client_id
        )
        
        return jsonify({
            "response": response,
            "persona": persona,
            "client_id": client_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500

# Frontend Routes - MOVED BEFORE main execution
@app.route('/')
def index():
    """Serve the main React app"""
    frontend_dir = Path(__file__).parent / "frontend" / "dist"
    if frontend_dir.exists() and (frontend_dir / "index.html").exists():
        return send_from_directory(frontend_dir, 'index.html')
    else:
        return jsonify({
            "error": "Frontend not built",
            "message": "Run 'npm run build' in the frontend directory first",
            "available_endpoints": ["/api/health", "/api/personas", "/api/memory/<persona>", "/api/chat"]
        }), 404

@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend static files"""
    # Explicitly reject API routes
    if path.startswith('api/'):
        return jsonify({"error": f"API endpoint /{path} not found"}), 404
        
    frontend_dir = Path(__file__).parent / "frontend" / "dist"
    
    if frontend_dir.exists():
        file_path = frontend_dir / path
        if file_path.exists() and file_path.is_file():
            return send_from_directory(frontend_dir, path)
    
    # If file not found, serve index.html for client-side routing
    if frontend_dir.exists() and (frontend_dir / 'index.html').exists():
        return send_from_directory(frontend_dir, 'index.html')
    else:
        return jsonify({"error": "Frontend files not found"}), 404

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="VALIS Backend")
    parser.add_argument('--port', type=int, default=3001, help='Port to run on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    
    args = parser.parse_args()
    
    # Initialize VALIS components
    components_initialized = init_valis_components()
    
    if components_initialized:
        logger.info("VALIS Backend starting with full functionality")
        print(f"VALIS Backend starting on http://{args.host}:{args.port}")
        print("React frontend served at root URL")
        print("API endpoints at /api/*")
    else:
        logger.warning("VALIS components failed - running in fallback mode")
        print("VALIS Backend starting in fallback mode")
    
    try:
        app.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        print(f"Failed to start: {e}")
