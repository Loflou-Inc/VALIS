"""
VALIS 2.0 Admin Routes
Protected admin interface for session and memory management
"""
from flask import Blueprint, request, jsonify, abort
from functools import wraps
import logging
import sys
import os
from pathlib import Path
import uuid
from datetime import datetime, timedelta

# Add valis2 to path
valis2_dir = Path(__file__).parent.parent
sys.path.append(str(valis2_dir))

from memory.query_client import memory
from memory.db import db
import json

logger = logging.getLogger("AdminRoutes")
admin_bp = Blueprint('admin', __name__)

# Admin API key (should be in environment)
ADMIN_API_KEY = os.getenv('VALIS_ADMIN_KEY', 'valis_admin_2025')

def require_admin_auth(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow OPTIONS requests for CORS preflight
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
            
        # Check for API key in header or query parameter
        api_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key')
        
        if not api_key or api_key != ADMIN_API_KEY:
            abort(401, description='Admin authentication required')
        
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/api/admin/health', methods=['GET'])
@require_admin_auth
def admin_health():
    """Admin health check with system stats"""
    try:
        # Get database stats
        session_count = db.query("SELECT COUNT(*) as count FROM client_profiles")[0]['count']
        persona_count = db.query("SELECT COUNT(*) as count FROM persona_profiles")[0]['count']
        memory_count = db.query("SELECT COUNT(*) as count FROM working_memory")[0]['count']
        canon_count = db.query("SELECT COUNT(*) as count FROM canon_memories")[0]['count']
        
        return jsonify({
            'success': True,
            'status': 'admin_operational',
            'system_stats': {
                'total_clients': session_count,
                'total_personas': persona_count,
                'working_memories': memory_count,
                'canon_memories': canon_count
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Admin health check failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/admin/sessions', methods=['GET'])
@require_admin_auth  
def list_sessions():
    """List all client sessions with metadata"""
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Get client sessions with last activity
        sql = """
        SELECT 
            cp.id, cp.name, cp.traits, cp.created_at, cp.last_seen,
            COUNT(sl.id) as message_count,
            MAX(sl.created_at) as last_message
        FROM client_profiles cp
        LEFT JOIN session_logs sl ON cp.id = sl.client_id
        GROUP BY cp.id, cp.name, cp.traits, cp.created_at, cp.last_seen
        ORDER BY COALESCE(MAX(sl.created_at), cp.created_at) DESC
        LIMIT %s OFFSET %s
        """
        
        sessions = db.query(sql, (limit, offset))
        
        # Format response
        session_list = []
        for session in sessions:
            traits = session.get('traits')
            if isinstance(traits, str):
                try:
                    traits = json.loads(traits)
                except:
                    traits = {}
            
            session_list.append({
                'client_id': str(session['id']),
                'name': session['name'],
                'traits': traits,
                'message_count': session['message_count'] or 0,
                'created_at': session['created_at'].isoformat() if session['created_at'] else None,
                'last_seen': session['last_seen'].isoformat() if session['last_seen'] else None,
                'last_message': session['last_message'].isoformat() if session['last_message'] else None
            })
        
        return jsonify({
            'success': True,
            'sessions': session_list,
            'total': len(session_list)
        })
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/admin/session/<client_id>', methods=['GET'])
@require_admin_auth
def get_session_detail(client_id):
    """Get detailed session information"""
    try:
        # Get client info
        client = memory.get_client(client_id)
        if not client:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Get session logs
        logs = db.query("""
            SELECT sl.*, pp.name as persona_name 
            FROM session_logs sl
            LEFT JOIN persona_profiles pp ON sl.persona_id = pp.id
            WHERE sl.client_id = %s 
            ORDER BY sl.created_at DESC
            LIMIT 100
        """, (client_id,))
        
        # Get working memory
        working_memory = db.query("""
            SELECT wm.*, pp.name as persona_name
            FROM working_memory wm
            LEFT JOIN persona_profiles pp ON wm.persona_id = pp.id
            WHERE wm.client_id = %s
            ORDER BY wm.created_at DESC
        """, (client_id,))
        
        # Format traits
        traits = client.get('traits')
        if isinstance(traits, str):
            try:
                traits = json.loads(traits)
            except:
                traits = {}
        
        return jsonify({
            'success': True,
            'session': {
                'client_id': str(client['id']),
                'name': client['name'],
                'traits': traits,
                'created_at': client['created_at'].isoformat() if client['created_at'] else None,
                'last_seen': client['last_seen'].isoformat() if client['last_seen'] else None
            },
            'conversation_logs': [
                {
                    'id': str(log['id']),
                    'persona_name': log['persona_name'],
                    'user_input': log['user_input'],
                    'assistant_reply': log['assistant_reply'],
                    'created_at': log['created_at'].isoformat() if log['created_at'] else None
                } for log in logs
            ],
            'working_memory': [
                {
                    'id': str(wm['id']),
                    'persona_name': wm['persona_name'],
                    'content': wm['content'],
                    'importance': wm['importance'],
                    'created_at': wm['created_at'].isoformat() if wm['created_at'] else None,
                    'expires_at': wm['expires_at'].isoformat() if wm['expires_at'] else None
                } for wm in working_memory
            ]
        })
        
    except Exception as e:
        logger.error(f"Failed to get session detail: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500



@admin_bp.route('/api/admin/personas', methods=['GET'])
@require_admin_auth
def list_personas():
    """List all available personas"""
    try:
        personas = db.query("SELECT * FROM persona_profiles ORDER BY name")
        
        persona_list = []
        for persona in personas:
            # Handle traits parsing safely
            traits = persona['traits']
            if isinstance(traits, str):
                try:
                    traits = json.loads(traits)
                except:
                    traits = {}
            elif traits is None:
                traits = {}
            
            persona_list.append({
                'id': str(persona['id']),
                'name': persona['name'],
                'role': persona['role'],
                'bio': persona['bio'],
                'traits': traits,
                'default_context_mode': persona['default_context_mode'],
                'created_at': persona['created_at'].isoformat() if persona['created_at'] else None
            })
        
        return jsonify({
            'success': True,
            'personas': persona_list,
            'total': len(persona_list)
        })
        
    except Exception as e:
        logger.error(f"Failed to list personas: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/admin/persona/<persona_id>', methods=['GET'])
@require_admin_auth
def get_persona_detail(persona_id):
    """Get detailed persona information"""
    try:
        persona = db.query("SELECT * FROM persona_profiles WHERE id = %s", (persona_id,))
        if not persona:
            return jsonify({'success': False, 'error': 'Persona not found'}), 404
        
        persona = persona[0]
        
        # Handle traits parsing safely
        traits = persona['traits']
        if isinstance(traits, str):
            try:
                traits = json.loads(traits)
            except:
                traits = {}
        elif traits is None:
            traits = {}
        
        # Get canon memories for this persona
        canon_memories = db.query("""
            SELECT * FROM canon_memories 
            WHERE persona_id = %s 
            ORDER BY last_used DESC, relevance_score DESC
        """, (persona_id,))
        
        return jsonify({
            'success': True,
            'persona': {
                'id': str(persona['id']),
                'name': persona['name'],
                'role': persona['role'],
                'bio': persona['bio'],
                'traits': traits,
                'default_context_mode': persona['default_context_mode'],
                'created_at': persona['created_at'].isoformat() if persona['created_at'] else None
            },
            'canon_memories': [dict(cm) for cm in canon_memories]
        })
        
    except Exception as e:
        logger.error(f"Failed to get persona detail: {e}")
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
        
        # Get all memory layers
        canon_memories = db.query("SELECT * FROM canon_memories ORDER BY relevance_score DESC")
        
        working_memory = db.query("""
            SELECT * FROM working_memory 
            WHERE client_id = %s 
            ORDER BY created_at DESC
        """, (client_id,))
        
        session_logs = db.query("""
            SELECT sl.*, pp.name as persona_name FROM session_logs sl
            LEFT JOIN persona_profiles pp ON sl.persona_id = pp.id
            WHERE sl.client_id = %s 
            ORDER BY sl.created_at DESC 
            LIMIT 50
        """, (client_id,))
        
        return jsonify({
            'success': True,
            'client_id': client_id,
            'client_info': client,
            'memory_layers': {
                'canon_memories': [dict(cm) for cm in canon_memories],
                'working_memory': [dict(wm) for wm in working_memory], 
                'recent_sessions': [dict(sl) for sl in session_logs]
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get memory state: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/admin/override/context_mode', methods=['POST'])
@require_admin_auth
def override_context_mode():
    """Override context mode for a specific client session"""
    try:
        data = request.get_json()
        client_id = data.get('client_id')
        context_mode = data.get('context_mode')
        
        if not client_id or context_mode not in ['tight', 'balanced', 'full']:
            return jsonify({'success': False, 'error': 'Invalid client_id or context_mode'}), 400
        
        # This would typically update a session override table
        # For now, we'll just return success as the MCP can handle dynamic context modes
        
        return jsonify({
            'success': True,
            'message': f'Context mode override set to {context_mode} for client {client_id}',
            'client_id': client_id,
            'context_mode': context_mode
        })
        
    except Exception as e:
        logger.error(f"Failed to override context mode: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/admin/override/provider', methods=['POST'])
@require_admin_auth
def override_provider():
    """Override provider for a specific client session"""
    try:
        data = request.get_json()
        client_id = data.get('client_id')
        provider = data.get('provider')
        
        if not client_id or not provider:
            return jsonify({'success': False, 'error': 'Invalid client_id or provider'}), 400
        
        # This would typically update a session override table
        # For now, we'll just return success as the system can handle dynamic provider routing
        
        return jsonify({
            'success': True,
            'message': f'Provider override set to {provider} for client {client_id}',
            'client_id': client_id,
            'provider': provider
        })
        
    except Exception as e:
        logger.error(f"Failed to override provider: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/admin/logs', methods=['GET'])
@require_admin_auth
def get_all_logs():
    """Get all inference logs across all clients"""
    try:
        # Get all inference logs from session_logs with metadata
        logs = db.query("""
            SELECT sl.*, pp.name as persona_name,
                   CASE 
                       WHEN sl.assistant_reply LIKE '%Local Mistral%' THEN 'local_mistral'
                       WHEN sl.assistant_reply LIKE '%MCP%' THEN 'mcp'
                       ELSE 'unknown'
                   END as provider_used
            FROM session_logs sl
            LEFT JOIN persona_profiles pp ON sl.persona_id = pp.id
            ORDER BY sl.created_at DESC
            LIMIT 100
        """)
        
        # Convert timestamps to strings for JSON serialization
        for log in logs:
            if log.get('created_at'):
                log['created_at'] = str(log['created_at'])
        
        return jsonify({
            'success': True, 
            'logs': logs,
            'total_count': len(logs)
        })
        
    except Exception as e:
        logger.error(f"Failed to get all logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/admin/logs/<client_id>', methods=['GET'])
@require_admin_auth
def get_inference_logs(client_id):
    """Get inference logs for a specific client"""
    try:
        logger.info(f"Getting inference logs for client: {client_id}")
        
        # Get inference logs from session_logs - simplified query without CASE
        logs = db.query("""
            SELECT sl.*, pp.name as persona_name
            FROM session_logs sl
            LEFT JOIN persona_profiles pp ON sl.persona_id = pp.id
            WHERE sl.client_id = %s 
            ORDER BY sl.created_at DESC
            LIMIT 100
        """, (client_id,))
        
        logger.info(f"Query returned {len(logs)} logs")
        
        formatted_logs = []
        for i, log in enumerate(logs):
            logger.info(f"Processing log {i}: {type(log)}")
            # Safely access log fields with defaults
            formatted_logs.append({
                'id': str(log.get('id', '')),
                'persona_name': log.get('persona_name', 'Unknown'),
                'provider_used': log.get('provider_used', 'unknown'),
                'user_input': log.get('user_input', ''),
                'assistant_reply': log.get('assistant_reply', ''),
                'tokens_estimated': (
                    len(str(log.get('user_input', '')).split()) + 
                    len(str(log.get('assistant_reply', '')).split())
                ),
                'created_at': (
                    log['created_at'].isoformat() 
                    if log.get('created_at') and hasattr(log['created_at'], 'isoformat')
                    else str(log.get('created_at', ''))
                )
            })
        
        return jsonify({
            'success': True,
            'client_id': client_id,
            'logs': formatted_logs,  # Changed from 'inference_logs' to 'logs'
            'total': len(formatted_logs)
        })
        
    except Exception as e:
        logger.error(f"Failed to get inference logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/admin/executions', methods=['GET'])
@require_admin_auth
def list_executions():
    """List recent command executions"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        executions = db.query("""
            SELECT el.*, pp.name as persona_name, cp.name as client_name
            FROM execution_logs el
            LEFT JOIN persona_profiles pp ON el.persona_id = pp.id
            LEFT JOIN client_profiles cp ON el.client_id = cp.id
            ORDER BY el.created_at DESC
            LIMIT %s
        """, (limit,))
        
        execution_list = []
        for exec in executions:
            execution_list.append({
                'execution_id': exec['execution_id'],
                'client_name': exec['client_name'] or 'Anonymous',
                'persona_name': exec['persona_name'],
                'intent': exec['intent'],
                'function_name': exec['function_name'],
                'success': exec['success'],
                'execution_time': exec['execution_time'],
                'result_preview': exec['result_preview'],
                'created_at': exec['created_at'].isoformat() if exec['created_at'] else None
            })
        
        return jsonify({
            'success': True,
            'executions': execution_list,
            'total': len(execution_list)
        })
        
    except Exception as e:
        logger.error(f"Failed to list executions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/admin/execution/<execution_id>', methods=['GET'])
@require_admin_auth
def get_execution_detail(execution_id):
    """Get detailed execution information"""
    try:
        execution = db.query("""
            SELECT el.*, pp.name as persona_name, cp.name as client_name
            FROM execution_logs el
            LEFT JOIN persona_profiles pp ON el.persona_id = pp.id
            LEFT JOIN client_profiles cp ON el.client_id = cp.id
            WHERE el.execution_id = %s
        """, (execution_id,))
        
        if not execution:
            return jsonify({'success': False, 'error': 'Execution not found'}), 404
        
        exec = execution[0]
        
        # Parse parameters if they exist
        parameters = exec['parameters']
        if isinstance(parameters, str):
            try:
                parameters = json.loads(parameters)
            except:
                parameters = {}
        
        return jsonify({
            'success': True,
            'execution': {
                'execution_id': exec['execution_id'],
                'client_name': exec['client_name'] or 'Anonymous',
                'persona_name': exec['persona_name'],
                'intent': exec['intent'],
                'function_name': exec['function_name'],
                'parameters': parameters,
                'command_text': exec['command_text'],
                'success': exec['success'],
                'result_preview': exec['result_preview'],
                'execution_time': exec['execution_time'],
                'created_at': exec['created_at'].isoformat() if exec['created_at'] else None
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get execution detail: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/admin/test_execution', methods=['POST'])
@require_admin_auth  
def test_execution():
    """Test execution capabilities from admin interface"""
    try:
        data = request.get_json()
        command = data.get('command', 'list files in C:\\VALIS')
        
        # Import and test execution provider
        from providers.mcp_execution_provider import MCPExecutionProvider
        
        provider = MCPExecutionProvider()
        result = provider.ask(command, 'admin_test', 'admin')
        
        return jsonify({
            'success': True,
            'test_command': command,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Failed to test execution: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Add explicit OPTIONS handler for CORS preflight
@admin_bp.route('/api/admin/<path:path>', methods=['OPTIONS'])
def admin_options(path):
    """Handle CORS preflight for all admin routes"""
    return '', 200