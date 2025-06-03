#!/usr/bin/env python3
"""
VALIS Backend with Blueprint Isolation - 03's Final Fix
"""

import logging
import sys
from pathlib import Path
from flask import Flask, send_from_directory, jsonify, abort
from flask_cors import CORS

# Add VALIS root to path
sys.path.append(str(Path(__file__).parent))

# Import Blueprint and context
from api import api
import app_context

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

def init_valis_components():
    """Initialize VALIS components and wire to app_context"""
    if not VALIS_AVAILABLE:
        logger.error("VALIS components not available")
        return False
    
    try:
        logger.info("Initializing VALIS components...")
        
        app_context.valis_engine = VALISEngine()
        app_context.memory_router = MemoryRouter()
        app_context.persona_router = PersonaRouter()
        app_context.prompt_composer = PromptComposer()
        app_context.inference_pipeline = VALISInferencePipeline()
        
        logger.info("VALIS components initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize VALIS components: {e}")
        return False

# ───────────────────────────────────────────────────────────
# Register Blueprint BEFORE catch-all - 03's Fix
# ───────────────────────────────────────────────────────────
app.register_blueprint(api)

# ───────────────────────────────────────────────────────────
# SPA catch-all LAST
# ───────────────────────────────────────────────────────────
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    """Serve SPA index.html for non-API requests"""
    if path.startswith("api"):  # paranoia guard
        abort(404)
        
    frontend_dir = Path(__file__).parent / "frontend" / "dist"
    if frontend_dir.exists():
        return send_from_directory(frontend_dir, "index.html")
    else:
        return jsonify({
            "error": "Frontend not built",
            "message": "Run 'npm run build' in frontend directory"
        }), 404

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="VALIS Backend")
    parser.add_argument('--port', type=int, default=3001, help='Port to run on')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    
    args = parser.parse_args()
    
    components_initialized = init_valis_components()
    
    if components_initialized:
        logger.info("VALIS Backend starting with full functionality")
        print(f"VALIS Backend: http://{args.host}:{args.port}")
        print("API Blueprint: /api/*")
    else:
        logger.warning("Running in fallback mode")
    
    try:
        app.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
