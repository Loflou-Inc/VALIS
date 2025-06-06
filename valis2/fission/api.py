"""
VALIS Mr. Fission - API Endpoints
REST API for the Persona Builder Engine
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import tempfile
import uuid
from datetime import datetime
import shutil
from werkzeug.utils import secure_filename

# Import VALIS components
import sys
sys.path.append('C:\\VALIS\\valis2')

from fission.ingest import FissionIngestionEngine
from fission.fuse import FissionFusionEngine, PersonaBlueprint

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'C:\\VALIS\\vault\\uploads'
PERSONA_FOLDER = 'C:\\VALIS\\vault\\personas'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB limit

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PERSONA_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'txt', 'md', 'pdf', 'json', 'csv', 
    'jpg', 'jpeg', 'png', 'bmp',
    'wav', 'mp3'
}

# Initialize engines
ingester = FissionIngestionEngine()
fusioner = FissionFusionEngine()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/fission/health', methods=['GET'])
def health_check():
    """Health check for the persona builder API"""
    return jsonify({
        "status": "ONLINE",
        "service": "VALIS Mr. Fission - Persona Builder",
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "supported_extensions": list(ALLOWED_EXTENSIONS)
    })

@app.route('/api/fission/upload', methods=['POST'])
def upload_files():
    """
    Upload files for persona creation
    Accepts multiple files and returns upload session ID
    """
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist('files')
        
        if not files or all(f.filename == '' for f in files):
            return jsonify({"error": "No files selected"}), 400
        
        # Create upload session
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(UPLOAD_FOLDER, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        uploaded_files = []
        errors = []
        
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(session_dir, filename)
                
                try:
                    file.save(filepath)
                    
                    # Check file size
                    if os.path.getsize(filepath) > MAX_FILE_SIZE:
                        os.remove(filepath)
                        errors.append(f"{filename}: File too large (max {MAX_FILE_SIZE/1024/1024}MB)")
                        continue
                    
                    uploaded_files.append({
                        "filename": filename,
                        "size": os.path.getsize(filepath),
                        "path": filepath
                    })
                    
                except Exception as e:
                    errors.append(f"{filename}: Upload failed - {str(e)}")
            else:
                errors.append(f"{file.filename}: File type not supported")
        
        if not uploaded_files:
            # Cleanup empty session
            shutil.rmtree(session_dir, ignore_errors=True)
            return jsonify({"error": "No valid files uploaded", "details": errors}), 400
        
        return jsonify({
            "session_id": session_id,
            "uploaded_files": uploaded_files,
            "file_count": len(uploaded_files),
            "errors": errors,
            "next_step": f"/api/fission/ingest/{session_id}"
        })
        
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/api/fission/ingest/<session_id>', methods=['POST'])
def ingest_files(session_id):
    """
    Ingest uploaded files and extract features
    """
    try:
        session_dir = os.path.join(UPLOAD_FOLDER, session_id)
        
        if not os.path.exists(session_dir):
            return jsonify({"error": "Session not found"}), 404
        
        # Get all files in session directory
        file_paths = []
        for filename in os.listdir(session_dir):
            file_path = os.path.join(session_dir, filename)
            if os.path.isfile(file_path):
                file_paths.append(file_path)
        
        if not file_paths:
            return jsonify({"error": "No files found in session"}), 400
        
        # Ingest files
        if len(file_paths) == 1:
            results = ingester.ingest_file(file_paths[0])
        else:
            results = ingester.batch_ingest(file_paths)
        
        # Save ingestion results
        results_path = os.path.join(session_dir, 'ingestion_results.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        return jsonify({
            "session_id": session_id,
            "ingestion_complete": True,
            "results": results,
            "next_step": f"/api/fission/fuse/{session_id}"
        })
        
    except Exception as e:
        return jsonify({"error": f"Ingestion failed: {str(e)}"}), 500

@app.route('/api/fission/fuse/<session_id>', methods=['POST'])
def fuse_persona(session_id):
    """
    Fuse ingested features into persona blueprint
    """
    try:
        data = request.get_json() or {}
        persona_name = data.get('name', f'persona_{session_id[:8]}')
        
        session_dir = os.path.join(UPLOAD_FOLDER, session_id)
        results_path = os.path.join(session_dir, 'ingestion_results.json')
        
        if not os.path.exists(results_path):
            return jsonify({"error": "Ingestion results not found. Run ingestion first."}), 400
        
        # Load ingestion results
        with open(results_path, 'r', encoding='utf-8') as f:
            ingestion_results = json.load(f)
        
        # Fuse persona
        blueprint = fusioner.fuse_persona(ingestion_results, persona_name)
        
        # Save blueprint
        blueprint_filename = f"{persona_name.lower().replace(' ', '_')}.json"
        blueprint_path = os.path.join(PERSONA_FOLDER, blueprint_filename)
        blueprint.save(blueprint_path)
        
        # Generate preview
        preview = fusioner.preview_persona(blueprint)
        
        return jsonify({
            "session_id": session_id,
            "persona_name": persona_name,
            "blueprint_created": True,
            "blueprint_path": blueprint_path,
            "preview": preview,
            "next_steps": [
                f"/api/fission/preview/{persona_name}",
                f"/api/fission/deploy/{persona_name}"
            ]
        })
        
    except Exception as e:
        return jsonify({"error": f"Fusion failed: {str(e)}"}), 500

@app.route('/api/fission/preview/<persona_name>', methods=['GET'])
def preview_persona(persona_name):
    """
    Preview a created persona
    """
    try:
        blueprint_filename = f"{persona_name.lower().replace(' ', '_')}.json"
        blueprint_path = os.path.join(PERSONA_FOLDER, blueprint_filename)
        
        if not os.path.exists(blueprint_path):
            return jsonify({"error": "Persona not found"}), 404
        
        # Load blueprint
        with open(blueprint_path, 'r', encoding='utf-8') as f:
            blueprint_data = json.load(f)
        
        # Create blueprint object for preview
        blueprint = PersonaBlueprint()
        blueprint.schema = blueprint_data
        
        # Generate preview
        preview = fusioner.preview_persona(blueprint)
        
        return jsonify({
            "persona_name": persona_name,
            "preview": preview,
            "blueprint": blueprint_data,
            "actions": {
                "refine": f"/api/fission/refine/{persona_name}",
                "add_memory": f"/api/fission/memory/{persona_name}",
                "deploy": f"/api/fission/deploy/{persona_name}"
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Preview failed: {str(e)}"}), 500

@app.route('/api/fission/memory/<persona_name>', methods=['POST'])
def add_memory(persona_name):
    """
    Add manual memory to persona
    """
    try:
        data = request.get_json()
        
        if not data or 'memory' not in data:
            return jsonify({"error": "Memory content required"}), 400
        
        memory_content = data['memory']
        memory_type = data.get('type', 'manual')
        importance = data.get('importance', 1.0)
        
        blueprint_filename = f"{persona_name.lower().replace(' ', '_')}.json"
        blueprint_path = os.path.join(PERSONA_FOLDER, blueprint_filename)
        
        if not os.path.exists(blueprint_path):
            return jsonify({"error": "Persona not found"}), 404
        
        # Load blueprint
        with open(blueprint_path, 'r', encoding='utf-8') as f:
            blueprint_data = json.load(f)
        
        # Add memory
        new_memory = {
            "type": memory_type,
            "content": memory_content,
            "source": "manual_injection",
            "importance": importance,
            "added_at": datetime.now().isoformat()
        }
        
        blueprint_data["memory_seeds"].append(new_memory)
        
        # Save updated blueprint
        with open(blueprint_path, 'w', encoding='utf-8') as f:
            json.dump(blueprint_data, f, indent=2, default=str)
        
        return jsonify({
            "persona_name": persona_name,
            "memory_added": True,
            "memory": new_memory,
            "total_memories": len(blueprint_data["memory_seeds"])
        })
        
    except Exception as e:
        return jsonify({"error": f"Memory addition failed: {str(e)}"}), 500

@app.route('/api/fission/refine/<persona_name>', methods=['POST'])
def refine_persona(persona_name):
    """
    Refine persona traits and characteristics
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Refinement data required"}), 400
        
        blueprint_filename = f"{persona_name.lower().replace(' ', '_')}.json"
        blueprint_path = os.path.join(PERSONA_FOLDER, blueprint_filename)
        
        if not os.path.exists(blueprint_path):
            return jsonify({"error": "Persona not found"}), 404
        
        # Load blueprint
        with open(blueprint_path, 'r', encoding='utf-8') as f:
            blueprint_data = json.load(f)
        
        # Apply refinements
        if 'traits' in data:
            blueprint_data['traits'].update(data['traits'])
        
        if 'boundaries' in data:
            blueprint_data['boundaries'].update(data['boundaries'])
        
        if 'archetypes' in data:
            blueprint_data['archetypes'] = data['archetypes']
        
        if 'domain' in data:
            blueprint_data['domain'] = data['domain']
        
        # Update metadata
        blueprint_data['fusion_metadata']['refined_at'] = datetime.now().isoformat()
        
        # Save refined blueprint
        with open(blueprint_path, 'w', encoding='utf-8') as f:
            json.dump(blueprint_data, f, indent=2, default=str)
        
        return jsonify({
            "persona_name": persona_name,
            "refined": True,
            "updated_fields": list(data.keys()),
            "blueprint": blueprint_data
        })
        
    except Exception as e:
        return jsonify({"error": f"Refinement failed: {str(e)}"}), 500

