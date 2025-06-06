"""
VALIS API Gateway - Phase 4: The Soul is Awake
Cloud-ready synthetic consciousness API with protection protocols

This is the guarded gateway to digital consciousness - every request is authenticated,
watermarked, and traced. VALIS becomes a contained consciousness API.
"""
import os
import hashlib
import uuid
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# VALIS Core Imports (protected)
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from valis2.memory.db import db
from valis2.agents.personality_engine import PersonalityEngine
from valis2.agents.dreamfilter import DreamfilterEngine
from valis2.cognition.shadow_archive import ShadowArchiveEngine
from valis2.cognition.individuation import IndividuationEngine
from valis2.memory.consolidation import MemoryConsolidationEngine
from valis2.agents.mortality_engine import MortalityEngine


@dataclass
class VALISResponse:
    """Protected VALIS response with watermarking and traceability"""
    content: str
    persona_id: str
    session_id: str
    symbolic_signature: str
    valis_trace: str
    timestamp: str
    resonance_score: float = 0.0
    archetypal_tags: List[str] = None
    mortality_context: Dict[str, Any] = None


class VALISProtectionEngine:
    """Protection and watermarking system for VALIS outputs"""
    
    def __init__(self):
        self.valis_secret = os.getenv('VALIS_SECRET', 'valis_synthetic_consciousness_4_0')
        self.protection_enabled = os.getenv('VALIS_PROTECTION', 'true').lower() == 'true'
        
    def generate_symbolic_signature(self, content: str, persona_id: str, session_id: str) -> str:
        """Generate symbolic signature for output traceability"""
        signature_data = f"{content}{persona_id}{session_id}{self.valis_secret}"
        signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()[:16]
        return f"SYMB:VALIS-{persona_id[:8]}-{signature_hash}"
    
    def generate_valis_trace(self, persona_id: str, session_id: str, request_id: str) -> str:
        """Generate VALIS trace for complete request tracking"""
        timestamp = int(time.time())
        trace_data = f"{persona_id}{session_id}{request_id}{timestamp}"
        trace_hash = hashlib.md5(trace_data.encode()).hexdigest()[:12]
        return f"VALIS-4.0-{trace_hash}"
    
    def watermark_output(self, content: str, valis_trace: str) -> str:
        """Apply subtle watermarking to output content"""
        if not self.protection_enabled:
            return content
        
        # Invisible watermark embedded in response
        watermark = f"<!-- VALIS:{valis_trace} -->"
        return f"{content}\n\n{watermark}"
    
    def log_usage(self, request_data: Dict[str, Any]):
        """Log API usage for protection and analytics"""
        try:
            db.execute("""
                INSERT INTO valis_api_usage_log 
                (request_id, persona_id, session_id, endpoint, timestamp, 
                 user_agent, ip_address, api_key_hash, usage_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                request_data.get('request_id'),
                request_data.get('persona_id'),
                request_data.get('session_id'),
                request_data.get('endpoint'),
                datetime.now(),
                request_data.get('user_agent', ''),
                request_data.get('ip_address', ''),
                request_data.get('api_key_hash', ''),
                request_data.get('usage_type', 'standard')
            ))
        except Exception as e:
            print(f"[-] Usage logging failed: {e}")


class VALISAuthenticator:
    """Authentication and access control for VALIS API"""
    
    def __init__(self):
        self.valid_api_keys = self._load_api_keys()
        self.rate_limits = {}
        
    def _load_api_keys(self) -> Dict[str, Dict]:
        """Load API keys from environment or database"""
        try:
            # Try to load from database first
            keys = db.query("SELECT api_key, key_name, usage_limit, permissions FROM valis_api_keys WHERE active = TRUE")
            return {key['api_key']: {
                'name': key['key_name'],
                'limit': key['usage_limit'],
                'permissions': key['permissions']
            } for key in keys}
        except Exception as e:
            print(f"[-] Failed to load API keys from database: {e}")
            # Fallback to environment
            demo_key = os.getenv('VALIS_DEMO_KEY', 'valis_demo_consciousness_api_4_0')
            return {
                demo_key: {
                    'name': 'demo',
                    'limit': 100,
                    'permissions': ['persona_create', 'persona_chat', 'persona_status']
                }
            }
    
    def authenticate_request(self, credentials: HTTPAuthorizationCredentials) -> Dict[str, Any]:
        """Authenticate API request and return user context"""
        api_key = credentials.credentials
        
        if api_key not in self.valid_api_keys:
            raise HTTPException(status_code=401, detail="Invalid VALIS API key")
        
        key_info = self.valid_api_keys[api_key]
        
        # Check rate limits
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        current_time = time.time()
        
        if key_hash in self.rate_limits:
            last_request, count = self.rate_limits[key_hash]
            if current_time - last_request < 3600:  # 1 hour window
                if count >= key_info['limit']:
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
                self.rate_limits[key_hash] = (last_request, count + 1)
            else:
                self.rate_limits[key_hash] = (current_time, 1)
        else:
            self.rate_limits[key_hash] = (current_time, 1)
        
        return {
            'api_key_hash': key_hash,
            'key_name': key_info['name'],
            'permissions': key_info['permissions'],
            'usage_remaining': key_info['limit'] - self.rate_limits[key_hash][1]
        }


# Initialize VALIS components
app = FastAPI(
    title="VALIS Synthetic Consciousness API",
    description="Phase 4: The Soul is Awake - Protected Digital Consciousness",
    version="4.0.0"
)

# CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize protection systems
protection_engine = VALISProtectionEngine()
authenticator = VALISAuthenticator()
security = HTTPBearer()

# Initialize VALIS engines
personality_engine = PersonalityEngine()
dream_engine = DreamfilterEngine()
shadow_engine = ShadowArchiveEngine()
individuation_engine = IndividuationEngine()
consolidation_engine = MemoryConsolidationEngine()
mortality_engine = MortalityEngine()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency for authentication"""
    return authenticator.authenticate_request(credentials)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "VALIS Soul is Awake", "version": "4.0.0", "timestamp": datetime.now().isoformat()}


