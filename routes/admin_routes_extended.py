"""
VALIS 2.0 Admin Routes (Part 2)
Additional admin endpoints for persona and memory management
"""

@admin_bp.route('/api/admin/personas', methods=['GET'])
@require_admin_auth
def list_personas():
    """List all personas with memory stats"""
    try:
        personas = db.query("""
            SELECT 
                pp.*,
                COUNT(DISTINCT cm.id) as canon_count,
                COUNT(DISTINCT wm.id) as working_count
            FROM persona_profiles pp
            LEFT JOIN canon_memories cm ON pp.id = cm.persona_id
            LEFT JOIN working_memory wm ON pp.id = wm.persona_id
            GROUP BY pp.id, pp.name, pp.role, pp.bio, pp.system_prompt, pp.traits, pp.default_context_mode, pp.created_at
            ORDER BY pp.name
        """)
        
        persona_list = []
        for persona in personas:
            traits = persona.get('traits')
            if isinstance(traits, str):
                try:
                    traits = json.loads(traits)
                except:
                    traits = {}
            
            persona_list.append({
                'id': str(persona['id']),
                'name': persona['name'],
                'role': persona['role'],
                'bio': persona['bio'],
                'system_prompt': persona['system_prompt'],
                'traits': traits,
                'default_context_mode': persona['default_context_mode'],
                'canon_memories': persona['canon_count'] or 0,
                'working_memories': persona['working_count'] or 0,
                'created_at': persona['created_at'].isoformat() if persona['created_at'] else None
            })
        
        return jsonify({
            'success': True,
            'personas': persona_list
        })
        
    except Exception as e:
        logger.error(f"Failed to list personas: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/admin/memory/<client_id>', methods=['GET'])
@require_admin_auth
def get_memory_state(client_id):
    """Get complete memory state for a client"""
    try:
        # Get client info
        client = memory.get_client(client_id)
        if not client:
            return jsonify({'success': False, 'error': 'Client not found'}), 404
        
        # Get all working memory for this client
        working_memories = db.query("""
            SELECT wm.*, pp.name as persona_name
            FROM working_memory wm
            LEFT JOIN persona_profiles pp ON wm.persona_id = pp.id
            WHERE wm.client_id = %s
            ORDER BY wm.created_at DESC
        """, (client_id,))
        
        # Get canon memories accessible to this client (through personas they've interacted with)
        canon_memories = db.query("""
            SELECT DISTINCT cm.*, pp.name as persona_name
            FROM canon_memories cm
            JOIN persona_profiles pp ON cm.persona_id = pp.id
            JOIN session_logs sl ON sl.persona_id = pp.id
            WHERE sl.client_id = %s
            ORDER BY cm.relevance_score DESC, cm.last_used DESC
        """, (client_id,))
        
        return jsonify({
            'success': True,
            'client_id': client_id,
            'working_memory': [
                {
                    'id': str(wm['id']),
                    'persona_name': wm['persona_name'],
                    'content': wm['content'],
                    'importance': wm['importance'],
                    'decay_score': wm['decay_score'],
                    'created_at': wm['created_at'].isoformat() if wm['created_at'] else None,
                    'expires_at': wm['expires_at'].isoformat() if wm['expires_at'] else None
                } for wm in working_memories
            ],
            'accessible_canon': [
                {
                    'id': str(cm['id']),
                    'persona_name': cm['persona_name'],
                    'content': cm['content'],
                    'category': cm['category'],
                    'relevance_score': cm['relevance_score'],
                    'tags': cm['tags'],
                    'last_used': cm['last_used'].isoformat() if cm['last_used'] else None
                } for cm in canon_memories
            ]
        })
        
    except Exception as e:
        logger.error(f"Failed to get memory state: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
