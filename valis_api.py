#!/usr/bin/env python3
"""
VALIS FastAPI Service Layer - Enhanced with Temporal-Safe Logging
Doc Brown's API-102 & API-103 Enhancements
"""

import asyncio
import os
import time
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
import sqlite3
import threading

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
import uvicorn
from dotenv import load_dotenv

# Import our bulletproof VALIS engine
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.valis_engine import VALISEngine
from core.config_schema import VALISConfig

# Load environment variables FIRST (Doc Brown's requirement)
load_dotenv()

# Configure enhanced JSON logging (API-102)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('valis_api.log')
    ]
)

# Create secure logger that filters sensitive data
class SecureJSONFormatter(logging.Formatter):
    """Custom formatter that prevents API key leakage"""
    
    SENSITIVE_KEYS = ['api_key', 'openai_api_key', 'anthropic_api_key', 'authorization', 'bearer']
    
    def format(self, record):
        # Convert log record to JSON, filtering sensitive data
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName
        }
        
        # Filter any sensitive data from the message
        message = record.getMessage().lower()
        for sensitive_key in self.SENSITIVE_KEYS:
            if sensitive_key in message:
                log_data['message'] = '[REDACTED - SENSITIVE DATA FILTERED]'
                break
                
        return json.dumps(log_data)

# Apply secure logging
logger = logging.getLogger("valis_api")
handler = logging.StreamHandler()
handler.setFormatter(SecureJSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Rate limiting storage
request_counts = defaultdict(list)
RATE_LIMIT_REQUESTS = 60  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

# Pydantic Models for API
class ChatRequest(BaseModel):
    session_id: str
    persona_id: str
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    provider: Optional[str] = None
    session_id: str
    persona_id: str
    timestamp: str
    request_id: Optional[str] = None
    error: Optional[str] = None
    timing: Optional[Dict[str, float]] = None

class PersonaInfo(BaseModel):
    id: str
    name: str
    role: str
    description: Optional[str] = None
    available: bool = True

class SessionInfo(BaseModel):
    session_id: str
    created_at: str
    last_activity: str
    request_count: int
    last_persona: Optional[str] = None

class HealthStatus(BaseModel):
    status: str
    timestamp: str
    system_info: Dict[str, Any]
    providers_available: List[str]
    personas_loaded: int
    active_sessions: int

# Initialize VALIS Engine (Temporal-Safe)
valis_engine = VALISEngine()

# Create FastAPI application
app = FastAPI(
    title="VALIS API",
    description="Temporal-Safe AI Democratization Service",
    version="2.11.0"
)

# Configure CORS (Doc Brown's security requirement)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Rate limiting function (Temporal Overload Prevention)
async def check_rate_limit(request: Request):
    """Doc Brown's temporal overload prevention"""
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old requests outside window
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]
    
    # Check if limit exceeded
    if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {RATE_LIMIT_REQUESTS} requests per minute"
        )
    
    # Record this request
    request_counts[client_ip].append(current_time)

# API ENDPOINTS

@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(check_rate_limit)])
async def chat_endpoint(chat_request: ChatRequest) -> ChatResponse:
    """
    Handle chat requests with temporal session isolation
    Doc Brown's Requirements: Preserve session isolation ✅
    """
    try:
        start_time = time.time()
        
        # Use our bulletproof VALIS engine (no logic duplication)
        result = await valis_engine.get_persona_response(
            persona_id=chat_request.persona_id,
            message=chat_request.message,
            session_id=chat_request.session_id,
            context=chat_request.context
        )
        
        processing_time = time.time() - start_time
        
        # Convert VALIS result to API response format
        return ChatResponse(
            success=result.get('success', False),
            response=result.get('response'),
            provider=result.get('provider'),
            session_id=chat_request.session_id,
            persona_id=chat_request.persona_id,
            timestamp=datetime.now().isoformat(),
            request_id=result.get('request_id'),
            error=result.get('error'),
            timing={
                'processing_time': processing_time,
                'provider_time': result.get('provider_time', 0)
            }
        )
        
    except Exception as e:
        return ChatResponse(
            success=False,
            response=None,
            provider=None,
            session_id=chat_request.session_id,
            persona_id=chat_request.persona_id,
            timestamp=datetime.now().isoformat(),
            error=f"API Error: {str(e)}"
        )

