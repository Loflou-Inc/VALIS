"""
VALIS Mr. Fission v2 - Enhanced API Endpoints
Soul Stratification: Layered consciousness construction API
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import uuid
from datetime import datetime
import shutil
from werkzeug.utils import secure_filename

# Import VALIS components
import sys
sys.path.append('C:\\VALIS\\valis2')

# Import new Soul Stratification components
from fission.deep_fusion import DeepFusionEngine, LayeredPersonaBlueprint, DocumentClassifier
from fission.ingestion_utils import IngestionUtils
from memory.db import db

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

# Initialize enhanced engines
deep_fusion = DeepFusionEngine()
ingestion_utils = IngestionUtils()
classifier = DocumentClassifier()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def initialize_database():
    """Initialize database with Soul Stratification schema"""
    try:
        # Run migration script
        migration_path = os.path.join(os.path.dirname(__file__), 'migrations', '001_persona_documents.sql')
        if os.path.exists(migration_path):
            with open(migration_path, 'r') as f:
                migration_sql = f.read()
            
            # Execute migration (split by semicolons for multiple statements)
            statements = migration_sql.split(';')
            for statement in statements:
                if statement.strip():
                    try:
                        db.execute(statement)
                    except Exception as e:
                        # Ignore errors for already existing tables/indexes
                        if 'already exists' not in str(e).lower():
                            print(f"Migration warning: {e}")
            
            print("Database migration completed successfully")
        else:
            print("Migration file not found - creating basic structure")
            
    except Exception as e:
        print(f"Database initialization error: {e}")

# Initialize database on startup
initialize_database()

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "Mr. Fission v2 Soul Stratification Online",
        "version": "2.0",
        "features": ["layered_consciousness", "knowledge_boundaries", "document_store"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/upload')
def upload_interface():
    """Serve the Mr. Fission upload interface"""
    try:
        upload_html_path = os.path.join(os.path.dirname(__file__), 'upload.html')
        return send_file(upload_html_path)
    except Exception as e:
        return jsonify({"error": f"Failed to load upload interface: {str(e)}"}), 500

@app.route('/api/fission/upload', methods=['POST'])
def upload_files():
    """
    Enhanced file upload with document classification and storage
    """
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist('files')
        
        if not files or all(f.filename == '' for f in files):
            return jsonify({"error": "No files selected"}), 400
        
        # Create upload session
        session_id = str(uuid.uuid4())
        persona_id = str(uuid.uuid4())  # Generate persona ID for document linking
        session_dir = os.path.join(UPLOAD_FOLDER, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        uploaded_files = []
        document_ids = []
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
                    
                    # Extract content and classify
                    extraction_result = ingestion_utils.extract_text(filepath)
                    
                    if extraction_result['extraction_status'] == 'success':
                        # Classify document
                        classification = ingestion_utils.classify_document_enhanced(
                            filename, extraction_result['content'], extraction_result['file_type']
                        )
                        
                        # Store document in database
                        doc_id = deep_fusion.store_document(
                            persona_id=persona_id,
                            session_id=session_id,
                            title=filename,
                            content=extraction_result['content'],
                            file_type=extraction_result['file_type'],
                            file_size=extraction_result['file_size']
                        )
                        
                        document_ids.append(doc_id)
                        
                        uploaded_files.append({
                            "filename": filename,
                            "size": extraction_result['file_size'],
                            "path": filepath,
                            "document_id": doc_id,
                            "classification": {
                                "doc_type": classification['doc_type'],
                                "canon_status": classification['canon_status'],
                                "life_phase": classification['life_phase'],
                                "confidence": classification['confidence']
                            },
                            "content_metrics": classification['content_metrics'],
                            "entities_detected": len(sum(classification['entities'].values(), []))
                        })
                    else:
                        errors.append(f"{filename}: {extraction_result['content']}")
                        
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
            "persona_id": persona_id,
            "uploaded_files": uploaded_files,
            "file_count": len(uploaded_files),
            "document_ids": document_ids,
            "errors": errors,
            "next_step": f"/api/fission/fuse/{session_id}",
            "classification_summary": {
                "doc_types": list(set([f['classification']['doc_type'] for f in uploaded_files])),
                "canon_distribution": {
                    status: len([f for f in uploaded_files if f['classification']['canon_status'] == status])
                    for status in ['core', 'secondary', 'noise']
                },
                "life_phases": list(set([f['classification']['life_phase'] for f in uploaded_files if f['classification']['life_phase']]))
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/api/fission/fuse/<session_id>', methods=['POST'])
def fuse_layered_persona(session_id):
    """
    Create layered persona blueprint using Deep Fusion Engine
    """
    try:
        data = request.get_json() or {}
        persona_name = data.get('name', f'persona_{session_id[:8]}')
        
        # Get persona_id from session
        session_dir = os.path.join(UPLOAD_FOLDER, session_id)
        if not os.path.exists(session_dir):
            return jsonify({"error": "Session not found"}), 404
        
        # Find persona_id from documents in this session
        persona_docs = db.query("""
            SELECT DISTINCT persona_id FROM persona_documents 
            WHERE session_id = %s LIMIT 1
        """, (session_id,))
        
        if not persona_docs:
            return jsonify({"error": "No documents found for session"}), 404
        
        persona_id = persona_docs[0]['persona_id']
        
        # Create layered persona blueprint
        blueprint = deep_fusion.fuse_layered_persona(persona_id, persona_name)
        
        # Save blueprint to file
        blueprint_filename = f"{persona_name.lower().replace(' ', '_')}.json"
        blueprint_path = os.path.join(PERSONA_FOLDER, blueprint_filename)
        blueprint.save(blueprint_path)
        
        # Generate enhanced preview
        preview = generate_layered_preview(blueprint)
        
        return jsonify({
            "session_id": session_id,
            "persona_id": persona_id,
            "persona_name": persona_name,
            "fusion_complete": True,
            "blueprint_path": blueprint_path,
            "fusion_metrics": blueprint.schema['fusion_metadata'],
            "preview": preview,
            "knowledge_boundaries": blueprint.schema['knowledge_identity']['knowledge_boundaries'],
            "life_phase_coverage": blueprint.schema['source_documents']['life_phase_coverage'],
            "next_steps": {
                "preview": f"/api/fission/preview/{persona_name}",
                "deploy": f"/api/fission/deploy/{persona_name}",
                "manage_docs": f"/api/fission/documents/{persona_id}"
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Fusion failed: {str(e)}"}), 500

@app.route('/api/fission/preview/<persona_name>', methods=['GET'])
def preview_layered_persona(persona_name):
    """
    Enhanced preview of layered persona with knowledge boundaries
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
        blueprint = LayeredPersonaBlueprint()
        blueprint.schema = blueprint_data
        
        # Generate comprehensive preview
        preview = generate_layered_preview(blueprint)
        
        # Add Faust problem validation
        faust_validation = validate_knowledge_boundaries(blueprint)
        
        return jsonify({
            "persona_name": persona_name,
            "version": blueprint_data.get('version', '2.0'),
            "preview": preview,
            "knowledge_boundaries": blueprint_data['knowledge_identity']['knowledge_boundaries'],
            "narrative_summary": generate_narrative_summary(blueprint_data['narrative_identity']),
            "fusion_metrics": blueprint_data['fusion_metadata'],
            "faust_validation": faust_validation,
            "blueprint": blueprint_data,
            "actions": {
                "refine": f"/api/fission/refine/{persona_name}",
                "add_memory": f"/api/fission/memory/{persona_name}",
                "deploy": f"/api/fission/deploy/{persona_name}",
                "manage_docs": f"/api/fission/documents/{blueprint_data['id']}"
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Preview failed: {str(e)}"}), 500

@app.route('/api/fission/documents/<persona_id>', methods=['GET'])
def get_persona_documents(persona_id):
    """
    Get all documents for a persona with classification details
    """
    try:
        documents = db.query("""
            SELECT id, title, doc_type, canon_status, life_phase, 
                   tags, file_size, created_at, content_hash
            FROM persona_documents 
            WHERE persona_id = %s
            ORDER BY created_at ASC
        """, (persona_id,))
        
        # Organize by type and phase
        organized_docs = {
            'by_type': {},
            'by_phase': {},
            'by_canon': {},
            'summary': {
                'total_count': len(documents),
                'types': set(),
                'phases': set(),
                'canon_statuses': set()
            }
        }
        
        for doc in documents:
            doc_type = doc['doc_type']
            life_phase = doc['life_phase']
            canon_status = doc['canon_status']
            
            # Organize by type
            if doc_type not in organized_docs['by_type']:
                organized_docs['by_type'][doc_type] = []
            organized_docs['by_type'][doc_type].append(doc)
            
            # Organize by phase
            if life_phase:
                if life_phase not in organized_docs['by_phase']:
                    organized_docs['by_phase'][life_phase] = []
                organized_docs['by_phase'][life_phase].append(doc)
            
            # Organize by canon status
            if canon_status not in organized_docs['by_canon']:
                organized_docs['by_canon'][canon_status] = []
            organized_docs['by_canon'][canon_status].append(doc)
            
            # Update summary
            organized_docs['summary']['types'].add(doc_type)
            if life_phase:
                organized_docs['summary']['phases'].add(life_phase)
            organized_docs['summary']['canon_statuses'].add(canon_status)
        
        # Convert sets to lists for JSON serialization
        organized_docs['summary']['types'] = list(organized_docs['summary']['types'])
        organized_docs['summary']['phases'] = list(organized_docs['summary']['phases'])
        organized_docs['summary']['canon_statuses'] = list(organized_docs['summary']['canon_statuses'])
        
        return jsonify({
            "persona_id": persona_id,
            "documents": organized_docs,
            "raw_documents": documents
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get documents: {str(e)}"}), 500

@app.route('/api/fission/documents/<doc_id>/reclassify', methods=['POST'])
def reclassify_document(doc_id):
    """
    Manually reclassify a document's type, canon status, or life phase
    """
    try:
        data = request.get_json()
        
        updates = {}
        if 'doc_type' in data:
            updates['doc_type'] = data['doc_type']
        if 'canon_status' in data:
            updates['canon_status'] = data['canon_status']
        if 'life_phase' in data:
            updates['life_phase'] = data['life_phase']
        if 'tags' in data:
            updates['tags'] = json.dumps(data['tags'])
        
        if not updates:
            return jsonify({"error": "No classification updates provided"}), 400
        
        # Update document
        set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
        values = list(updates.values()) + [doc_id]
        
        db.execute(f"""
            UPDATE persona_documents 
            SET {set_clause}, processed_timestamp = %s
            WHERE id = %s
        """, values + [datetime.now()])
        
        # Get updated document
        updated_doc = db.query("""
            SELECT * FROM persona_documents WHERE id = %s
        """, (doc_id,))
        
        if not updated_doc:
            return jsonify({"error": "Document not found"}), 404
        
        return jsonify({
            "document_id": doc_id,
            "updated": True,
            "new_classification": {
                "doc_type": updated_doc[0]['doc_type'],
                "canon_status": updated_doc[0]['canon_status'],
                "life_phase": updated_doc[0]['life_phase']
            },
            "message": "Document reclassified successfully"
        })
        
    except Exception as e:
        return jsonify({"error": f"Reclassification failed: {str(e)}"}), 500
def generate_layered_preview(blueprint: LayeredPersonaBlueprint) -> Dict[str, Any]:
    """
    Generate comprehensive preview of layered persona
    """
    schema = blueprint.schema
    
    # Extract key information
    narrative = schema['narrative_identity']
    knowledge = schema['knowledge_identity']
    traits = schema['personality_traits']
    
    # Generate narrative summary
    life_events = []
    for phase, data in narrative['life_phases'].items():
        if data['events']:
            life_events.extend([f"{phase}: {event}" for event in data['events'][:2]])
    
    # Generate knowledge summary
    education_summary = []
    if knowledge['formal_education']['degrees']:
        education_summary = knowledge['formal_education']['degrees'][:3]
    
    career_summary = []
    if knowledge['professional_experience']['positions']:
        career_summary = knowledge['professional_experience']['positions'][:3]
    
    # Generate trait summary
    big_five_summary = {
        trait: f"{value:.1f}/1.0" 
        for trait, value in traits['big_five'].items() 
        if value != 0.5  # Only show non-neutral traits
    }
    
    return {
        "identity_layers": {
            "narrative": {
                "core_narratives": narrative['core_narratives'][:3],
                "life_events": life_events[:5],
                "personality_development": narrative['personality_development']['defining_moments'][:3]
            },
            "knowledge": {
                "education": education_summary,
                "career": career_summary,
                "expertise_areas": knowledge['knowledge_boundaries']['deep_expertise'][:5],
                "known_limitations": knowledge['knowledge_boundaries']['unknown_domains'][:5]
            }
        },
        "personality_profile": {
            "big_five_highlights": big_five_summary,
            "communication_style": traits['communication_style'],
            "primary_archetype": schema['archetypes']['primary'],
            "secondary_archetypes": schema['archetypes']['secondary'][:2]
        },
        "data_quality": {
            "fusion_confidence": schema['fusion_metadata']['fusion_confidence'],
            "knowledge_completeness": schema['fusion_metadata']['knowledge_completeness'],
            "narrative_coherence": schema['fusion_metadata']['narrative_coherence'],
            "boundary_clarity": schema['fusion_metadata']['boundary_clarity']
        },
        "source_coverage": {
            "total_documents": schema['source_documents']['total_count'],
            "document_types": schema['source_documents']['by_type'],
            "life_phases_covered": schema['source_documents']['life_phase_coverage'],
            "canon_distribution": schema['source_documents']['canon_distribution']
        }
    }

def generate_narrative_summary(narrative_identity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate summary of narrative identity across life phases
    """
    phases = narrative_identity['life_phases']
    
    # Count events and themes across phases
    total_events = sum(len(phase_data['events']) for phase_data in phases.values())
    all_themes = []
    
    for phase_data in phases.values():
        all_themes.extend(phase_data['themes'])
    
    # Find most common themes
    from collections import Counter
    theme_counts = Counter(all_themes)
    
    return {
        "life_phases_documented": [phase for phase, data in phases.items() if data['events']],
        "total_life_events": total_events,
        "dominant_themes": [theme for theme, count in theme_counts.most_common(5)],
        "core_narratives": narrative_identity['core_narratives'],
        "symbolic_memories_count": len(narrative_identity['symbolic_memories']),
        "defining_moments_count": len(narrative_identity['personality_development']['defining_moments'])
    }

def validate_knowledge_boundaries(blueprint: LayeredPersonaBlueprint) -> Dict[str, Any]:
    """
    Validate knowledge boundaries to solve Faust problem
    """
    knowledge_bounds = blueprint.schema['knowledge_identity']['knowledge_boundaries']
    
    validation = {
        "faust_problem_addressed": True,
        "knowledge_boundary_score": 0.0,
        "validation_checks": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Check if deep expertise is defined
    if knowledge_bounds['deep_expertise']:
        validation['validation_checks'].append("✓ Deep expertise areas defined")
        validation['knowledge_boundary_score'] += 0.3
    else:
        validation['warnings'].append("No deep expertise areas defined")
        validation['faust_problem_addressed'] = False
    
    # Check if unknown domains are specified
    if knowledge_bounds['unknown_domains']:
        validation['validation_checks'].append("✓ Unknown domains explicitly marked")
        validation['knowledge_boundary_score'] += 0.3
    else:
        validation['warnings'].append("Unknown domains not specified")
    
    # Check for surface knowledge distinction
    if knowledge_bounds['surface_knowledge']:
        validation['validation_checks'].append("✓ Surface knowledge distinguished from deep expertise")
        validation['knowledge_boundary_score'] += 0.2
    
    # Check learning style
    if knowledge_bounds['learning_style']:
        validation['validation_checks'].append("✓ Learning style identified")
        validation['knowledge_boundary_score'] += 0.2
    
    # Generate recommendations
    if validation['knowledge_boundary_score'] < 0.7:
        validation['recommendations'].append("Add more educational/career documents to strengthen knowledge boundaries")
    
    if not knowledge_bounds['unknown_domains']:
        validation['recommendations'].append("Explicitly define what the persona does NOT know to prevent Faust problem")
    
    return validation

@app.route('/api/fission/validate/<persona_name>', methods=['GET'])
def validate_persona_boundaries(persona_name):
    """
    Validate persona knowledge boundaries (Faust problem check)
    """
    try:
        blueprint_filename = f"{persona_name.lower().replace(' ', '_')}.json"
        blueprint_path = os.path.join(PERSONA_FOLDER, blueprint_filename)
        
        if not os.path.exists(blueprint_path):
            return jsonify({"error": "Persona not found"}), 404
        
        with open(blueprint_path, 'r', encoding='utf-8') as f:
            blueprint_data = json.load(f)
        
        blueprint = LayeredPersonaBlueprint()
        blueprint.schema = blueprint_data
        
        validation = validate_knowledge_boundaries(blueprint)
        
        return jsonify({
            "persona_name": persona_name,
            "validation_results": validation,
            "knowledge_profile": blueprint_data['knowledge_identity']['knowledge_boundaries'],
            "recommendations": blueprint_data['fusion_metadata']['recommendations']
        })
        
    except Exception as e:
        return jsonify({"error": f"Validation failed: {str(e)}"}), 500

@app.route('/api/fission/deploy/<persona_name>', methods=['POST'])
def deploy_layered_persona(persona_name):
    """
    Deploy layered persona to VALIS runtime with knowledge boundaries
    """
    try:
        blueprint_filename = f"{persona_name.lower().replace(' ', '_')}.json"
        blueprint_path = os.path.join(PERSONA_FOLDER, blueprint_filename)
        
        if not os.path.exists(blueprint_path):
            return jsonify({"error": "Persona not found"}), 404
        
        with open(blueprint_path, 'r', encoding='utf-8') as f:
            blueprint_data = json.load(f)
        
        # Validate knowledge boundaries before deployment
        blueprint = LayeredPersonaBlueprint()
        blueprint.schema = blueprint_data
        validation = validate_knowledge_boundaries(blueprint)
        
        if not validation['faust_problem_addressed']:
            return jsonify({
                "error": "Cannot deploy persona with insufficient knowledge boundaries",
                "validation_results": validation,
                "message": "Faust problem not addressed - persona needs better knowledge boundary definition"
            }), 400
        
        # TODO: Integrate with VALIS runtime deployment
        # This would connect to the vault system and VALIS main database
        
        return jsonify({
            "persona_name": persona_name,
            "deployment_status": "ready_for_valis",
            "blueprint_path": blueprint_path,
            "validation_passed": True,
            "knowledge_boundaries_enforced": True,
            "deployment_details": {
                "fusion_confidence": blueprint_data['fusion_metadata']['fusion_confidence'],
                "knowledge_completeness": blueprint_data['fusion_metadata']['knowledge_completeness'],
                "boundary_clarity": blueprint_data['fusion_metadata']['boundary_clarity']
            },
            "message": "Layered persona ready for VALIS deployment with enforced knowledge boundaries"
        })
        
    except Exception as e:
        return jsonify({"error": f"Deployment failed: {str(e)}"}), 500

@app.route('/api/fission/stats', methods=['GET'])
def get_fission_stats():
    """
    Get Mr. Fission system statistics
    """
    try:
        # Document store stats
        doc_stats = db.query("""
            SELECT 
                COUNT(*) as total_documents,
                COUNT(DISTINCT persona_id) as total_personas,
                COUNT(DISTINCT session_id) as total_sessions
            FROM persona_documents
        """)[0]
        
        # Document type distribution
        type_distribution = db.query("""
            SELECT doc_type, COUNT(*) as count
            FROM persona_documents
            GROUP BY doc_type
            ORDER BY count DESC
        """)
        
        # Canon status distribution
        canon_distribution = db.query("""
            SELECT canon_status, COUNT(*) as count
            FROM persona_documents
            GROUP BY canon_status
            ORDER BY count DESC
        """)
        
        # Life phase coverage
        phase_coverage = db.query("""
            SELECT life_phase, COUNT(*) as count
            FROM persona_documents
            WHERE life_phase IS NOT NULL
            GROUP BY life_phase
            ORDER BY count DESC
        """)
        
        return jsonify({
            "system_version": "2.0 - Soul Stratification",
            "document_store": {
                "total_documents": doc_stats['total_documents'],
                "total_personas": doc_stats['total_personas'],
                "total_sessions": doc_stats['total_sessions']
            },
            "document_distribution": {
                "by_type": {row['doc_type']: row['count'] for row in type_distribution},
                "by_canon": {row['canon_status']: row['count'] for row in canon_distribution},
                "by_phase": {row['life_phase']: row['count'] for row in phase_coverage}
            },
            "features": [
                "layered_consciousness_construction",
                "knowledge_boundary_enforcement", 
                "faust_problem_prevention",
                "document_classification",
                "life_phase_mapping",
                "canon_status_tracking"
            ]
        })
        
    except Exception as e:
        return jsonify({"error": f"Stats failed: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("=== VALIS MR. FISSION v2 - SOUL STRATIFICATION STARTING ===")
    print("Layered Consciousness Constructor Online")
    print("Features: Knowledge Boundaries, Document Store, Faust Problem Prevention")
    print("Supported file types:", ALLOWED_EXTENSIONS)
    print("Upload limit:", MAX_FILE_SIZE // (1024*1024), "MB")
    print("\nAPI Endpoints:")
    print("  POST /api/fission/upload - Upload and classify documents")
    print("  POST /api/fission/fuse/<session_id> - Create layered persona")
    print("  GET  /api/fission/preview/<persona_name> - Preview with knowledge boundaries")
    print("  GET  /api/fission/documents/<persona_id> - Manage persona documents")
    print("  POST /api/fission/documents/<doc_id>/reclassify - Reclassify documents")
    print("  GET  /api/fission/validate/<persona_name> - Validate knowledge boundaries")
    print("  POST /api/fission/deploy/<persona_name> - Deploy with boundary enforcement")
    print("  GET  /api/fission/stats - System statistics")
    print("=== SOUL STRATIFICATION ENGINE READY ===")
    
    app.run(host='0.0.0.0', port=8001, debug=True)
