# Add missing routes to MCP backend

@app.route('/api/sessions')
def get_sessions():
    """Get active sessions"""
    return jsonify([])

@app.route('/api/sessions/<session_id>/history')
def get_session_history(session_id):
    """Get session history"""
    return jsonify([])

@app.route('/api/memory/<persona_id>')
def get_memory_data(persona_id):
    """Get memory data with session parameter"""
    session_id = request.args.get('session')
    
    if not mcp_engine:
        return jsonify({"error": "MCP engine not available"}), 503
    
    status = mcp_engine.get_memory_status(persona_id)
    return jsonify({
        "persona_id": persona_id,
        "session_id": session_id,
        "memory_loaded": status.get("memory_accessible", False),
        "external_source": True,
        "layers": []
    })