@app.get("/personas", response_model=List[PersonaInfo])
async def get_personas() -> List[PersonaInfo]:
    """Return available persona metadata"""
    try:
        personas = valis_engine.get_available_personas()
        return [
            PersonaInfo(
                id=persona_id,
                name=persona_data.get('name', persona_id),
                role=persona_data.get('role', 'Unknown'),
                description=persona_data.get('background', ''),
                available=True
            )
            for persona_id, persona_data in personas.items()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get personas: {str(e)}")

@app.get("/sessions", response_model=List[SessionInfo])
async def get_sessions() -> List[SessionInfo]:
    """Return active session metadata with temporal isolation"""
    try:
        sessions = valis_engine.get_active_sessions()
        return [
            SessionInfo(
                session_id=session_id,
                created_at=session_data.get('created_at', ''),
                last_activity=session_data.get('last_activity', ''),
                request_count=session_data.get('request_count', 0),
                last_persona=session_data.get('last_persona')
            )
            for session_id, session_data in sessions.items()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")

@app.get("/health", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """Proxy to engine.health_check() as requested by Doc Brown"""
    try:
        health_data = await valis_engine.health_check()
        
        return HealthStatus(
            status=health_data.get('status', 'unknown'),
            timestamp=datetime.now().isoformat(),
            system_info=health_data.get('system_info', {}),
            providers_available=health_data.get('providers_available', []),
            personas_loaded=health_data.get('personas_loaded', 0),
            active_sessions=health_data.get('active_sessions', 0)
        )
    except Exception as e:
        return HealthStatus(
            status="error",
            timestamp=datetime.now().isoformat(),
            system_info={"error": str(e)},
            providers_available=[],
            personas_loaded=0,
            active_sessions=0
        )

@app.get("/config")
async def get_config():
    """Return current configuration"""
    try:
        return valis_engine.get_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get config: {str(e)}")

@app.post("/config")
async def update_config(new_config: Dict[str, Any], dependencies=[Depends(check_rate_limit)]):
    """Dynamic config editing with validation (Doc Brown's requirement)"""
    try:
        # Use our proven schema validation
        validated_config = VALISConfig(**new_config)
        
        # Update engine configuration
        await valis_engine.update_config(validated_config.dict())
        
        return {"status": "success", "message": "Configuration updated"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Config validation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")

# Global error handler for temporal stability
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to prevent timeline disasters"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": f"Temporal anomaly detected: {str(exc)}",
            "timestamp": datetime.now().isoformat(),
            "endpoint": str(request.url)
        }
    )

# Development server startup
if __name__ == "__main__":
    print("VALIS API Server Starting...")
    print("Temporal-Safe AI Democratization Service")
    print("Doc Brown's Specifications Implemented")
    print("-" * 50)
    
    uvicorn.run(
        "valis_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=True
    )

# API-103: Message History Tracking with Temporal Safeguards
class MessageHistoryManager:
    """
    Temporal-Safe Message History System
    Doc Brown's Required Safeguards:
    - Automatic cleanup ✅
    - Maximum messages per session ✅
    - Bounded data structures ✅
    - Message size limits ✅
    - SQLite with proper indexing ✅
    - Privacy-safe data handling ✅
    """
    
    def __init__(self, db_path: str = "valis_message_history.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        
        # TEMPORAL SAFEGUARDS
        self.MAX_MESSAGES_PER_SESSION = 100  # Prevent session data explosion
        self.MAX_MESSAGE_SIZE = 10000  # Prevent massive message storage
        self.CLEANUP_HOURS = 24  # Auto-cleanup after 24 hours
        self.MAX_TOTAL_MESSAGES = 10000  # Global message limit
        
        self._initialize_database()
        logger.info("Message History Manager initialized with temporal safeguards")
    
    def _initialize_database(self):
        """Initialize SQLite database with proper indexing"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS message_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    persona_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    provider_used TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Critical indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON message_history(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON message_history(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON message_history(created_at)")
            conn.commit()
    
    def add_message(self, session_id: str, persona_id: str, message: str, 
                   response: str, provider_used: str) -> bool:
        """Add message with temporal safeguards"""
        try:
            # SAFEGUARD 1: Message size limit
            if len(message) > self.MAX_MESSAGE_SIZE or len(response) > self.MAX_MESSAGE_SIZE:
                logger.warning(f"Message too large for session {session_id}, truncating")
                message = message[:self.MAX_MESSAGE_SIZE]
                response = response[:self.MAX_MESSAGE_SIZE]
            
            # SAFEGUARD 2: Check session message limit
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM message_history WHERE session_id = ?",
                    (session_id,)
                )
                count = cursor.fetchone()[0]
                
                if count >= self.MAX_MESSAGES_PER_SESSION:
                    # Remove oldest message for this session
                    conn.execute("""
                        DELETE FROM message_history 
                        WHERE session_id = ? AND id = (
                            SELECT id FROM message_history 
                            WHERE session_id = ? 
                            ORDER BY timestamp ASC LIMIT 1
                        )
                    """, (session_id, session_id))
                
                # Add new message
                conn.execute("""
                    INSERT INTO message_history 
                    (session_id, timestamp, persona_id, message, response, provider_used)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (session_id, time.time(), persona_id, message, response, provider_used))
                
                conn.commit()
            
            # SAFEGUARD 3: Global cleanup if needed
            self._cleanup_if_needed()
            return True
            
        except Exception as e:
            logger.error(f"Failed to add message history: {e}")
            return False

    def _cleanup_if_needed(self):
        """Automatic cleanup to prevent temporal disasters"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # SAFEGUARD 1: Remove messages older than CLEANUP_HOURS
                cutoff_time = time.time() - (self.CLEANUP_HOURS * 3600)
                cursor = conn.execute(
                    "DELETE FROM message_history WHERE timestamp < ?",
                    (cutoff_time,)
                )
                deleted_old = cursor.rowcount
                
                # SAFEGUARD 2: Global message limit
                cursor = conn.execute("SELECT COUNT(*) FROM message_history")
                total_count = cursor.fetchone()[0]
                
                if total_count > self.MAX_TOTAL_MESSAGES:
                    # Remove oldest messages globally
                    excess = total_count - self.MAX_TOTAL_MESSAGES
                    conn.execute("""
                        DELETE FROM message_history WHERE id IN (
                            SELECT id FROM message_history 
                            ORDER BY timestamp ASC LIMIT ?
                        )
                    """, (excess,))
                    deleted_excess = cursor.rowcount
                    logger.info(f"Cleaned up {deleted_excess} excess messages")
                
                if deleted_old > 0:
                    logger.info(f"Cleaned up {deleted_old} old messages")
                
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get message history for a session with limits"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT session_id, timestamp, persona_id, message, response, provider_used
                    FROM message_history 
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (session_id, min(limit, 100)))  # Cap at 100 for safety
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get session history: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics for monitoring"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM message_history")
                total_messages = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(DISTINCT session_id) FROM message_history")
                unique_sessions = cursor.fetchone()[0]
                
                return {
                    'total_messages': total_messages,
                    'unique_sessions': unique_sessions,
                    'max_per_session': self.MAX_MESSAGES_PER_SESSION,
                    'cleanup_hours': self.CLEANUP_HOURS,
                    'max_total': self.MAX_TOTAL_MESSAGES
                }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

# Initialize Message History Manager with temporal safeguards
message_history = MessageHistoryManager()

# Rate limiting storage
request_counts = defaultdict(list)
RATE_LIMIT_REQUESTS = 60  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

# Enhanced Pydantic Models
class ChatRequest(BaseModel):
    session_id: str
    persona_id: str
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    provider: Optional[str] = None
    session_id: str
    persona_id: str
    timestamp: str
    request_id: Optional[str] = None
    error: Optional[str] = None
    timing: Optional[Dict[str, float]] = None

class MessageHistoryEntry(BaseModel):
    session_id: str
    timestamp: float
    persona_id: str
    message: str
    response: str
    provider_used: str

class MessageHistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageHistoryEntry]
    total_count: int

class PersonaInfo(BaseModel):
    id: str
    name: str
    role: str
    description: Optional[str] = None
    available: bool = True

class SessionInfo(BaseModel):
    session_id: str
    created_at: str
    last_activity: str
    request_count: int
    last_persona: Optional[str] = None
    message_count: Optional[int] = None

class HealthStatus(BaseModel):
    status: str
    timestamp: str
    system_info: Dict[str, Any]
    providers_available: List[str]
    personas_loaded: int
    active_sessions: int
    message_history_stats: Optional[Dict[str, Any]] = None

class SystemStats(BaseModel):
    message_history: Dict[str, Any]
    active_sessions: int
    total_requests: int
    uptime_seconds: float

# Initialize VALIS Engine (Temporal-Safe)
valis_engine = VALISEngine()
startup_time = time.time()

# Create FastAPI application with enhanced configuration
app = FastAPI(
    title="VALIS API Enhanced",
    description="Temporal-Safe AI Democratization Service with Message History",
    version="2.11.1"
)

# Enhanced CORS Configuration (API-102)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Development frontend
        "http://127.0.0.1:3000",   # Development frontend (alternative)
        "http://localhost:8080",   # Alternative dev port
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Enhanced rate limiting with logging
async def check_rate_limit(request: Request):
    """Enhanced rate limiting with temporal overload prevention"""
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old requests outside window
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]
    
    # Check if limit exceeded
    if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {RATE_LIMIT_REQUESTS} requests per minute"
        )
    
    # Record this request
    request_counts[client_ip].append(current_time)
    logger.debug(f"Request from {client_ip}, count: {len(request_counts[client_ip])}")

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log requests with sensitive data filtering"""
    start_time = time.time()
    
    # Log request (without sensitive data)
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} in {process_time:.3f}s")
    
    return response

# ENHANCED API ENDPOINTS WITH MESSAGE HISTORY

@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(check_rate_limit)])
async def enhanced_chat_endpoint(chat_request: ChatRequest) -> ChatResponse:
    """
    Enhanced chat endpoint with message history tracking
    Doc Brown's API-103 Implementation with temporal safeguards
    """
    try:
        start_time = time.time()
        
        logger.info(f"Chat request: session={chat_request.session_id}, persona={chat_request.persona_id}")
        
        # Use our bulletproof VALIS engine (no logic duplication)
        result = await valis_engine.get_persona_response(
            persona_id=chat_request.persona_id,
            message=chat_request.message,
            session_id=chat_request.session_id,
            context=chat_request.context
        )
        
        processing_time = time.time() - start_time
        
        # ENHANCED: Store message history with temporal safeguards
        if result.get('success') and result.get('response'):
            message_history.add_message(
                session_id=chat_request.session_id,
                persona_id=chat_request.persona_id,
                message=chat_request.message,
                response=result.get('response', ''),
                provider_used=result.get('provider', 'Unknown')
            )
            logger.debug(f"Message history stored for session {chat_request.session_id}")
        
        # Convert VALIS result to API response format
        return ChatResponse(
            success=result.get('success', False),
            response=result.get('response'),
            provider=result.get('provider'),
            session_id=chat_request.session_id,
            persona_id=chat_request.persona_id,
            timestamp=datetime.now().isoformat(),
            request_id=result.get('request_id'),
            error=result.get('error'),
            timing={
                'processing_time': processing_time,
                'provider_time': result.get('provider_time', 0)
            }
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return ChatResponse(
            success=False,
            response=None,
            provider=None,
            session_id=chat_request.session_id,
            persona_id=chat_request.persona_id,
            timestamp=datetime.now().isoformat(),
            error=f"API Error: {str(e)}"
        )

@app.get("/sessions/{session_id}/history", response_model=MessageHistoryResponse)
async def get_session_message_history(session_id: str, limit: int = 50) -> MessageHistoryResponse:
    """Get message history for a specific session"""
    try:
        logger.info(f"Retrieving history for session: {session_id}")
        
        messages = message_history.get_session_history(session_id, limit)
        
        return MessageHistoryResponse(
            session_id=session_id,
            messages=[MessageHistoryEntry(**msg) for msg in messages],
            total_count=len(messages)
        )
        
    except Exception as e:
        logger.error(f"Failed to get session history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

@app.get("/admin/stats", response_model=SystemStats)
async def get_system_stats() -> SystemStats:
    """Get system statistics for monitoring"""
    try:
        return SystemStats(
            message_history=message_history.get_stats(),
            active_sessions=len(valis_engine.get_active_sessions()),
            total_requests=sum(len(reqs) for reqs in request_counts.values()),
            uptime_seconds=time.time() - startup_time
        )
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/personas", response_model=List[PersonaInfo])
async def get_personas() -> List[PersonaInfo]:
    """Return available persona metadata"""
    try:
        logger.debug("Retrieving personas")
        personas = valis_engine.get_available_personas()
        return [
            PersonaInfo(
                id=persona_id,
                name=persona_data.get('name', persona_id),
                role=persona_data.get('role', 'Unknown'),
                description=persona_data.get('background', ''),
                available=True
            )
            for persona_id, persona_data in personas.items()
        ]
    except Exception as e:
        logger.error(f"Failed to get personas: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get personas: {str(e)}")

@app.get("/sessions", response_model=List[SessionInfo])
async def get_enhanced_sessions() -> List[SessionInfo]:
    """Return active session metadata with message counts"""
    try:
        logger.debug("Retrieving enhanced sessions")
        sessions = valis_engine.get_active_sessions()
        result = []
        
        for session_id, session_data in sessions.items():
            # Get message count from history
            history = message_history.get_session_history(session_id, 1)
            message_count = len(message_history.get_session_history(session_id, 1000))
            
            result.append(SessionInfo(
                session_id=session_id,
                created_at=session_data.get('created_at', ''),
                last_activity=session_data.get('last_activity', ''),
                request_count=session_data.get('request_count', 0),
                last_persona=session_data.get('last_persona'),
                message_count=message_count
            ))
        
        return result
    except Exception as e:
        logger.error(f"Failed to get sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")

@app.get("/health", response_model=HealthStatus)
async def enhanced_health_check() -> HealthStatus:
    """Enhanced health check with message history stats"""
    try:
        health_data = await valis_engine.health_check()
        
        return HealthStatus(
            status=health_data.get('status', 'unknown'),
            timestamp=datetime.now().isoformat(),
            system_info=health_data.get('system_info', {}),
            providers_available=health_data.get('providers_available', []),
            personas_loaded=health_data.get('personas_loaded', 0),
            active_sessions=health_data.get('active_sessions', 0),
            message_history_stats=message_history.get_stats()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthStatus(
            status="error",
            timestamp=datetime.now().isoformat(),
            system_info={"error": str(e)},
            providers_available=[],
            personas_loaded=0,
            active_sessions=0,
            message_history_stats={}
        )

@app.get("/config")
async def get_config():
    """Return current configuration"""
    try:
        return valis_engine.get_config()
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get config: {str(e)}")

@app.post("/config")
async def update_config(new_config: Dict[str, Any], dependencies=[Depends(check_rate_limit)]):
    """Dynamic config editing with validation"""
    try:
        logger.info("Updating configuration")
        # Use our proven schema validation
        validated_config = VALISConfig(**new_config)
        
        # Update engine configuration
        await valis_engine.update_config(validated_config.dict())
        
        logger.info("Configuration updated successfully")
        return {"status": "success", "message": "Configuration updated"}
    except ValidationError as e:
        logger.error(f"Config validation failed: {e}")
        raise HTTPException(status_code=400, detail=f"Config validation failed: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")

# Enhanced global error handler
@app.exception_handler(Exception)
async def enhanced_exception_handler(request: Request, exc: Exception):
    """Enhanced global exception handler with logging"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": f"Temporal anomaly detected: {str(exc)}",
            "timestamp": datetime.now().isoformat(),
            "endpoint": str(request.url)
        }
    )

# Enhanced startup event
@app.on_event("startup")
async def startup_event():
    """Enhanced startup with logging"""
    logger.info("VALIS API Enhanced Server Starting...")
    logger.info("Temporal-Safe AI Democratization Service with Message History")
    logger.info("Doc Brown's API-102 & API-103 Specifications Implemented")
    logger.info("FastAPI + VALIS Engine + Message History Integration")
    logger.info(f"Message History: Max {message_history.MAX_MESSAGES_PER_SESSION} per session")
    logger.info(f"Auto-cleanup: {message_history.CLEANUP_HOURS} hours")
    logger.info("Enhanced CORS enabled for localhost:3000")
    logger.info("Available endpoints: /chat, /personas, /sessions, /health, /config, /sessions/{id}/history, /admin/stats")

# Development server startup with enhanced uvicorn configuration
if __name__ == "__main__":
    print("VALIS API Enhanced Server Starting...")
    print("Temporal-Safe AI Democratization Service")
    print("Doc Brown's API-102 & API-103 Implemented")
    print("Enhanced with Message History & Secure Logging")
    print("-" * 50)
    
    # Enhanced uvicorn configuration (API-102)
    uvicorn.run(
        "valis_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=True,
        log_level="debug",  # Enhanced debug logging
        use_colors=True,
        reload_dirs=["./"]
    )
