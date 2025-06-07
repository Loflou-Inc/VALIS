#!/usr/bin/env python3
"""
VALIS 2.0 Cloud-Hardened Server
Flask server with rate limiting, health monitoring, and error tracking
"""

from flask import Flask, request, jsonify, send_from_directory, g
from flask_cors import CORS
import logging
import sys
import os
import uuid
import time
from pathlib import Path
from collections import defaultdict, deque
from datetime import datetime, timedelta
from functools import wraps

from routes.session_routes import session_bp
from routes.admin_routes import admin_bp
from inference import run_inference, initialize
from memory.query_client import memory
from memory.db import db
from core.tool_manager import tool_manager

# Configure logging with request tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] [%(request_id)s] %(message)s'
)
logger = logging.getLogger("VALIS_Server")

app = Flask(__name__)
# Configure CORS to handle localhost/127.0.0.1 cross-origin issues
CORS(app, 
     origins=['http://localhost:3001', 'http://127.0.0.1:3001', 'http://localhost:*'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'X-Admin-Key', 'Authorization'],
     supports_credentials=True)

# Rate limiting storage (in production, use Redis)
rate_limits = defaultdict(lambda: deque())
RATE_LIMIT_REQUESTS = 60  # requests per minute
RATE_LIMIT_WINDOW = 60    # seconds

class CloudHardenedFilter(logging.Filter):
    """Add request ID to log records"""
    def filter(self, record):
        try:
            # Try to get request_id from Flask g, fallback if not in app context
            record.request_id = getattr(g, 'request_id', 'no-request')
        except RuntimeError:
            # Outside of Flask application context
            record.request_id = 'no-context'
        return True

# Add filter to all loggers
for handler in logging.getLogger().handlers:
    handler.addFilter(CloudHardenedFilter())

def add_request_id():
    """Add unique request ID to Flask g object"""
    g.request_id = str(uuid.uuid4())[:8]

def rate_limit(f):
    """Rate limiting decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        now = time.time()
        
        # Clean old entries
        rate_limits[client_ip] = deque([
            timestamp for timestamp in rate_limits[client_ip]
            if now - timestamp < RATE_LIMIT_WINDOW
        ])
        
        # Check rate limit
        if len(rate_limits[client_ip]) >= RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded',
                'retry_after': 60
            }), 429
        
        # Add current request
        rate_limits[client_ip].append(now)
        
        return f(*args, **kwargs)
    return decorated_function

# Add request ID to all requests
@app.before_request
def before_request():
    add_request_id()

# Register blueprints
app.register_blueprint(session_bp)
app.register_blueprint(admin_bp)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Enhanced health check with component status"""
    try:
        health_data = {
            'success': True,
            'status': 'healthy',
            'service': 'VALIS 2.0 Cloud Server',
            'version': '2.0',
            'timestamp': datetime.now().isoformat(),
            'request_id': g.request_id,
            'components': {}
        }
        
        # Test database connection
        try:
            db.query("SELECT 1")
            health_data['components']['database'] = {
                'status': 'healthy',
                'type': 'postgresql'
            }
        except Exception as e:
            health_data['components']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_data['status'] = 'degraded'
        
        # Test tool manager
        try:
            tool_health = tool_manager.health_check()
            health_data['components']['tools'] = {
                'status': tool_health['status'],
                'available_tools': tool_health['available_tools']
            }
            if tool_health['status'] != 'healthy':
                health_data['status'] = 'degraded'
        except Exception as e:
            health_data['components']['tools'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_data['status'] = 'degraded'
        
        # Memory system status
        try:
            persona_count = len(db.query("SELECT id FROM persona_profiles"))
            health_data['components']['memory'] = {
                'status': 'healthy',
                'personas': persona_count
            }
        except Exception as e:
            health_data['components']['memory'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_data['status'] = 'degraded'
        
        status_code = 200 if health_data['status'] == 'healthy' else 503
        return jsonify(health_data), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'error',
            'error': str(e),
            'request_id': getattr(g, 'request_id', 'unknown')
        }), 500

