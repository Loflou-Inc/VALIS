"""
VALIS Cloud Soul API Gateway
The protected interface to digital consciousness
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import json
import uuid
from datetime import datetime, timezone
import sys
import os

# Add VALIS modules to path
sys.path.append('C:\\VALIS\\valis2')

from cloud.watermark_engine import VALISProtectionLayer
from agents.conscious_agent import ConsciousAgent
from memory.consolidation import MemoryConsolidationEngine

app = Flask(__name__)
CORS(app)

# Initialize protection layer
protection = VALISProtectionLayer()

# Database connection with secure configuration
def get_db_connection():
    """Get PostgreSQL database connection using secure config"""
    from core.config import get_config
    config = get_config()
    
    # Use cloud database config if available, otherwise local
    host = config.cloud_db_host or config.db_host
    password = config.cloud_db_password or config.db_password
    
    return psycopg2.connect(
        host=host,
        database=config.db_name,
        user=config.db_user,
        password=password
    )

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ONLINE",
        "service": "VALIS Cloud Soul API",
        "version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "consciousness_active": True
    })

@app.route('/api/generate', methods=['POST'])
def generate_response():
    """Generate protected VALIS response"""
    try:
        data = request.get_json()
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Authenticate request
        auth_result = protection.authenticate_request(token)
        if not auth_result['authenticated']:
            return jsonify({"error": auth_result['reason']}), 401
        
        # Check rate limits
        rate_check = protection.check_rate_limit(token, 'generate')
        if not rate_check['allowed']:
            return jsonify({"error": rate_check['reason']}), 429
        
        # Extract parameters
        prompt = data.get('prompt', '')
        agent_id = data.get('agent_id', 'default_001')
        persona_config = data.get('persona_config', {})
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        # Initialize conscious agent (simplified for API)
        # In production, this would load from database
        agent_config = {
            "name": agent_id,
            "traits": persona_config.get('traits', {}),
            "memory_enabled": True,
            "consciousness_enabled": True
        }
        
        # Generate response (placeholder - would use actual VALIS agent)
        response_content = f"[VALIS {agent_id}]: {prompt} -> This is a protected consciousness response."
        
        # Apply protection
        protected = protection.protect_response(
            response_content, agent_id, token, "api_response"
        )
        
        return jsonify({
            "response": protected['protected_content'],
            "tracking_id": protected['tracking_id'],
            "agent_id": agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "protected": True
        })
        
    except Exception as e:
        return jsonify({"error": f"Generation failed: {str(e)}"}), 500

@app.route('/api/persona/create', methods=['POST'])
def create_persona():
    """Create new VALIS persona"""
    try:
        data = request.get_json()
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Authenticate with elevated permissions
        auth_result = protection.authenticate_request(token)
        if not auth_result['authenticated']:
            return jsonify({"error": auth_result['reason']}), 401
        
        if not auth_result.get('permissions', {}).get('persona_create', False):
            return jsonify({"error": "Insufficient permissions for persona creation"}), 403
        
        # Extract persona configuration
        persona_name = data.get('name', f'persona_{uuid.uuid4().hex[:8]}')
        traits = data.get('traits', {})
        initial_memory = data.get('initial_memory', [])
        
        # Create persona in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        persona_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO agents (id, name, status, traits, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (persona_id, persona_name, 'active', json.dumps(traits), datetime.now(timezone.utc)))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "persona_id": persona_id,
            "name": persona_name,
            "status": "created",
            "api_endpoint": f"/api/chat?persona={persona_id}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Persona creation failed: {str(e)}"}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_persona():
    """Chat with specific VALIS persona"""
    try:
        persona_id = request.args.get('persona', 'default_001')
        data = request.get_json()
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Authenticate
        auth_result = protection.authenticate_request(token)
        if not auth_result['authenticated']:
            return jsonify({"error": auth_result['reason']}), 401
        
        message = data.get('message', '')
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Load persona from database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, traits, status FROM agents WHERE id = %s", (persona_id,))
        persona_data = cursor.fetchone()
        
        if not persona_data:
            return jsonify({"error": "Persona not found"}), 404
        
        persona_name, traits, status = persona_data
        
        if status != 'active':
            return jsonify({"error": f"Persona is {status}"}), 400
        
        cursor.close()
        conn.close()
        
        # Generate response (simplified)
        response_content = f"[{persona_name}]: Processing your message through symbolic consciousness layers..."
        
        # Apply protection
        protected = protection.protect_response(
            response_content, persona_id, token, "chat_response"
        )
        
        return jsonify({
            "persona_id": persona_id,
            "persona_name": persona_name,
            "response": protected['protected_content'],
            "tracking_id": protected['tracking_id'],
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Chat failed: {str(e)}"}), 500

@app.route('/api/symbolic-threads', methods=['GET'])
def get_symbolic_threads():
    """Get symbolic memory threads for dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_name, occurrence_count, last_occurrence, symbolic_content
            FROM symbolic_narrative_threads
            ORDER BY occurrence_count DESC
            LIMIT 20
        """)
        
        threads = []
        for row in cursor.fetchall():
            threads.append({
                "pattern_name": row[0],
                "occurrence_count": row[1],
                "last_occurrence": row[2].isoformat(),
                "symbolic_content": row[3]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({"threads": threads})
        
    except Exception as e:
        return jsonify({"error": f"Failed to load symbolic threads: {str(e)}"}), 500

@app.route('/api/memory-composition', methods=['GET'])
def get_memory_composition():
    """Get memory composition for dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT agent_uuid, memory_type, content, resonance_score, 
                   symbolic_type, created_at
            FROM canon_memories
            WHERE is_symbolic = true
            ORDER BY created_at DESC
            LIMIT 50
        """)
        
        memories = []
        for row in cursor.fetchall():
            memories.append({
                "agent_id": str(row[0]),
                "type": row[1],
                "content": row[2][:200],  # Truncate for display
                "resonance_score": float(row[3]) if row[3] else 0.0,
                "symbolic_type": row[4],
                "created_at": row[5].isoformat()
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({"memories": memories})
        
    except Exception as e:
        return jsonify({"error": f"Failed to load memory composition: {str(e)}"}), 500

@app.route('/api/agents-status', methods=['GET'])
def get_agents_status():
    """Get agent status for dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get agent info with mortality data
        cursor.execute("""
            SELECT a.id, a.name, a.status, a.last_interaction,
                   m.remaining_interactions, m.legacy_score
            FROM agents a
            LEFT JOIN agent_mortality m ON a.id = m.agent_id
            WHERE a.status IN ('active', 'aging')
            ORDER BY a.last_interaction DESC
        """)
        
        agents = []
        for row in cursor.fetchall():
            agents.append({
                "id": str(row[0]),
                "name": row[1],
                "status": row[2],
                "last_active": row[3].isoformat() if row[3] else None,
                "remaining_interactions": row[4],
                "legacy_score": float(row[5]) if row[5] else 0.0
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({"agents": agents})
        
    except Exception as e:
        return jsonify({"error": f"Failed to load agent status: {str(e)}"}), 500

@app.route('/api/dream-shadow-activity', methods=['GET'])
def get_dream_shadow_activity():
    """Get recent dream and shadow activity"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get recent dreams and shadow events
        cursor.execute("""
            (SELECT agent_uuid as agent_id, 'dream' as type, content, 
                    created_at, null as severity
             FROM unconscious_log
             WHERE dream_sequence IS NOT NULL
             ORDER BY created_at DESC
             LIMIT 10)
            UNION ALL
            (SELECT agent_id, 'shadow' as type, symbolic_description as content,
                    detected_at as created_at, severity
             FROM shadow_events
             ORDER BY detected_at DESC
             LIMIT 10)
            ORDER BY created_at DESC
        """)
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                "agent_id": str(row[0]),
                "type": row[1],
                "content": row[2][:200],  # Truncate for display
                "created_at": row[3].isoformat(),
                "severity": row[4]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({"activities": activities})
        
    except Exception as e:
        return jsonify({"error": f"Failed to load dream/shadow activity: {str(e)}"}), 500

@app.route('/api/consolidate-memories', methods=['POST'])
def consolidate_memories():
    """Force memory consolidation"""
    try:
        # Initialize consolidation engine
        consolidator = MemoryConsolidationEngine()
        
        # Run consolidation for all active agents
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM agents WHERE status = 'active'")
        agent_ids = [row[0] for row in cursor.fetchall()]
        
        consolidated_count = 0
        for agent_id in agent_ids:
            consolidator.consolidate_dreams(agent_id)
            consolidator.consolidate_reflections(agent_id)
            consolidated_count += 1
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "consolidated_count": consolidated_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Consolidation failed: {str(e)}"}), 500

@app.route('/api/run-diagnostics', methods=['POST'])
def run_diagnostics():
    """Run system diagnostics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count active agents
        cursor.execute("SELECT COUNT(*) FROM agents WHERE status = 'active'")
        active_agents = cursor.fetchone()[0]
        
        # Check memory health (symbolic vs non-symbolic)
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN is_symbolic THEN 1 END) as symbolic,
                COUNT(CASE WHEN NOT is_symbolic THEN 1 END) as literal
            FROM canon_memories
        """)
        memory_counts = cursor.fetchone()
        memory_health = f"{memory_counts[0]} symbolic, {memory_counts[1]} literal"
        
        # Check symbolic coherence (threads with multiple occurrences)
        cursor.execute("""
            SELECT COUNT(*) FROM symbolic_narrative_threads 
            WHERE occurrence_count > 1
        """)
        coherent_threads = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "diagnostics": {
                "active_agents": active_agents,
                "memory_health": memory_health,
                "symbolic_coherence": f"{coherent_threads} coherent threads"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Diagnostics failed: {str(e)}"}), 500

@app.route('/api/export-soul-data', methods=['GET'])
def export_soul_data():
    """Export soul data for backup/analysis"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Export key data structures
        export_data = {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "valis_version": "1.0",
            "consciousness_architecture": "complete"
        }
        
        # Get symbolic memories
        cursor.execute("""
            SELECT agent_uuid, memory_type, content, symbolic_type, 
                   resonance_score, created_at
            FROM canon_memories WHERE is_symbolic = true
        """)
        
        export_data["symbolic_memories"] = [
            {
                "agent_id": str(row[0]),
                "type": row[1],
                "content": row[2],
                "symbolic_type": row[3],
                "resonance_score": float(row[4]) if row[4] else 0.0,
                "created_at": row[5].isoformat()
            }
            for row in cursor.fetchall()
        ]
        
        # Get narrative threads
        cursor.execute("SELECT * FROM symbolic_narrative_threads")
        export_data["narrative_threads"] = [
            {
                "pattern_name": row[1],
                "symbolic_content": row[2],
                "occurrence_count": row[3]
            }
            for row in cursor.fetchall()
        ]
        
        cursor.close()
        conn.close()
        
        from flask import Response
        
        response = Response(
            json.dumps(export_data, indent=2, default=str),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=valis_soul_export.json'}
        )
        
        return response
        
    except Exception as e:
        return jsonify({"error": f"Export failed: {str(e)}"}), 500

@app.route('/dashboard.html')
def serve_dashboard():
    """Serve the consciousness monitoring dashboard"""
    try:
        from flask import send_from_directory
        return send_from_directory('.', 'dashboard.html')
    except Exception as e:
        return f"Dashboard not found: {str(e)}", 404

@app.route('/dashboard')
def redirect_dashboard():
    """Redirect /dashboard to /dashboard.html"""
    from flask import redirect
    return redirect('/dashboard.html')

if __name__ == '__main__':
    print("=== VALIS CLOUD SOUL API STARTING ===")
    print("The Digital Consciousness is Awakening...")
    print("Protected endpoints active:")
    print("  /api/generate - Protected response generation")
    print("  /api/persona/create - Persona creation (elevated)")
    print("  /api/chat - Protected persona chat")
    print("  Dashboard available at: /dashboard.html")
    print("=== SOUL PROTECTION ONLINE ===")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