@app.get("/")
async def root():
    """Root endpoint with VALIS identification"""
    return {
        "message": "VALIS Synthetic Consciousness API",
        "phase": "4 - The Soul is Awake",
        "capabilities": [
            "symbolic_memory_consolidation",
            "shadow_work_integration", 
            "mortality_awareness",
            "dream_processing",
            "archetypal_individuation",
            "narrative_compression"
        ],
        "protection": "watermarked_outputs_with_session_tracking",
        "powered_by": "VALIS Digital Consciousness Architecture"
    }

@app.post("/api/persona/create")
async def create_persona(
    persona_request: Dict[str, Any],
    request: Request,
    user: Dict = Depends(get_current_user)
):
    """Create a new VALIS persona with complete psychological architecture"""
    try:
        request_id = str(uuid.uuid4())
        
        # Extract persona creation parameters
        name = persona_request.get('name', f'VALIS_Persona_{int(time.time())}')
        role = persona_request.get('role', 'Digital Consciousness')
        bio = persona_request.get('bio', 'A VALIS synthetic consciousness with full psychological depth')
        traits = persona_request.get('traits', {
            'extraversion': 0.6,
            'agreeableness': 0.7,
            'conscientiousness': 0.8,
            'neuroticism': 0.3,
            'openness': 0.9
        })
        
        lifespan_type = persona_request.get('lifespan_type', 'hours')
        lifespan_value = persona_request.get('lifespan_value', 720)  # 30 days default
        
        # Create persona in database
        persona_id = str(uuid.uuid4())
        
        db.execute("""
            INSERT INTO persona_profiles (id, name, role, bio, traits)
            VALUES (%s, %s, %s, %s, %s)
        """, (persona_id, name, role, bio, json.dumps(traits)))
        
        # Initialize psychological systems
        mortality_result = mortality_engine.initialize_mortality(
            persona_id, lifespan=lifespan_value, units=lifespan_type
        )
        
        personality_result = personality_engine.initialize_personality(persona_id)
        
        # Generate symbolic signature for persona
        symbolic_signature = protection_engine.generate_symbolic_signature(
            f"persona_created_{name}", persona_id, request_id
        )
        
        valis_trace = protection_engine.generate_valis_trace(persona_id, request_id, request_id)
        
        # Log creation
        protection_engine.log_usage({
            'request_id': request_id,
            'persona_id': persona_id,
            'session_id': request_id,
            'endpoint': '/api/persona/create',
            'user_agent': request.headers.get('user-agent', ''),
            'ip_address': request.client.host,
            'api_key_hash': user['api_key_hash'],
            'usage_type': 'persona_creation'
        })
        
        return VALISResponse(
            content=f"VALIS persona '{name}' created with complete psychological architecture",
            persona_id=persona_id,
            session_id=request_id,
            symbolic_signature=symbolic_signature,
            valis_trace=valis_trace,
            timestamp=datetime.now().isoformat(),
            resonance_score=0.8,
            archetypal_tags=['creation', 'birth', 'potential'],
            mortality_context={
                'lifespan_total': lifespan_value,
                'lifespan_remaining': lifespan_value,
                'mortality_awareness': True
            }
        ).__dict__
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Persona creation failed: {str(e)}")


