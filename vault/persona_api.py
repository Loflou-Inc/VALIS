"""
VALIS Persona Lifecycle API
REST endpoints for persona management and activation
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Add VALIS modules to path
sys.path.append('C:\\VALIS\\valis2')
sys.path.append('C:\\VALIS\\vault')

from persona_vault import PersonaVault

app = Flask(__name__)
CORS(app)

# Initialize persona vault
vault = PersonaVault()

@app.route('/api/persona/health', methods=['GET'])
def health_check():
    """Health check for persona lifecycle API"""
    return jsonify({
        "status": "ONLINE",
        "service": "VALIS Persona Lifecycle API",
        "version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "vault_stats": vault.get_vault_stats()
    })

@app.route('/api/persona/list', methods=['GET'])
def list_personas():
    """
    List all stored personas with metadata
    Supports filtering by status and type
    """
    try:
        status = request.args.get('status')
        persona_type = request.args.get('type')
        include_blueprint = request.args.get('include_blueprint', 'false').lower() == 'true'
        
        personas = vault.list_personas(status=status, persona_type=persona_type)
        
        # Optionally include full blueprints
        if include_blueprint:
            for persona in personas:
                blueprint = vault.get_persona(persona['uuid'])
                persona['blueprint'] = blueprint
        
        return jsonify({
            "personas": personas,
            "total_count": len(personas),
            "filters": {
                "status": status,
                "type": persona_type
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to list personas: {str(e)}"}), 500

@app.route('/api/persona/<identifier>', methods=['GET'])
def get_persona(identifier):
    """
    Get full persona blueprint by UUID or name
    """
    try:
        blueprint = vault.get_persona(identifier)
        
        if not blueprint:
            return jsonify({"error": "Persona not found"}), 404
        
        # Get vault metadata
        personas = vault.list_personas()
        vault_data = next((p for p in personas if p['name'] == identifier or p['uuid'] == identifier), {})
        
        return jsonify({
            "blueprint": blueprint,
            "vault_metadata": vault_data,
            "history": vault.get_persona_history(identifier)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get persona: {str(e)}"}), 500

@app.route('/api/persona/initiate', methods=['POST'])
def initiate_persona():
    """
    Launch persona session in sandbox or production
    """
    try:
        data = request.get_json()
        
        if not data or 'persona' not in data:
            return jsonify({"error": "Persona identifier required"}), 400
        
        persona_identifier = data['persona']
        user_id = data.get('user_id', 'system')
        sandbox = data.get('sandbox', True)
        
        # Verify persona exists and can be initiated
        blueprint = vault.get_persona(persona_identifier)
        if not blueprint:
            return jsonify({"error": "Persona not found"}), 404
        
        # Check status
        personas = vault.list_personas()
        vault_data = next((p for p in personas if p['name'] == persona_identifier or p['uuid'] == persona_identifier), {})
        
        if not vault_data:
            return jsonify({"error": "Persona not found in vault"}), 404
        
        status = vault_data.get('status')
        if status not in ['active', 'draft']:
            return jsonify({"error": f"Persona is {status} and cannot be initiated"}), 400
        
        # Start session
        session_id = vault.start_session(persona_identifier, user_id)
        
        # Prepare persona configuration for runtime
        persona_config = {
            "session_id": session_id,
            "persona_uuid": vault_data['uuid'],
            "persona_name": vault_data['name'],
            "blueprint": blueprint,
            "sandbox_mode": sandbox,
            "user_id": user_id,
            "initiated_at": datetime.now(timezone.utc).isoformat()
        }
        
        return jsonify({
            "session_initiated": True,
            "session_id": session_id,
            "persona_config": persona_config,
            "endpoints": {
                "chat": f"/api/persona/chat/{session_id}",
                "status": f"/api/persona/session/{session_id}/status",
                "end": f"/api/persona/session/{session_id}/end"
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to initiate persona: {str(e)}"}), 500

@app.route('/api/persona/status/<identifier>', methods=['POST'])
def update_persona_status(identifier):
    """
    Update persona vault status (draft, active, archived, locked)
    """
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({"error": "Status required"}), 400
        
        new_status = data['status']
        description = data.get('description', f"Status updated to {new_status}")
        
        result = vault.update_status(identifier, new_status, description)
        
        if not result:
            return jsonify({"error": "Persona not found or update failed"}), 404
        
        return jsonify({
            "status_updated": True,
            "persona": identifier,
            "new_status": new_status,
            "description": description,
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update status: {str(e)}"}), 500

@app.route('/api/persona/fork', methods=['POST'])
def fork_persona():
    """
    Create a fork of an existing persona
    """
    try:
        data = request.get_json()
        
        if not data or 'source' not in data or 'new_name' not in data:
            return jsonify({"error": "Source persona and new_name required"}), 400
        
        source_identifier = data['source']
        new_name = data['new_name']
        changes = data.get('changes', {})
        
        new_uuid = vault.fork_persona(source_identifier, new_name, changes)
        
        return jsonify({
            "fork_created": True,
            "source_persona": source_identifier,
            "new_persona_uuid": new_uuid,
            "new_persona_name": new_name,
            "changes_applied": bool(changes)
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to fork persona: {str(e)}"}), 500

@app.route('/api/persona/<identifier>/history', methods=['GET'])
def get_persona_history(identifier):
    """
    Get version history of a persona
    """
    try:
        history = vault.get_persona_history(identifier)
        
        if not history:
            return jsonify({"error": "Persona not found or no history"}), 404
        
        return jsonify({
            "persona": identifier,
            "history": history,
            "version_count": len(history)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get history: {str(e)}"}), 500

@app.route('/api/persona/session/<session_id>/status', methods=['GET'])
def get_session_status(session_id):
    """
    Get status of a persona session
    """
    try:
        # Query session from vault database
        import sqlite3
        
        with sqlite3.connect(vault.db_path) as conn:
            cursor = conn.execute("""
                SELECT ps.*, p.name as persona_name 
                FROM persona_sessions ps
                JOIN personas p ON ps.persona_uuid = p.uuid
                WHERE ps.session_id = ?
            """, (session_id,))
            
            result = cursor.fetchone()
            
            if not result:
                return jsonify({"error": "Session not found"}), 404
            
            columns = [description[0] for description in cursor.description]
            session_data = dict(zip(columns, result))
            
            return jsonify({
                "session": session_data,
                "is_active": session_data['status'] == 'active'
            })
            
    except Exception as e:
        return jsonify({"error": f"Failed to get session status: {str(e)}"}), 500

@app.route('/api/persona/session/<session_id>/end', methods=['POST'])
def end_session(session_id):
    """
    End a persona session
    """
    try:
        data = request.get_json() or {}
        interaction_count = data.get('interaction_count', 0)
        
        result = vault.end_session(session_id, interaction_count)
        
        if not result:
            return jsonify({"error": "Session not found"}), 404
        
        return jsonify({
            "session_ended": True,
            "session_id": session_id,
            "interaction_count": interaction_count,
            "ended_at": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to end session: {str(e)}"}), 500

@app.route('/api/persona/chat/<session_id>', methods=['POST'])
def chat_with_persona(session_id):
    """
    Chat with a persona in an active session
    This is a placeholder - actual implementation would integrate with VALIS runtime
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Message required"}), 400
        
        message = data['message']
        
        # Get session info
        import sqlite3
        
        with sqlite3.connect(vault.db_path) as conn:
            cursor = conn.execute("""
                SELECT ps.*, p.name as persona_name, p.uuid as persona_uuid
                FROM persona_sessions ps
                JOIN personas p ON ps.persona_uuid = p.uuid
                WHERE ps.session_id = ? AND ps.status = 'active'
            """, (session_id,))
            
            result = cursor.fetchone()
            
            if not result:
                return jsonify({"error": "Active session not found"}), 404
            
            columns = [description[0] for description in cursor.description]
            session_data = dict(zip(columns, result))
        
        # Get persona blueprint for response generation
        blueprint = vault.get_persona(session_data['persona_uuid'])
        
        # Generate simulated response (placeholder)
        response = f"[{session_data['persona_name']}]: Thank you for your message. This is a simulated response in session {session_id}."
        
        # Update interaction count
        with sqlite3.connect(vault.db_path) as conn:
            conn.execute("""
                UPDATE persona_sessions 
                SET interaction_count = interaction_count + 1
                WHERE session_id = ?
            """, (session_id,))
            conn.commit()
        
        return jsonify({
            "response": response,
            "session_id": session_id,
            "persona_name": session_data['persona_name'],
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Chat failed: {str(e)}"}), 500

@app.route('/api/persona/registry', methods=['GET'])
def get_persona_registry():
    """
    Get public persona registry (scaffolding for future public UX)
    """
    try:
        # Only return active personas with public visibility
        personas = vault.list_personas(status='active')
        
        # Create public registry entries
        registry = []
        for persona in personas:
            # Only include if marked as public (future feature)
            public_visibility = persona.get('public_visibility', False)
            
            registry_entry = {
                "uuid": persona['uuid'],
                "name": persona['name'],
                "type": persona['type'],
                "archetypes": persona.get('archetypes', []),
                "domains": persona.get('domains', []),
                "summary": f"A {persona['type']} persona with {len(persona.get('archetypes', []))} archetypes",
                "confidence": persona.get('fusion_confidence', 0.0),
                "is_forkable": persona.get('is_forkable', True)
            }
            
            registry.append(registry_entry)
        
        return jsonify({
            "registry": registry,
            "total_count": len(registry),
            "public_access": False,  # Currently private
            "note": "Persona registry is currently for internal use only"
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get registry: {str(e)}"}), 500

@app.route('/api/persona/vault/stats', methods=['GET'])
def get_vault_stats():
    """
    Get comprehensive vault statistics
    """
    try:
        stats = vault.get_vault_stats()
        
        # Add additional metrics
        import sqlite3
        
        with sqlite3.connect(vault.db_path) as conn:
            # Session statistics
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_sessions,
                    AVG(interaction_count) as avg_interactions_per_session
                FROM persona_sessions
            """)
            session_stats = cursor.fetchone()
            
            stats["session_statistics"] = {
                "total_sessions": session_stats[0],
                "active_sessions": session_stats[1], 
                "avg_interactions": round(session_stats[2] or 0, 2)
            }
            
            # Persona type distribution
            cursor = conn.execute("""
                SELECT type, COUNT(*) 
                FROM personas 
                GROUP BY type
            """)
            stats["personas_by_type"] = dict(cursor.fetchall())
        
        return jsonify({
            "vault_statistics": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get vault stats: {str(e)}"}), 500

# Error handlers
@app.route('/api/persona/register', methods=['POST'])
def register_persona():
    """
    Register a persona from Mr. Fission into the vault
    """
    try:
        data = request.get_json()
        persona_name = data.get('persona_name')
        status = data.get('status', 'draft')
        source = data.get('source', 'api')
        
        if not persona_name:
            return jsonify({"error": "persona_name is required"}), 400
        
        # Check if persona exists in personas folder
        import os
        import json
        
        persona_file = f"{persona_name.lower().replace(' ', '_')}.json"
        persona_path = os.path.join('C:\\VALIS\\vault\\personas', persona_file)
        
        if not os.path.exists(persona_path):
            return jsonify({"error": f"Persona blueprint not found: {persona_file}"}), 404
        
        # Load blueprint and store in vault
        with open(persona_path, 'r', encoding='utf-8') as f:
            blueprint = json.load(f)
        
        # Store in vault using existing method
        persona_uuid = vault.store_persona(blueprint, status=status)
        
        return jsonify({
            "success": True,
            "persona_id": persona_uuid,
            "persona_name": persona_name,
            "status": status,
            "source": source,
            "message": f"Persona {persona_name} registered in vault"
        })
        
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@app.route('/api/persona/activate', methods=['POST'])
def activate_persona():
    """
    Activate a persona in the vault (draft -> active)
    """
    try:
        data = request.get_json()
        persona_name = data.get('persona_name')
        
        if not persona_name:
            return jsonify({"error": "persona_name is required"}), 400
        
        # Find persona by name
        personas = vault.list_personas()
        target_persona = None
        for persona in personas:
            if persona['name'].lower() == persona_name.lower():
                target_persona = persona
                break
        
        if not target_persona:
            return jsonify({"error": f"Persona {persona_name} not found in vault"}), 404
        
        # Update status to active
        result = vault.update_status(target_persona['uuid'], 'active')
        
        return jsonify({
            "success": True,
            "persona_id": target_persona['uuid'],
            "persona_name": persona_name,
            "status": "active",
            "message": f"Persona {persona_name} activated"
        })
        
    except Exception as e:
        return jsonify({"error": f"Activation failed: {str(e)}"}), 500

@app.route('/api/persona/deploy', methods=['POST'])
def deploy_persona():
    """
    Deploy a persona from vault to main VALIS database
    """
    try:
        data = request.get_json()
        persona_name = data.get('persona_name')
        target = data.get('target', 'valis_main')
        
        if not persona_name:
            return jsonify({"error": "persona_name is required"}), 400
        
        # Import bridge functionality
        from vault_db_bridge import VaultDBBridge
        
        bridge = VaultDBBridge()
        
        # Find persona in vault
        personas = vault.list_personas()
        target_persona = None
        for persona in personas:
            if persona['name'].lower() == persona_name.lower():
                target_persona = persona
                break
        
        if not target_persona:
            return jsonify({"error": f"Persona {persona_name} not found in vault"}), 404
        
        # Deploy to VALIS main database
        valis_persona_id = bridge.deploy_vault_persona_to_main_db(target_persona['uuid'])
        
        return jsonify({
            "success": True,
            "persona_id": target_persona['uuid'],
            "valis_id": valis_persona_id,
            "persona_name": persona_name,
            "target": target,
            "message": f"Persona {persona_name} deployed to VALIS",
            "deployment_details": {
                "vault_persona_id": target_persona['uuid'],
                "valis_persona_id": valis_persona_id
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Deployment failed: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("=== VALIS PERSONA LIFECYCLE API STARTING ===")
    print("The Garden Gate - Persona Management Layer")
    print("\nAPI Endpoints:")
    print("  GET  /api/persona/health - Health check and stats")
    print("  GET  /api/persona/list - List all personas")
    print("  GET  /api/persona/<id> - Get persona blueprint")
    print("  POST /api/persona/initiate - Start persona session")
    print("  POST /api/persona/status/<id> - Update persona status")
    print("  POST /api/persona/fork - Fork existing persona")
    print("  GET  /api/persona/<id>/history - Get persona history")
    print("  GET  /api/persona/session/<id>/status - Get session status")
    print("  POST /api/persona/session/<id>/end - End session")
    print("  POST /api/persona/chat/<id> - Chat with persona")
    print("  GET  /api/persona/registry - Public persona registry")
    print("  GET  /api/persona/vault/stats - Vault statistics")
    print("  POST /api/persona/register - Register persona from Mr. Fission")
    print("  POST /api/persona/activate - Activate persona in vault")
    print("  POST /api/persona/deploy - Deploy persona to VALIS")
    print("=== THE GARDEN GATE IS OPEN ===")
    
    app.run(host='0.0.0.0', port=8002, debug=True)
