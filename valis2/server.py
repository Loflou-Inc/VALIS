#!/usr/bin/env python3
"""
VALIS 2.0 Public Chat Server
Flask server for public chat frontend with session management
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
import os
from pathlib import Path

# Add valis2 to path
valis2_dir = Path(__file__).parent
sys.path.append(str(valis2_dir))

from api.session_routes import session_bp
from api.admin_routes import admin_bp
from inference import run_inference, initialize
from memory.query_client import memory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VALIS_Server")

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Register blueprints
app.register_blueprint(session_bp)
app.register_blueprint(admin_bp)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'operational',
        'service': 'VALIS 2.0 Public Chat',
        'version': '2.0'
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint with persona-aware routing"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Extract required fields
        message = data.get('message', '').strip()
        client_id = data.get('client_id')
        persona_id = data.get('persona_id')
        context_mode = data.get('context_mode', 'balanced')
        
        # Validate required fields
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        if not client_id:
            return jsonify({'success': False, 'error': 'Client ID is required'}), 400
        if not persona_id:
            return jsonify({'success': False, 'error': 'Persona ID is required'}), 400
        
        # Validate client exists
        client = memory.get_client(client_id)
        if not client:
            return jsonify({'success': False, 'error': 'Invalid client ID'}), 400
        
        # Validate persona exists
        persona = memory.get_persona(persona_id)
        if not persona:
            return jsonify({'success': False, 'error': 'Invalid persona ID'}), 400
        
        logger.info(f"Chat request: {message[:50]}... (client: {client_id[:8]}, persona: {persona['name']})")
        
        # Run inference with persona-aware routing
        result = run_inference(
            prompt=message,
            client_id=client_id,
            persona_id=persona_id
        )
        
        # Log session turn to database
        if result.get('success'):
            try:
                memory.log_session_turn(
                    client_id=client_id,
                    persona_id=persona_id,
                    user_input=message,
                    assistant_reply=result.get('response', ''),
                    session_id=f"public_chat_{client_id}"
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
            'timestamp': result.get('timestamp')
        }
        
        if not result.get('success'):
            response['error'] = result.get('error', 'Unknown error')
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting VALIS 2.0 Public Chat Server...")
    
    # Initialize VALIS system
    if initialize():
        logger.info("VALIS system initialized successfully")
        app.run(host='0.0.0.0', port=3001, debug=True)
    else:
        logger.error("Failed to initialize VALIS system")
        sys.exit(1)