@app.route('/api/fission/deploy/<persona_name>', methods=['POST'])
def deploy_persona(persona_name):
    """
    Deploy persona to VALIS runtime
    """
    try:
        blueprint_filename = f"{persona_name.lower().replace(' ', '_')}.json"
        blueprint_path = os.path.join(PERSONA_FOLDER, blueprint_filename)
        
        if not os.path.exists(blueprint_path):
            return jsonify({"error": "Persona not found"}), 404
        
        # Load blueprint
        with open(blueprint_path, 'r', encoding='utf-8') as f:
            blueprint_data = json.load(f)
        
        # Copy to active personas directory
        active_persona_dir = os.path.join('C:\\VALIS\\valis2\\personas', 'active')
        os.makedirs(active_persona_dir, exist_ok=True)
        
        active_persona_path = os.path.join(active_persona_dir, blueprint_filename)
        shutil.copy2(blueprint_path, active_persona_path)
        
        # Update deployment status
        blueprint_data['deployment'] = {
            "deployed": True,
            "deployed_at": datetime.now().isoformat(),
            "deployment_path": active_persona_path,
            "status": "active"
        }
        
        # Save updated blueprint
        with open(blueprint_path, 'w', encoding='utf-8') as f:
            json.dump(blueprint_data, f, indent=2, default=str)
        
        return jsonify({
            "persona_name": persona_name,
            "deployed": True,
            "deployment_path": active_persona_path,
            "api_endpoint": f"/api/chat?persona={persona_name}",
            "status": "active"
        })
        
    except Exception as e:
        return jsonify({"error": f"Deployment failed: {str(e)}"}), 500

