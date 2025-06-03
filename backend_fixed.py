#!/usr/bin/env python3
"""
VALIS Professional Backend API - 03's Route Fix Applied
All /api/* routes FIRST, catch-all LAST
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add VALIS root to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from core.valis_engine import VALISEngine
    from core.valis_memory import MemoryRouter
    from core.persona_router import PersonaRouter
    from core.prompt_composer import PromptComposer
    from valis_inference_pipeline import VALISInferencePipeline
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
inference_pipeline = None

# Session storage
sessions_db = {}
messages_db = {}

def init_valis_components():
    """Initialize VALIS components"""
    global valis_engine, memory_router, persona_router, prompt_composer, inference_pipeline
    
    if not VALIS_AVAILABLE:
        logger.error("VALIS components not available")
        return False
    
    try:
        logger.info("Initializing VALIS components...")
        
        valis_engine = VALISEngine()
        logger.info("✓ VALISEngine initialized")
        
        memory_router = MemoryRouter()
        logger.info("✓ MemoryRouter initialized")
        
        persona_router = PersonaRouter()
        logger.info("✓ PersonaRouter initialized")
        
        prompt_composer = PromptComposer()
        logger.info("✓ PromptComposer initialized")
        
        logger.info("Initializing VALISInferencePipeline...")
        inference_pipeline = VALISInferencePipeline()
        logger.info("✓ VALISInferencePipeline initialized")
        
        logger.info("VALIS components initialized successfully")
        logger.info("Memory-aware inference pipeline ready")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize VALIS components: {e}")
        return False

def get_session_info(session_id: str) -> Dict[str, Any]:
    """Get or create session info"""
    if session_id not in sessions_db:
        sessions_db[session_id] = {
            "session_id": session_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "request_count": 0,
            "last_persona": None,
            "message_count": 0
        }
    return sessions_db[session_id]

def add_message(session_id: str, persona_id: str, message: str, response: str, provider: str):
    """Add message to history"""
    if session_id not in messages_db:
        messages_db[session_id] = []
    
    message_entry = {
        "session_id": session_id,
        "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
        "persona_id": persona_id,
        "message": message,
        "response": response,
        "provider_used": provider
    }
    
    messages_db[session_id].append(message_entry)
    
    # Update session info
    session = get_session_info(session_id)
    session["last_activity"] = datetime.now(timezone.utc).isoformat()
    session["last_persona"] = persona_id
    session["message_count"] = len(messages_db[session_id])
    session["request_count"] += 1

# ───────────────────────────────────────────────────────────
#  ALL API ROUTES FIRST - 03's Fix
# ───────────────────────────────────────────────────────────

@app.route('/api/health')
def health():
    """Get system health status"""
    try:
        available_personas = 0
        if persona_router:
            available_personas = len(persona_router.get_available_personas())
        
        now = datetime.now(timezone.utc)
        active_sessions = 0
        for session in sessions_db.values():
            last_activity = datetime.fromisoformat(session["last_activity"].replace('Z', '+00:00'))
            if (now - last_activity).total_seconds() < 3600:
                active_sessions += 1
        
        total_messages = sum(len(messages) for messages in messages_db.values())
        
        return jsonify({
            "status": "healthy" if VALIS_AVAILABLE else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_info": {
                "valis_available": VALIS_AVAILABLE,
                "engine_loaded": valis_engine is not None,
                "memory_loaded": memory_router is not None,
                "routing_loaded": persona_router is not None
            },
            "providers_available": ["MCP", "Anthropic", "OpenAI", "Fallback"] if valis_engine else [],
            "personas_loaded": available_personas,
            "active_sessions": active_sessions,
            "message_history_stats": {
                "total_messages": total_messages,
                "unique_sessions": len(sessions_db),
                "max_per_session": max([len(messages) for messages in messages_db.values()], default=0),
                "cleanup_hours": 24,
                "max_total": 10000
            }
        })
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }), 500

@app.route('/api/personas')
def get_personas():
    """Get available personas"""
    try:
        personas = []
        
        if persona_router:
            available_personas = persona_router.get_available_personas()
            
            for persona_id in available_personas:
                try:
                    persona_file = Path(__file__).parent / "personas" / f"{persona_id}.json"
                    if persona_file.exists():
                        with open(persona_file, 'r', encoding='utf-8') as f:
                            persona_data = json.load(f)
                            
                        personas.append({
                            "id": persona_id,
                            "name": persona_data.get("name", persona_id.replace('_', ' ').title()),
                            "role": persona_data.get("role", "AI Assistant"),
                            "description": persona_data.get("description", ""),
                            "available": True
                        })
                except Exception as e:
                    logger.warning(f"Failed to load persona {persona_id}: {e}")
                    personas.append({
                        "id": persona_id,
                        "name": persona_id.replace('_', ' ').title(),
                        "role": "AI Assistant",
                        "description": "Persona details unavailable",
                        "available": False
                    })
        else:
            fallback_personas = ["jane", "laika", "marty"]
            for persona_id in fallback_personas:
                personas.append({
                    "id": persona_id,
                    "name": persona_id.replace('_', ' ').title(),
                    "role": "AI Assistant",
                    "description": "Fallback persona",
                    "available": False
                })
        
        return jsonify(personas)
        
    except Exception as e:
        logger.error(f"Get personas error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory/<persona_id>')
def get_memory_data(persona_id: str):
    """Get memory data for persona diagnostics - CRITICAL API ROUTE"""
    try:
        session_id = request.args.get('session', 'default')
        client_id = f"session_{session_id}"
        
        if memory_router:
            memory_payload = memory_router.get_memory_payload(
                persona_id=persona_id,
                client_id=client_id,
                current_message=""
            )
            return jsonify(memory_payload)
        else:
            return jsonify({
                "error": "Memory system not available"
            }), 503
            
    except Exception as e:
        logger.error(f"Get memory data error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Send message and get response using memory-aware inference pipeline"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        session_id = data.get('session_id')
        persona_id = data.get('persona_id', 'jane')
        message = data.get('message', '')
        context = data.get('context', {})
        
        if not session_id:
            return jsonify({"error": "session_id is required"}), 400
        if not message:
            return jsonify({"error": "message is required"}), 400
        
        session = get_session_info(session_id)
        request_id = str(uuid.uuid4())
        
        logger.info(f"Chat request: {session_id}, {persona_id}")
        
        if inference_pipeline:
            try:
                client_id = f"session_{session_id}"
                
                session_history = messages_db.get(session_id, [])
                formatted_history = [{"role": msg.get("persona_id", "assistant"), "content": msg.get("response", "")} 
                                   for msg in session_history[-5:]]
                
                enhanced_context = context or {}
                enhanced_context.update({
                    "session_history": formatted_history,
                    "client_id": client_id
                })
                
                pipeline_result = inference_pipeline.run_memory_aware_chat(
                    persona_id=persona_id,
                    client_id=client_id,
                    user_message=message,
                    session_id=session_id
                )
                
                response_text = pipeline_result["response"]
                provider_used = pipeline_result["provider"]
                processing_time = pipeline_result["processing_time"]
                memory_used = pipeline_result["memory_used"]
                tags_processed = pipeline_result["tags_processed"]
                
                add_message(session_id, persona_id, message, response_text, provider_used)
                
                return jsonify({
                    "success": True,
                    "response": response_text,
                    "provider": provider_used,
                    "session_id": session_id,
                    "persona_id": persona_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "request_id": request_id,
                    "timing": {
                        "processing_time": processing_time,
                        "provider_time": processing_time
                    },
                    "memory_info": {
                        "layers_used": {
                            "core_biography": len(memory_used.get('core_biography', [])),
                            "canonized_identity": len(memory_used.get('canonized_identity', [])),
                            "client_profile": len(memory_used.get('client_profile', {}).get('facts', {})),
                            "working_memory": len(memory_used.get('working_memory', [])),
                            "session_history": len(memory_used.get('session_history', []))
                        },
                        "tags_processed": tags_processed
                    }
                })
                
            except Exception as e:
                logger.error(f"Memory-aware pipeline error: {e}")
                response_text = f"Error with memory system: {str(e)}"
                provider_used = "Error"
                processing_time = 0.0
        
        else:
            response_text = f"Hello! I'm {persona_id}. The memory-aware system is not available."
            provider_used = "Fallback"
            processing_time = 0.1
        
        add_message(session_id, persona_id, message, response_text, provider_used)
        
        return jsonify({
            "success": True,
            "response": response_text,
            "provider": provider_used,
            "session_id": session_id,
            "persona_id": persona_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "timing": {
                "processing_time": processing_time,
                "provider_time": processing_time
            }
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "session_id": data.get('session_id', ''),
            "persona_id": data.get('persona_id', ''),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500

# ───────────────────────────────────────────────────────────
#  CATCH-ALL FOR SPA - VERY LAST - 03's Fix
# ───────────────────────────────────────────────────────────

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Serve index.html for non-API requests - SPA routing"""
    # 💡 short-circuit if it looks like an API call - 03's fix enhanced
    if path.startswith("api/") or path == "api":
        return jsonify({"error": f"API endpoint /{path} not found"}), 404
        
    frontend_dir = Path(__file__).parent / "frontend" / "dist"
    if frontend_dir.exists():
        return send_from_directory(frontend_dir, 'index.html')
    else:
        return jsonify({
            "error": "Frontend not built"
        }), 404

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="VALIS Backend")
    parser.add_argument('--port', type=int, default=3001, help='Port to run on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    
    args = parser.parse_args()
    
    components_initialized = init_valis_components()
    
    if components_initialized:
        logger.info("VALIS Backend starting with full functionality")
        print(f"VALIS Backend: http://{args.host}:{args.port}")
        print("API endpoints: /api/*")
    else:
        logger.warning("VALIS components failed - running in fallback mode")
    
    try:
        app.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\nVALIS Backend shutting down...")
    except Exception as e:
        logger.error(f"Backend startup failed: {e}")
