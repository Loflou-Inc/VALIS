"""
VALIS - Vast Active Living Intelligence System
Universal AI Persona Engine with Temporal Stabilization

The core engine that provides AI personas to any application.
Supports multiple AI backends with graceful fallbacks and async coordination.

Based on Philip K. Dick's concept of VALIS - a mystical AI intelligence.
"""

import json
import logging
import asyncio
import uuid
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

class VALISEngine:
    """
    The main VALIS engine - Universal AI Persona System
    
    Provides a simple interface for any application to get AI persona responses.
    Handles provider selection, fallbacks, and response generation.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize VALIS with temporal stabilization"""
        self.config = self._load_config(config_path)
        self.personas = {}
        self.providers = []
        self.logger = self._setup_logging()
        
        # Temporal coordination components
        self.session_lock = asyncio.Lock()
        self.active_sessions = {}
        self.session_cleanup_task = None
        self.session_timeout = timedelta(minutes=30)
        
        # Request coordination
        self.request_queue = asyncio.Queue(maxsize=100)  # Backpressure limit
        self.request_semaphore = asyncio.Semaphore(20)   # Concurrent request limit
        self.persona_locks = defaultdict(asyncio.Lock)   # Per-persona locks
        
        # Performance tracking
        self.request_metrics = defaultdict(list)
        self.engine_start_time = datetime.now()
        
        # Load personas and providers
        self._initialize_personas()
        self._initialize_providers()
        
        # Start session cleanup task
        self._start_session_cleanup()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load VALIS configuration"""
        default_config = {
            "personas_dir": "personas",
            "providers": ["desktop_commander_mcp", "anthropic_api", "openai_api", "hardcoded_fallback"],
            "logging_level": "INFO",
            "max_response_time": 30,
            "enable_memory": True
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        return default_config    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for VALIS"""
        logger = logging.getLogger('VALIS')
        logger.setLevel(getattr(logging, self.config['logging_level']))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - VALIS - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _initialize_personas(self):
        """Load all available personas"""
        personas_dir = Path(__file__).parent.parent / self.config['personas_dir']
        
        if not personas_dir.exists():
            self.logger.warning(f"Personas directory not found: {personas_dir}")
            return
            
        for persona_file in personas_dir.glob("*.json"):
            try:
                with open(persona_file, 'r') as f:
                    persona_data = json.load(f)
                    persona_id = persona_file.stem
                    self.personas[persona_id] = persona_data
                    self.logger.info(f"Loaded persona: {persona_id}")
            except Exception as e:
                self.logger.error(f"Error loading persona {persona_file}: {e}")
    
    def _initialize_providers(self):
        """Initialize AI providers in order of preference"""
        from core.provider_manager import ProviderManager
        self.provider_manager = ProviderManager(self.config['providers'])
        self.logger.info(f"Initialized {len(self.config['providers'])} providers")    
    async def get_persona_response(
        self, 
        persona_id: str, 
        message: str, 
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Get a response from a specific persona with temporal coordination"""
        request_start = datetime.now()
        
        # Validate persona exists
        if persona_id not in self.personas:
            return {
                "success": False,
                "error": f"Unknown persona: {persona_id}",
                "available_personas": list(self.personas.keys())
            }
        
        # Check for backpressure
        if await self._check_request_queue_pressure():
            return {
                "success": False,
                "error": "System overloaded - too many concurrent requests",
                "retry_after": 30
            }
        
        # Use semaphore to limit concurrent requests
        async with self.request_semaphore:
            # Manage session with temporal coordination
            session_id = await self._manage_session(session_id)
            
            # Use per-persona lock to prevent conflicts
            async with self.persona_locks[persona_id]:
                try:
                    persona = self.personas[persona_id]
                    
                    # Add request tracking context
                    enhanced_context = context or {}
                    enhanced_context.update({
                        'session_id': session_id,
                        'request_timestamp': request_start.isoformat(),
                        'engine_uptime': str(datetime.now() - self.engine_start_time)
                    })
                    
                    # Get response through provider cascade
                    result = await self.provider_manager.get_response(
                        persona=persona,
                        message=message,
                        session_id=session_id,
                        context=enhanced_context
                    )
                    
                    # Record performance metrics
                    response_time = (datetime.now() - request_start).total_seconds()
                    self.request_metrics[persona_id].append({
                        'timestamp': request_start,
                        'response_time': response_time,
                        'success': result.get('success', False),
                        'provider_used': result.get('provider_used', 'unknown')
                    })
                    
                    # Add temporal metadata to response
                    result.update({
                        'session_id': session_id,
                        'response_time': response_time,
                        'engine_version': 'VALIS-Temporal-Stabilized'
                    })
                    
                    self.logger.info(f"Response generated for {persona_id} via {result.get('provider_used', 'unknown')} in {response_time:.3f}s")
                    return result
                    
                except Exception as e:
                    response_time = (datetime.now() - request_start).total_seconds()
                    
                    # Record failed request metrics
                    self.request_metrics[persona_id].append({
                        'timestamp': request_start,
                        'response_time': response_time,
                        'success': False,
                        'error': str(e)
                    })
                    
                    self.logger.error(f"Error getting response for {persona_id}: {e}")
                    return {
                        "success": False, 
                        "error": str(e), 
                        "persona_id": persona_id,
                        "session_id": session_id,
                        "response_time": response_time
                    }    
    def get_available_personas(self) -> List[Dict[str, Any]]:
        """Get list of all available personas with their basic info"""
        return [
            {
                "id": persona_id,
                "name": persona_data.get("name", persona_id),
                "description": persona_data.get("description", ""),
                "expertise": persona_data.get("expertise", [])
            }
            for persona_id, persona_data in self.personas.items()
        ]
    
    def get_persona_info(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific persona"""
        return self.personas.get(persona_id)
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the VALIS system"""
        return {
            "status": "operational",
            "personas_loaded": len(self.personas),
            "providers_available": len(self.config['providers']),
            "personas": list(self.personas.keys())
        }
    
    def _start_session_cleanup(self):
        """Start the session cleanup background task"""
        async def cleanup_sessions():
            while True:
                try:
                    await asyncio.sleep(300)  # Check every 5 minutes
                    await self._cleanup_expired_sessions()
                except Exception as e:
                    self.logger.error(f"Session cleanup error: {e}")
        
        # Start the cleanup task (will run in background)
        try:
            loop = asyncio.get_event_loop()
            self.session_cleanup_task = loop.create_task(cleanup_sessions())
        except RuntimeError:
            # No event loop running yet, cleanup will start when needed
            self.session_cleanup_task = None
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions to prevent memory leaks"""
        async with self.session_lock:
            now = datetime.now()
            expired_sessions = []
            
            for session_id, session_data in self.active_sessions.items():
                if now - session_data['last_activity'] > self.session_timeout:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
                self.logger.debug(f"Cleaned up expired session: {session_id}")
            
            if expired_sessions:
                self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    async def _manage_session(self, session_id: Optional[str]) -> str:
        """Manage session state with temporal coordination"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        async with self.session_lock:
            now = datetime.now()
            
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    'created': now,
                    'last_activity': now,
                    'request_count': 0
                }
                self.logger.debug(f"Created new session: {session_id}")
            else:
                self.active_sessions[session_id]['last_activity'] = now
            
            self.active_sessions[session_id]['request_count'] += 1
            
        return session_id
    
    async def _check_request_queue_pressure(self) -> bool:
        """Check if request queue has backpressure"""
        queue_size = self.request_queue.qsize() if hasattr(self.request_queue, '_qsize') else 0
        
        if queue_size > 80:  # 80% of maxsize
            self.logger.warning(f"High request queue pressure: {queue_size}/100")
            return True
        return False
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive engine status for monitoring"""
        now = datetime.now()
        uptime = now - self.engine_start_time
        
        return {
            "status": "operational",
            "uptime": str(uptime),
            "personas_loaded": len(self.personas),
            "active_sessions": len(self.active_sessions),
            "total_requests": sum(len(metrics) for metrics in self.request_metrics.values()),
            "recent_requests": sum(
                len([m for m in metrics if now - m['timestamp'] < timedelta(minutes=5)]) 
                for metrics in self.request_metrics.values()
            ),
            "provider_cascade": self.provider_manager.get_cascade_status() if hasattr(self, 'provider_manager') else {},
            "performance_summary": self._get_performance_summary()
        }
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all personas"""
        summary = {}
        now = datetime.now()
        
        for persona_id, metrics in self.request_metrics.items():
            recent_metrics = [m for m in metrics if now - m['timestamp'] < timedelta(hours=1)]
            
            if recent_metrics:
                response_times = [m['response_time'] for m in recent_metrics if 'response_time' in m]
                success_rate = len([m for m in recent_metrics if m.get('success', False)]) / len(recent_metrics)
                
                summary[persona_id] = {
                    "requests_last_hour": len(recent_metrics),
                    "success_rate": success_rate,
                    "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
                    "max_response_time": max(response_times) if response_times else 0
                }
        
        return summary
    
    async def shutdown(self):
        """Graceful shutdown of VALIS engine"""
        self.logger.info("Shutting down VALIS engine...")
        
        # Cancel session cleanup task
        if self.session_cleanup_task:
            self.session_cleanup_task.cancel()
            try:
                await self.session_cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Clear active sessions
        async with self.session_lock:
            self.active_sessions.clear()
        
        self.logger.info("VALIS engine shutdown complete")

# Convenience function for simple usage
async def ask_persona(persona_id: str, message: str, session_id: Optional[str] = None) -> str:
    """Simple convenience function to get a persona response"""
    engine = VALISEngine()
    result = await engine.get_persona_response(persona_id, message, session_id)
    
    if result.get("success"):
        return result.get("response", "No response generated")
    else:
        return f"Error: {result.get('error', 'Unknown error')}"
