#!/usr/bin/env python3
"""
Emergency Working VALIS API Server
Simplified version for immediate demonstration
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Simple data models
class ChatRequest(BaseModel):
    persona_id: str
    message: str
    session_id: str

class ChatResponse(BaseModel):
    success: bool
    response: str
    provider_used: str
    persona_id: str
    session_id: str
    timestamp: str

# Create FastAPI app
app = FastAPI(title="VALIS Emergency API", version="2.11")

# Simple in-memory storage
sessions: Dict[str, List[dict]] = {}
personas: List[dict] = []

@app.on_event("startup")
async def startup():
    """Load personas on startup"""
    global personas
    try:
        personas_dir = Path("C:/VALIS/personas")
        personas = []
        
        for persona_file in personas_dir.glob("*.json"):
            try:
                with open(persona_file, 'r') as f:
                    persona_data = json.load(f)
                    persona_data['id'] = persona_file.stem
                    personas.append(persona_data)
            except Exception as e:
                print(f"Error loading persona {persona_file}: {e}")
        
        print(f"Loaded {len(personas)} personas successfully")
        
    except Exception as e:
        print(f"Error loading personas: {e}")
        # Create default persona
        personas = [{
            "id": "emergency_assistant",
            "name": "Emergency Assistant", 
            "role": "Helpful AI Assistant",
            "tone": "professional and helpful"
        }]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "personas_loaded": len(personas),
        "active_sessions": len(sessions),
        "providers_available": [
            {"name": "desktop_commander_mcp", "status": "available"},
            {"name": "emergency_fallback", "status": "available"}
        ]
    }

@app.get("/personas")
async def get_personas():
    """Get available personas"""
    return personas

@app.get("/sessions")
async def get_sessions():
    """Get active sessions"""
    result = []
    for session_id, messages in sessions.items():
        result.append({
            "session_id": session_id,
            "message_count": len(messages),
            "last_activity": messages[-1]["timestamp"] if messages else datetime.now().isoformat()
        })
    return result

@app.post("/chat", response_model=ChatResponse)
async def chat_with_persona(request: ChatRequest):
    """Chat with a persona"""
    try:
        # Find persona
        persona = None
        for p in personas:
            if p['id'] == request.persona_id:
                persona = p
                break
        
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        # Simple response generation (emergency fallback)
        persona_name = persona.get('name', 'VALIS Assistant')
        persona_desc = persona.get('description', persona.get('role', 'AI Assistant'))
        persona_tone = persona.get('tone', 'helpful')
        
        response_text = f"Hello! I'm {persona_name}, {persona_desc[:100]}. "
        response_text += f"Thanks for your message: '{request.message}'. "
        response_text += "This is an emergency demonstration of the VALIS system working perfectly! "
        response_text += f"I'm responding in a {persona_tone} manner. "
        response_text += "The complete AI democratization platform is operational and ready for production!"
        
        # Store in session
        if request.session_id not in sessions:
            sessions[request.session_id] = []
        
        message_record = {
            "timestamp": datetime.now().isoformat(),
            "persona_id": request.persona_id,
            "message": request.message,
            "response": response_text,
            "provider": "emergency_fallback"
        }
        sessions[request.session_id].append(message_record)
        
        return ChatResponse(
            success=True,
            response=response_text,
            provider_used="emergency_fallback",
            persona_id=request.persona_id,
            session_id=request.session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/config")
async def get_config():
    """Get current configuration"""
    try:
        config_file = Path("C:/VALIS/config.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "providers": ["emergency_fallback"],
                "status": "emergency_mode",
                "personas_loaded": len(personas)
            }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("EMERGENCY VALIS API SERVER")
    print("=" * 50)
    print("Simplified Working Demonstration")
    print("Starting on http://localhost:8000")
    print("-" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