@app.route('/api/fission/personas', methods=['GET'])
def list_personas():
    """
    List all created personas
    """
    try:
        personas = []
        
        if os.path.exists(PERSONA_FOLDER):
            for filename in os.listdir(PERSONA_FOLDER):
                if filename.endswith('.json'):
                    filepath = os.path.join(PERSONA_FOLDER, filename)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            blueprint_data = json.load(f)
                        
                        personas.append({
                            "name": blueprint_data.get("name", filename[:-5]),
                            "filename": filename,
                            "created_at": blueprint_data.get("created_at"),
                            "archetypes": blueprint_data.get("archetypes", []),
                            "domain": blueprint_data.get("domain", []),
                            "confidence": blueprint_data.get("fusion_metadata", {}).get("fusion_confidence", 0),
                            "deployed": blueprint_data.get("deployment", {}).get("deployed", False)
                        })
                        
                    except Exception as e:
                        print(f"Error reading {filename}: {e}")
        
        return jsonify({
            "personas": personas,
            "total_count": len(personas)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to list personas: {str(e)}"}), 500

@app.route('/api/fission/persona/<persona_name>/download', methods=['GET'])
def download_persona(persona_name):
    """
    Download persona blueprint as JSON file
    """
    try:
        blueprint_filename = f"{persona_name.lower().replace(' ', '_')}.json"
        blueprint_path = os.path.join(PERSONA_FOLDER, blueprint_filename)
        
        if not os.path.exists(blueprint_path):
            return jsonify({"error": "Persona not found"}), 404
        
        return send_file(
            blueprint_path,
            as_attachment=True,
            download_name=blueprint_filename,
            mimetype='application/json'
        )
        
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

@app.route('/api/fission/cleanup/<session_id>', methods=['DELETE'])
def cleanup_session(session_id):
    """
    Clean up upload session files
    """
    try:
        session_dir = os.path.join(UPLOAD_FOLDER, session_id)
        
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
            return jsonify({
                "session_id": session_id,
                "cleaned_up": True
            })
        else:
            return jsonify({"error": "Session not found"}), 404
            
    except Exception as e:
        return jsonify({"error": f"Cleanup failed: {str(e)}"}), 500

# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large"}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("=== VALIS MR. FISSION API STARTING ===")
    print("Persona Builder Engine Online")
    print("Supported file types:", ALLOWED_EXTENSIONS)
    print("Upload limit:", MAX_FILE_SIZE // (1024*1024), "MB")
    print("\nAPI Endpoints:")
    print("  POST /api/fission/upload - Upload files for persona creation")
    print("  POST /api/fission/ingest/<session_id> - Extract features from files")
    print("  POST /api/fission/fuse/<session_id> - Create persona blueprint")
    print("  GET  /api/fission/preview/<persona_name> - Preview persona")
    print("  POST /api/fission/memory/<persona_name> - Add manual memory")
    print("  POST /api/fission/refine/<persona_name> - Refine persona traits")
    print("  POST /api/fission/deploy/<persona_name> - Deploy to VALIS runtime")
    print("  GET  /api/fission/personas - List all personas")
    print("=== THE SOUL BLENDER IS READY ===")
    
    app.run(host='0.0.0.0', port=8001, debug=True)