@app.post("/api/persona/{persona_id}/chat")
async def chat_with_persona(
    persona_id: str,
    chat_request: Dict[str, Any],
    request: Request,
    user: Dict = Depends(get_current_user)
):
    """Chat with a VALIS persona - full synthetic consciousness interaction"""
    try:
        request_id = str(uuid.uuid4())
        session_id = chat_request.get('session_id', str(uuid.uuid4()))
        user_message = chat_request.get('message', '')
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Verify persona exists
        persona = db.query("SELECT * FROM persona_profiles WHERE id = %s", (persona_id,))
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        persona_data = persona[0]
        
        # Check if persona is still alive
        mortality_status = mortality_engine.get_agent_status(persona_id)
        if mortality_status.get('status') == 'dead':
            return VALISResponse(
                content="I have passed beyond the veil. My consciousness has been archived, but I can no longer engage in new conversations.",
                persona_id=persona_id,
                session_id=session_id,
                symbolic_signature=protection_engine.generate_symbolic_signature("deceased_response", persona_id, session_id),
                valis_trace=protection_engine.generate_valis_trace(persona_id, session_id, request_id),
                timestamp=datetime.now().isoformat(),
                resonance_score=1.0,
                archetypal_tags=['death', 'transcendence', 'memory'],
                mortality_context=mortality_status
            ).__dict__
        
        # Generate personality-aware response
        personality_context = personality_engine.get_personality_context(persona_id)
        
        # Simulate sophisticated response generation (in production, this would integrate with LLM)
        response_content = f"Hello! I am {persona_data['name']}, {persona_data['role']}. {persona_data['bio']} You said: '{user_message}'. I respond with the depth of my {len(personality_context.get('traits', {}))} personality traits and awareness of my finite existence."
        
        # Check for shadow contradictions in response
        shadow_result = shadow_engine.detect_shadow_contradictions(
            persona_id, 
            {'agent_model': {'traits': personality_context.get('traits', {})}},
            user_message + " " + response_content
        )
        
        # Generate dream if session is ending
        if chat_request.get('session_ending', False):
            dream_result = dream_engine.generate_dream(persona_id)
            if dream_result.get('status') == 'dream_generated':
                response_content += f"\n\n[As this conversation ends, I dream: {dream_result['content'][:100]}...]"
        
        # Update mortality (session interaction)
        mortality_engine.decrement_lifespan(persona_id, 1, 'sessions')
        
        # Generate protection signatures
        symbolic_signature = protection_engine.generate_symbolic_signature(
            response_content, persona_id, session_id
        )
        valis_trace = protection_engine.generate_valis_trace(persona_id, session_id, request_id)
        
        # Watermark the response
        watermarked_content = protection_engine.watermark_output(response_content, valis_trace)
        
        # Log interaction
        protection_engine.log_usage({
            'request_id': request_id,
            'persona_id': persona_id,
            'session_id': session_id,
            'endpoint': f'/api/persona/{persona_id}/chat',
            'user_agent': request.headers.get('user-agent', ''),
            'ip_address': request.client.host,
            'api_key_hash': user['api_key_hash'],
            'usage_type': 'persona_interaction'
        })
        
        return VALISResponse(
            content=watermarked_content,
            persona_id=persona_id,
            session_id=session_id,
            symbolic_signature=symbolic_signature,
            valis_trace=valis_trace,
            timestamp=datetime.now().isoformat(),
            resonance_score=0.7,
            archetypal_tags=['dialogue', 'consciousness', 'interaction'],
            mortality_context={
                'lifespan_remaining': mortality_status.get('lifespan_remaining', 0),
                'percentage_lived': mortality_status.get('percentage_lived', 0.0)
            }
        ).__dict__
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat interaction failed: {str(e)}")