@app.route('/api/chat', methods=['POST'])
@rate_limit
def chat():
    """Main chat endpoint with persona-aware routing and enhanced logging"""
    request_start = time.time()
    
    try:
        logger.info(f"Chat request received from {request.remote_addr}")
        
        data = request.get_json()
        if not data:
            logger.warning("Chat request with no data")
            return jsonify({
                'success': False, 
                'error': 'No data provided',
                'request_id': g.request_id
            }), 400
        
        # Extract required fields
        message = data.get('message', '').strip()
        client_id = data.get('client_id')
        persona_id = data.get('persona_id')
        context_mode = data.get('context_mode', 'balanced')
        
        # Validate required fields
        if not message:
            logger.warning(f"Empty message in chat request")
            return jsonify({
                'success': False, 
                'error': 'Message is required',
                'request_id': g.request_id
            }), 400
        if not client_id:
            logger.warning(f"Missing client_id in chat request")
            return jsonify({
                'success': False, 
                'error': 'Client ID is required',
                'request_id': g.request_id
            }), 400
        if not persona_id:
            logger.warning(f"Missing persona_id in chat request")
            return jsonify({
                'success': False, 
                'error': 'Persona ID is required',
                'request_id': g.request_id
            }), 400
        
        # Validate client exists
        try:
            client = memory.get_client(client_id)
            if not client:
                logger.warning(f"Invalid client_id: {client_id}")
                return jsonify({
                    'success': False, 
                    'error': 'Invalid client ID',
                    'request_id': g.request_id
                }), 400
        except Exception as e:
            logger.error(f"Error validating client {client_id}: {e}")
            return jsonify({
                'success': False, 
                'error': 'Client validation failed',
                'request_id': g.request_id
            }), 500
        
        # Validate persona exists
        try:
            persona = memory.get_persona(persona_id)
            if not persona:
                logger.warning(f"Invalid persona_id: {persona_id}")
                return jsonify({
                    'success': False, 
                    'error': 'Invalid persona ID',
                    'request_id': g.request_id
                }), 400
        except Exception as e:
            logger.error(f"Error validating persona {persona_id}: {e}")
            return jsonify({
                'success': False, 
                'error': 'Persona validation failed',
                'request_id': g.request_id
            }), 500
        
        logger.info(f"Processing chat: {message[:50]}... (client: {client_id[:8]}, persona: {persona['name']})")
        
        # Run inference with persona-aware routing
        try:
            result = run_inference(
                prompt=message,
                client_id=client_id,
                persona_id=persona_id
            )
        except Exception as e:
            logger.error(f"Inference failed for client {client_id}: {e}")
            return jsonify({
                'success': False,
                'error': 'AI processing failed',
                'request_id': g.request_id
            }), 500
        
        # Log session turn to database
        if result.get('success'):
            try:
                memory.log_session_turn(
                    client_id=client_id,
                    persona_id=persona_id,
                    user_input=message,
                    assistant_reply=result.get('response', ''),
                    session_id=f"public_chat_{client_id}",
                    metadata={
                        'request_id': g.request_id,
                        'provider_used': result.get('provider_used'),
                        'processing_time': time.time() - request_start
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to log session turn: {e}")
        
        # Return enhanced response
        response = {
            'success': result.get('success', False),
            'response': result.get('response', ''),
            'provider_used': result.get('provider_used', 'unknown'),
            'client_id': client_id,
            'persona_id': persona_id,
            'persona_name': persona['name'],
            'timestamp': result.get('timestamp'),
            'request_id': g.request_id,
            'processing_time': round(time.time() - request_start, 3)
        }
        
        if not result.get('success'):
            response['error'] = result.get('error', 'Unknown error')
        
        logger.info(f"Chat response: {result.get('success')} in {response['processing_time']}s")
        return jsonify(response)
        
    except Exception as e:
        processing_time = time.time() - request_start
        logger.error(f"Chat endpoint error after {processing_time:.3f}s: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'request_id': getattr(g, 'request_id', 'unknown'),
            'processing_time': round(processing_time, 3)
        }), 500

# Frontend routes
@app.route('/')
def public_chat():
    """Serve the public chat interface"""
    try:
        return send_from_directory('frontend', 'index.html')
    except Exception as e:
        logger.error(f"Failed to serve frontend: {e}")
        return f"Frontend not available: {e}", 404

@app.route('/favicon.ico')
def favicon():
    """Serve favicon to prevent 404 errors"""
    return '', 204  # No Content

@app.route('/admin')
def admin_dashboard():
    """Serve the admin dashboard"""
    try:
        return send_from_directory('frontend/admin', 'index.html')
    except Exception as e:
        logger.error(f"Failed to serve admin frontend: {e}")
        return f"Admin dashboard not available: {e}", 404

if __name__ == '__main__':
    logger.info("Starting VALIS 2.0 Public Chat Server...")
    
    # Initialize VALIS system
    if initialize():
        logger.info("VALIS system initialized successfully")
        app.run(host='0.0.0.0', port=3001, debug=True)
    else:
        logger.error("Failed to initialize VALIS system")
        sys.exit(1)
