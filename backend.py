#!/usr/bin/env python3
"""
VALIS Professional Backend API
Serves the existing React/TypeScript frontend with proper API endpoints
Integrates with Sprint 6 memory system and Sprint 7 prompt composition
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
CORS(app)  # Enable CORS for frontend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VALISBackend")

# Global components
valis_engine = None
memory_router = None
persona_router = None
prompt_composer = None
inference_pipeline = None

# Session and message storage (in-memory for now, will be moved to Redis/Postgres in Sprint 9)
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

# API Routes

@app.route('/api/health')
def health():
    """Get system health status"""
    try:
        # Get available personas
        available_personas = 0
        if persona_router:
            available_personas = len(persona_router.get_available_personas())
        
        # Count active sessions (sessions with activity in last hour)
        now = datetime.now(timezone.utc)
        active_sessions = 0
        for session in sessions_db.values():
            last_activity = datetime.fromisoformat(session["last_activity"].replace('Z', '+00:00'))
            if (now - last_activity).total_seconds() < 3600:  # 1 hour
                active_sessions += 1
        
        # Get total message count
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

@app.route('/api/admin/stats')
def admin_stats():
    """Get system statistics"""
    try:
        total_messages = sum(len(messages) for messages in messages_db.values())
        total_requests = sum(session["request_count"] for session in sessions_db.values())
        
        # Calculate uptime (simplified - from first session)
        uptime_seconds = 0
        if sessions_db:
            first_session = min(sessions_db.values(), key=lambda s: s["created_at"])
            created_at = datetime.fromisoformat(first_session["created_at"].replace('Z', '+00:00'))
            uptime_seconds = int((datetime.now(timezone.utc) - created_at).total_seconds())
        
        return jsonify({
            "message_history": {
                "total_messages": total_messages,
                "unique_sessions": len(sessions_db),
                "max_per_session": max([len(messages) for messages in messages_db.values()], default=0),
                "cleanup_hours": 24,
                "max_total": 10000
            },
            "active_sessions": len(sessions_db),
            "total_requests": total_requests,
            "uptime_seconds": uptime_seconds
        })
        
    except Exception as e:
        logger.error(f"Admin stats error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/personas')
def get_personas():
    """Get available personas"""
    try:
        personas = []
        
        if persona_router:
            available_personas = persona_router.get_available_personas()
            
            for persona_id in available_personas:
                # Load persona details
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
            # Fallback personas if router not available
            fallback_personas = ["jane", "laika", "doc_brown", "biff"]
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

@app.route('/api/sessions')
def get_sessions():
    """Get all sessions"""
    try:
        sessions = list(sessions_db.values())
        return jsonify(sessions)
        
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/<session_id>/history')
def get_session_history(session_id: str):
    """Get message history for a session"""
    try:
        messages = messages_db.get(session_id, [])
        
        return jsonify({
            "session_id": session_id,
            "messages": messages,
            "total_count": len(messages)
        })
        
    except Exception as e:
        logger.error(f"Get session history error: {e}")
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
        
        # Get or create session
        session = get_session_info(session_id)
        
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())
        
        logger.info(f"=== MEMORY-AWARE CHAT REQUEST ===")
        logger.info(f"Session: {session_id}")
        logger.info(f"Persona: {persona_id}")
        logger.info(f"Message: {message}")
        logger.info(f"Request ID: {request_id}")
        
        # Use memory-aware inference pipeline if available
        if inference_pipeline:
            try:
                logger.info(f"Using memory-aware inference pipeline")
                
                # Generate client ID from session
                client_id = f"session_{session_id}"
                
                logger.info(f"Calling pipeline with persona={persona_id}, client={client_id}")
                
                # Get session history for context
                session_history = messages_db.get(session_id, [])
                formatted_history = [{"role": msg.get("persona_id", "assistant"), "content": msg.get("response", "")} 
                                   for msg in session_history[-5:]]  # Last 5 messages
                
                # Add current message context
                enhanced_context = context or {}
                enhanced_context.update({
                    "session_history": formatted_history,
                    "client_id": client_id
                })
                
                # Use memory-aware pipeline
                pipeline_result = inference_pipeline.run_memory_aware_chat(
                    persona_id=persona_id,
                    client_id=client_id,
                    user_message=message,
                    session_id=session_id
                )
                
                logger.info(f"Pipeline completed successfully")
                
                response_text = pipeline_result["response"]
                provider_used = pipeline_result["provider"]
                processing_time = pipeline_result["processing_time"]
                memory_used = pipeline_result["memory_used"]
                tags_processed = pipeline_result["tags_processed"]
                
                # Log memory usage
                logger.info(f"=== MEMORY LAYERS USED ===")
                logger.info(f"Core Biography: {len(memory_used.get('core_biography', []))} entries")
                logger.info(f"Canonized Identity: {len(memory_used.get('canonized_identity', []))} entries")
                logger.info(f"Client Profile: {len(memory_used.get('client_profile', {}).get('facts', {}))} facts")
                logger.info(f"Working Memory: {len(memory_used.get('working_memory', []))} entries")
                logger.info(f"Session History: {len(memory_used.get('session_history', []))} messages")
                
                # Log tag processing
                if tags_processed:
                    logger.info(f"=== MEMORY TAGS PROCESSED ===")
                    logger.info(f"Tags: {tags_processed}")
                else:
                    logger.info(f"=== NO MEMORY TAGS DETECTED ===")
                
                # Add to message history
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
                import traceback
                traceback.print_exc()
                # Fall back to basic response
                response_text = f"I apologize, but I encountered an error with the memory system. Error: {str(e)}"
                provider_used = "Error"
                processing_time = 0.0
                memory_used = {}
                tags_processed = []
        
        # Fallback if no pipeline available
        else:
            logger.error("Memory-aware pipeline not available!")
            logger.error(f"inference_pipeline = {inference_pipeline}")
            response_text = f"Hello! I'm {persona_id}. The memory-aware system is not available, so this is a basic fallback response."
            provider_used = "Fallback"
            processing_time = 0.1
            memory_used = {}
            tags_processed = []
        
        # Add fallback response to history
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
                "layers_used": getattr(locals(), 'memory_used', {}),
                "tags_processed": getattr(locals(), 'tags_processed', [])
            }
        })
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "session_id": data.get('session_id', ''),
            "persona_id": data.get('persona_id', ''),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "session_id": data.get('session_id', ''),
            "persona_id": data.get('persona_id', ''),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500

@app.route('/api/config')
def get_config():
    """Get system configuration"""
    try:
        config = {
            "valis_engine_enabled": valis_engine is not None,
            "memory_system_enabled": memory_router is not None,
            "persona_routing_enabled": persona_router is not None,
            "session_management": "in-memory",
            "max_session_history": 1000,
            "cleanup_interval_hours": 24
        }
        
        return jsonify(config)
        
    except Exception as e:
        logger.error(f"Get config error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update system configuration (placeholder for now)"""
    try:
        data = request.get_json()
        # For now, just acknowledge the request
        # In Sprint 9, this will update actual configuration
        
        return jsonify({
            "status": "success",
            "message": "Configuration update acknowledged (Sprint 9 will implement full config management)"
        })
        
    except Exception as e:
        logger.error(f"Update config error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/memory/<persona_id>')
def get_memory_data(persona_id: str):
    """Get memory data for persona diagnostics"""
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

@app.route('/api/memory/canon', methods=['POST'])
def add_canon_memory():
    """Add canonical memory entry"""
    try:
        data = request.get_json()
        persona_id = data.get('persona_id')
        content = data.get('content')
        
        if not persona_id or not content:
            return jsonify({"error": "persona_id and content required"}), 400
        
        if memory_router:
            success = memory_router.canonize_response(
                persona_id=persona_id,
                response_text=content,
                source_prompt="Manual entry via UI"
            )
            return jsonify({"success": success})
        else:
            return jsonify({"error": "Memory system not available"}), 503
            
    except Exception as e:
        logger.error(f"Add canon memory error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory/client-fact', methods=['POST']) 
def add_client_fact():
    """Add client fact to memory"""
    try:
        data = request.get_json()
        persona_id = data.get('persona_id')
        client_id = data.get('client_id')
        key = data.get('key')
        value = data.get('value')
        
        if not all([persona_id, client_id, key, value]):
            return jsonify({"error": "persona_id, client_id, key, and value required"}), 400
        
        if memory_router:
            success = memory_router.add_client_fact(
                persona_id=persona_id,
                client_id=client_id,
                key=key,
                value=value
            )
            return jsonify({"success": success})
        else:
            return jsonify({"error": "Memory system not available"}), 503
            
    except Exception as e:
        logger.error(f"Add client fact error: {e}")
        return jsonify({"error": str(e)}), 500

# Serve the React frontend
@app.route('/')
def index():
    """Serve the main React app"""
    frontend_dir = Path(__file__).parent / "frontend" / "dist"
    if frontend_dir.exists():
        return send_from_directory(frontend_dir, 'index.html')
    else:
        return jsonify({
            "error": "Frontend not built",
            "message": "Run 'npm run build' in the frontend directory first"
        }), 404

@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend static files"""
    frontend_dir = Path(__file__).parent / "frontend" / "dist"
    if frontend_dir.exists():
        file_path = frontend_dir / path
        if file_path.exists():
            return send_from_directory(frontend_dir, path)
    
    # If file not found, serve index.html for client-side routing
    if (frontend_dir / 'index.html').exists():
        return send_from_directory(frontend_dir, 'index.html')
    
    return jsonify({"error": "File not found"}), 404

# Initialize and run
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="VALIS Professional Backend")
    parser.add_argument('--port', type=int, default=3001, help='Port to run on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    
    args = parser.parse_args()
    
    # Initialize VALIS components
    components_initialized = init_valis_components()
    
    if components_initialized:
        logger.info("VALIS Professional Backend starting with full functionality")
        print(f"VALIS Backend starting on http://{args.host}:{args.port}")
        print("Professional React frontend will be served at the root URL")
        print("API endpoints available at /api/*")
    else:
        logger.warning("VALIS components failed to initialize - running in fallback mode")
        print("VALIS Backend starting in fallback mode")
        print("Limited functionality - check component availability")
    
    try:
        app.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\nVALIS Backend shutting down...")
    except Exception as e:
        logger.error(f"Backend startup failed: {e}")
        print(f"Failed to start backend: {e}")