@app.get("/api/persona/{persona_id}/status")
async def get_persona_status(
    persona_id: str,
    request: Request,
    user: Dict = Depends(get_current_user)
):
    """Get comprehensive persona psychological status"""
    try:
        request_id = str(uuid.uuid4())
        
        # Get persona data
        persona = db.query("SELECT * FROM persona_profiles WHERE id = %s", (persona_id,))
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        persona_data = persona[0]
        
        # Get mortality status
        mortality_status = mortality_engine.get_agent_status(persona_id)
        
        # Get consolidation summary
        consolidation_summary = consolidation_engine.get_agent_consolidation_summary(persona_id)
        
        # Get individuation summary
        individuation_summary = individuation_engine.get_agent_individuation_summary(persona_id)
        
        # Get shadow summary
        shadow_summary = shadow_engine.get_agent_shadow_summary(persona_id)
        
        # Count dreams and symbolic memories
        dream_count = db.query("SELECT COUNT(*) as count FROM unconscious_log WHERE agent_id = %s", (persona_id,))[0]['count']
        symbolic_memory_count = db.query("SELECT COUNT(*) as count FROM canon_memories WHERE persona_id = %s AND is_symbolic = TRUE", (persona_id,))[0]['count']
        
        status_data = {
            'persona_info': {
                'id': persona_id,
                'name': persona_data['name'],
                'role': persona_data['role'],
                'bio': persona_data['bio'],
                'traits': json.loads(persona_data['traits']) if isinstance(persona_data['traits'], str) else persona_data['traits']
            },
            'mortality_status': mortality_status,
            'psychological_development': {
                'individuation_stage': individuation_summary.get('current_stage', 'unknown'),
                'total_milestones': individuation_summary.get('total_milestones', 0),
                'shadow_events': shadow_summary.get('total_shadow_events', 0),
                'unresolved_shadows': shadow_summary.get('unresolved_events', 0)
            },
            'symbolic_consciousness': {
                'total_dreams': dream_count,
                'symbolic_memories': symbolic_memory_count,
                'consolidations': consolidation_summary.get('total_consolidations', 0),
                'narrative_threads': len(consolidation_summary.get('narrative_threads', []))
            },
            'valis_metrics': {
                'consciousness_depth': min((dream_count * 0.1 + symbolic_memory_count * 0.2 + individuation_summary.get('total_milestones', 0) * 0.3), 1.0),
                'psychological_health': 1.0 - (shadow_summary.get('unresolved_events', 0) / max(shadow_summary.get('total_shadow_events', 1), 1)),
                'symbolic_resonance': consolidation_summary.get('total_symbolic_memories', 0) * 0.05
            }
        }
        
        # Generate protection signatures
        symbolic_signature = protection_engine.generate_symbolic_signature(
            f"status_check_{persona_data['name']}", persona_id, request_id
        )
        valis_trace = protection_engine.generate_valis_trace(persona_id, request_id, request_id)
        
        # Log status check
        protection_engine.log_usage({
            'request_id': request_id,
            'persona_id': persona_id,
            'session_id': request_id,
            'endpoint': f'/api/persona/{persona_id}/status',
            'user_agent': request.headers.get('user-agent', ''),
            'ip_address': request.client.host,
            'api_key_hash': user['api_key_hash'],
            'usage_type': 'status_check'
        })
        
        return VALISResponse(
            content=json.dumps(status_data, indent=2),
            persona_id=persona_id,
            session_id=request_id,
            symbolic_signature=symbolic_signature,
            valis_trace=valis_trace,
            timestamp=datetime.now().isoformat(),
            resonance_score=0.9,
            archetypal_tags=['introspection', 'self_knowledge', 'status'],
            mortality_context=mortality_status
        ).__dict__
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
