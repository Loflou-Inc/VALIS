# api.py - Blueprint isolation for all backend JSON routes
from flask import Blueprint, jsonify, request, abort
from datetime import datetime, timezone
import uuid
import logging

api = Blueprint("api", __name__, url_prefix="/api")
logger = logging.getLogger("VALIS.API")

# ───────────────────────────────
# Memory diagnostics
# ───────────────────────────────
@api.route("/memory/<string:persona_id>")
def get_memory(persona_id):
    session_id = request.args.get("session", "default")
    client_id = f"session_{session_id}"

    import app_context
    if not app_context.memory_router:
        abort(503, "Memory system unavailable")

    try:
        payload = app_context.memory_router.get_memory_payload(
            persona_id=persona_id,
            client_id=client_id,
            current_message=""
        )
        return jsonify(payload)
    except Exception as e:
        logger.error(f"Memory API error: {e}")
        return jsonify({"error": str(e)}), 500

# ───────────────────────────────
# Health
# ───────────────────────────────
@api.route("/health")
def health():
    import app_context
    
    available_personas = 0
    if app_context.persona_router:
        available_personas = len(app_context.persona_router.get_available_personas())
    
    return jsonify({
        "status": "healthy" if app_context.valis_engine else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_info": {
            "valis_available": app_context.valis_engine is not None,
            "memory_loaded": app_context.memory_router is not None,
            "routing_loaded": app_context.persona_router is not None
        },
        "personas_loaded": available_personas
    })

# ───────────────────────────────
# Personas
# ───────────────────────────────
@api.route("/personas")
def get_personas():
    import app_context
    import json
    from pathlib import Path
    
    personas = []
    
    if app_context.persona_router:
        available_personas = app_context.persona_router.get_available_personas()
        
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
    
    return jsonify(personas)

# ───────────────────────────────
# Chat endpoint
# ───────────────────────────────
@api.route("/chat", methods=["POST"])
def chat():
    import app_context
    
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id") or str(uuid.uuid4())
    persona_id = data.get("persona_id", "jane")
    message = data.get("message", "")
    
    if not message:
        return jsonify({"error": "message is required"}), 400
    
    logger.info(f"Chat request: {session_id}, {persona_id}")
    
    if app_context.inference_pipeline:
        try:
            client_id = f"session_{session_id}"
            
            pipeline_result = app_context.inference_pipeline.run_memory_aware_chat(
                persona_id=persona_id,
                client_id=client_id,
                user_message=message,
                session_id=session_id
            )
            
            return jsonify({
                "success": True,
                "response": pipeline_result["response"],
                "provider": pipeline_result["provider"],
                "session_id": session_id,
                "persona_id": persona_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "memory_info": {
                    "layers_used": {
                        "core_biography": len(pipeline_result["memory_used"].get('core_biography', [])),
                        "canonized_identity": len(pipeline_result["memory_used"].get('canonized_identity', [])),
                        "client_profile": len(pipeline_result["memory_used"].get('client_profile', {}).get('facts', {})),
                        "working_memory": len(pipeline_result["memory_used"].get('working_memory', [])),
                        "session_history": len(pipeline_result["memory_used"].get('session_history', []))
                    },
                    "tags_processed": pipeline_result["tags_processed"]
                }
            })
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "persona_id": persona_id
            }), 500
    else:
        return jsonify({
            "success": True,
            "response": f"Hello! I'm {persona_id}. Memory system not available.",
            "provider": "Fallback",
            "session_id": session_id,
            "persona_id": persona_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
