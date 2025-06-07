"""
VALIS 2.0 Session Routes
Handle public chat session initialization and management
"""
from flask import Blueprint, request, jsonify
import uuid
import logging
import sys
import os
from pathlib import Path

from memory.query_client import memory
from memory.db import db
import json

logger = logging.getLogger("SessionRoutes")
session_bp = Blueprint('session', __name__)

@session_bp.route('/api/init_session', methods=['POST'])
def init_session():
    """Initialize a new anonymous session with client_id and persona assignment"""
    try:
        data = request.get_json() or {}
        provided_client_id = data.get('client_id')
        
        # If client_id provided, check if it exists
        if provided_client_id:
            existing_client = memory.get_client(provided_client_id)
            if existing_client:
                # Return existing session info
                personas = db.query("SELECT id, name, role, default_context_mode FROM persona_profiles")
                if not personas:
                    return jsonify({'success': False, 'error': 'No personas available'}), 500
                
                assigned_persona = personas[0]  # Default to first for now
                
                return jsonify({
                    'success': True,
                    'client_id': str(existing_client['id']),
                    'persona_id': str(assigned_persona['id']),
                    'persona_name': assigned_persona['name'],
                    'persona_role': assigned_persona['role'],
                    'existing_session': True
                })
        
        # Create new client session
        new_client_id = str(uuid.uuid4())
        
        # Get available personas
        personas = db.query("SELECT id, name, role, default_context_mode FROM persona_profiles")
        if not personas:
            return jsonify({'success': False, 'error': 'No personas available'}), 500
        
        # Randomly assign a persona
        import random
        assigned_persona = random.choice(personas)
        
        # Create new client profile
        client_data = {
            'id': new_client_id,
            'name': f'Anonymous User {new_client_id[:8]}',
            'traits': json.dumps({
                'session_type': 'public_chat',
                'created_via': 'web_interface',
                'assigned_persona': assigned_persona['name']
            })
        }
        
        # Insert into database
        actual_client_id = db.insert('client_profiles', client_data)
        
        logger.info(f"Created new session: client_id={actual_client_id}, persona={assigned_persona['name']}")
        
        return jsonify({
            'success': True,
            'client_id': str(actual_client_id),
            'persona_id': str(assigned_persona['id']),
            'persona_name': assigned_persona['name'],
            'persona_role': assigned_persona['role'],
            'existing_session': False
        })
        
    except Exception as e:
        logger.error(f"Failed to initialize session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@session_bp.route('/api/persona_info/<persona_id>', methods=['GET'])
def get_persona_info(persona_id):
    """Get detailed persona information"""
    try:
        persona = memory.get_persona(persona_id)
        if not persona:
            return jsonify({'success': False, 'error': 'Persona not found'}), 404
        
        return jsonify({
            'success': True,
            'persona': {
                'id': str(persona['id']),
                'name': persona['name'],
                'role': persona['role'],
                'bio': persona['bio'],
                'default_context_mode': persona.get('default_context_mode', 'balanced'),
                'system_prompt': persona.get('system_prompt', '')
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get persona info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@session_bp.route('/api/available_personas', methods=['GET'])
def get_available_personas():
    """Get list of all available personas for public chat"""
    try:
        personas = db.query("SELECT id, name, role, bio, default_context_mode FROM persona_profiles ORDER BY name")
        
        persona_list = []
        for persona in personas:
            persona_list.append({
                'id': str(persona['id']),
                'name': persona['name'],
                'role': persona['role'],
                'bio': persona['bio'],
                'default_context_mode': persona.get('default_context_mode', 'balanced')
            })
        
        return jsonify({
            'success': True,
            'personas': persona_list
        })
        
    except Exception as e:
        logger.error(f"Failed to get available personas: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
