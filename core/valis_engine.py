"""
VALIS - Vast Active Living Intelligence System
Universal AI Persona Engine

The core engine that provides AI personas to any application.
Supports multiple AI backends with graceful fallbacks.

Based on Philip K. Dick's concept of VALIS - a mystical AI intelligence.
"""

import json
import logging
import asyncio
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

class VALISEngine:
    """
    The main VALIS engine - Universal AI Persona System
    
    Provides a simple interface for any application to get AI persona responses.
    Handles provider selection, fallbacks, and response generation.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize VALIS with configuration"""
        self.config = self._load_config(config_path)
        self.personas = {}
        self.providers = []
        self.logger = self._setup_logging()
        
        # Add concurrency control (Doc Brown's specs)
        self._request_lock = asyncio.Lock()
        self._active_requests = {}  # Track active requests by session_id
        self._request_counter = 0
        
        # Add basic memory integration (Task 2.1)
        self.memory_enabled = self.config.get('enable_memory', False)
        self.memory_client = None

        if self.memory_enabled:
            try:
                sys.path.append(str(Path(__file__).parent.parent / "claude-memory-ADV" / "MEMORY_DEV"))
                from memory_manager import add_memory, query_memories
                self.memory_client = {"add": add_memory, "query": query_memories}
                self.logger.info("Memory system connected successfully")
            except Exception as e:
                self.logger.warning(f"Memory system connection failed: {e}")
                self.memory_enabled = False
        
        # Add session tracking (Task 2.2)
        self.sessions = {}  # Track active sessions
        self.session_timeout = 30 * 60  # 30 minutes in seconds
        
        # NEURAL MATRIX HEALTH MONITORING (Task 2.4)
        try:
            from core.neural_health_monitor import NeuralMatrixHealthMonitor
            memory_dir = str(Path(__file__).parent.parent / "claude-memory-ADV" / "MEMORY_DEV")
            self.neural_health_monitor = NeuralMatrixHealthMonitor(memory_dir)
            self.logger.info("Neural Matrix Health Monitor initialized")
        except Exception as e:
            self.logger.warning(f"Neural Health Monitor initialization failed: {e}")
            self.neural_health_monitor = None
        
        # Load personas and providers
        self._initialize_personas()
        self._initialize_providers()
        
    def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get or create session context"""
        import time
        current_time = time.time()
        
        if session_id in self.sessions:
            # Update last activity time
            self.sessions[session_id]["last_activity"] = current_time
            return self.sessions[session_id]
        else:
            # Create new session
            session_context = {
                "created": current_time,
                "last_activity": current_time,
                "request_count": 0,
                "last_persona": None,
                "conversation_summary": []
            }
            self.sessions[session_id] = session_context
            self.logger.info(f"Created new session: {session_id}")
            return session_context
        
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
        """Get a response from a specific persona with enhanced concurrency control"""
        
        # Generate unique request ID
        async with self._request_lock:
            self._request_counter += 1
            request_id = f"req_{self._request_counter}_{persona_id}"
        
        self.logger.info(f"Processing request {request_id} for persona {persona_id}")
        
        # Add session context tracking (Task 2.2)
        session_context = None
        if session_id:
            session_context = self._get_session_context(session_id)
            session_context["request_count"] += 1
            session_context["last_persona"] = persona_id
        
        if persona_id not in self.personas:
            return {
                "success": False,
                "error": f"Unknown persona: {persona_id}",
                "available_personas": list(self.personas.keys()),
                "request_id": request_id
            }
        
        persona = self.personas[persona_id]
        
        # Check for concurrent requests from same session
        if session_id:
            async with self._request_lock:
                if session_id in self._active_requests:
                    self.logger.warning(f"Concurrent request detected for session {session_id}")
                    await asyncio.sleep(0.1)  # Brief delay to prevent cascade conflicts
                self._active_requests[session_id] = request_id
        
        try:
            # NEURAL MATRIX CONTEXT DEGRADATION PREVENTION (Task 2.3)
            # Enrich context with neural memories for seamless provider cascade
            enhanced_context = context.copy() if context else {}
            
            if self.memory_enabled and self.memory_client:
                try:
                    # Retrieve relevant conversation history for context continuity
                    memory_query = f"{persona_id} {message[:100]}"
                    relevant_memories = self.memory_client["query"](memory_query, top_k=8)
                    
                    if relevant_memories:
                        # Compress neural context to prevent token limit issues
                        compressed_context = self._compress_neural_context(relevant_memories)
                        
                        # NEURAL HEALTH MONITORING (Task 2.4)
                        # Track context retrieval and compression metrics
                        if self.neural_health_monitor:
                            compression_ratio = compressed_context["compressed_count"] / compressed_context["memory_count"] if compressed_context["memory_count"] > 0 else 1.0
                            self.neural_health_monitor.monitor_context_quality(
                                handoff_success=True,
                                compression_ratio=compression_ratio
                            )
                            self.neural_health_monitor.metrics['context_retrievals'] += 1
                        
                        # Create neural context for provider handoff
                        neural_context = {
                            "conversation_summary": compressed_context["summary"],
                            "recent_interactions": compressed_context["recent_memories"][:3],
                            "context_source": "neural_matrix",
                            "persona_continuity": f"Continuing conversation with {persona['name']} - {compressed_context['memory_count']} previous interactions",
                            "context_stats": {
                                "total_memories": compressed_context["memory_count"],
                                "included_memories": compressed_context["compressed_count"],
                                "context_compressed": compressed_context["context_compressed"]
                            }
                        }
                        enhanced_context["neural_context"] = neural_context
                        self.logger.info(f"Neural context added: {compressed_context['compressed_count']}/{compressed_context['memory_count']} memories for provider cascade")
                    
                    # Add session-specific context if available
                    if session_context:
                        enhanced_context["session_info"] = {
                            "request_count": session_context["request_count"],
                            "last_persona": session_context["last_persona"],
                            "session_continuity": f"This is request #{session_context['request_count']} in this session"
                        }
                        
                except Exception as e:
                    self.logger.warning(f"Neural context enhancement failed: {e}")
                    # Continue with original context if neural enhancement fails
                    enhanced_context = context.copy() if context else {}
            
            # Get response through provider cascade with enhanced neural context
            result = await self.provider_manager.get_response(
                persona=persona,
                message=message,
                session_id=session_id,
                context=enhanced_context
            )
            
            result["request_id"] = request_id
            self.logger.info(f"Request {request_id} completed via {result.get('provider_used', 'unknown')}")
            
            # Add simple memory storage after successful persona responses (Task 2.1)
            if self.memory_enabled and self.memory_client and result.get('success'):
                try:
                    memory_text = f"User asked {persona_id}: {message[:50]}..."
                    self.memory_client["add"](memory_text)
                    self.logger.info("Interaction stored in memory")
                except Exception as e:
                    self.logger.warning(f"Memory storage failed: {e}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Request {request_id} failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "persona_id": persona_id,
                "request_id": request_id
            }
        finally:
            # Clean up active request tracking
            if session_id:
                async with self._request_lock:
                    self._active_requests.pop(session_id, None)    
                    
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
        """Check the health of the VALIS system with comprehensive neural matrix monitoring"""
        base_health = {
            "status": "operational",
            "personas_loaded": len(self.personas),
            "providers_available": len(self.config['providers']),
            "personas": list(self.personas.keys()),
            "memory_enabled": self.memory_enabled,
            "memory_connected": bool(self.memory_client),
            "active_sessions": len(self.sessions),
            "total_session_requests": sum(s.get("request_count", 0) for s in self.sessions.values())
        }
        
        # NEURAL MATRIX HEALTH MONITORING (Task 2.4)
        if self.neural_health_monitor:
            try:
                # Update session count in health monitor
                self.neural_health_monitor.metrics['active_sessions'] = len(self.sessions)
                
                # Get comprehensive neural matrix health report
                neural_health = self.neural_health_monitor.get_comprehensive_health_report(self.sessions)
                base_health["neural_matrix_health"] = neural_health
                
                # Update overall status based on neural matrix health
                neural_status = neural_health.get("overall_status", "green")
                if neural_status == "red":
                    base_health["status"] = "degraded"
                elif neural_status == "yellow" and base_health["status"] == "operational":
                    base_health["status"] = "warning"
                    
            except Exception as e:
                self.logger.warning(f"Neural health monitoring failed: {e}")
                base_health["neural_matrix_health"] = {
                    "error": str(e),
                    "overall_status": "unknown"
                }
        
        return base_health
    
    def _compress_neural_context(self, memories: List[str], max_tokens: int = 1000) -> Dict[str, Any]:
        """Compress neural context to prevent token limit exceeded errors"""
        if not memories:
            return {"summary": "No previous conversation history", "memory_count": 0}
        
        # Simple compression: limit number of memories and truncate if needed
        compressed_memories = []
        total_chars = 0
        max_chars = max_tokens * 3  # Rough estimate: 1 token ≈ 3 characters
        
        for memory in memories[:10]:  # Limit to 10 most recent/relevant memories
            if total_chars + len(memory) > max_chars:
                # Truncate this memory to fit
                remaining_chars = max_chars - total_chars
                if remaining_chars > 50:  # Only include if we have at least 50 chars
                    compressed_memories.append(memory[:remaining_chars] + "...")
                break
            compressed_memories.append(memory)
            total_chars += len(memory)
        
        # Create compressed context
        if compressed_memories:
            summary = f"Previous conversation context: {'; '.join(compressed_memories[:3])}"
            if len(compressed_memories) > 3:
                summary += f" (and {len(compressed_memories) - 3} more interactions)"
        else:
            summary = "Limited conversation history available"
        
        return {
            "summary": summary,
            "recent_memories": compressed_memories,
            "memory_count": len(memories),
            "compressed_count": len(compressed_memories),
            "context_compressed": len(compressed_memories) < len(memories)
        }
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions with neural matrix health monitoring"""
        import time
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            if current_time - session_data["last_activity"] > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            self.logger.info(f"Cleaned up expired session: {session_id}")
        
        # NEURAL MATRIX CLEANUP (Task 2.4)
        if self.neural_health_monitor:
            try:
                cleanup_results = self.neural_health_monitor.run_cleanup_protocols(self.sessions)
                self.logger.info(f"Neural matrix cleanup completed: {cleanup_results}")
            except Exception as e:
                self.logger.warning(f"Neural matrix cleanup failed: {e}")
        
        return len(expired_sessions)
    
    def run_neural_health_check(self) -> Dict[str, Any]:
        """Run comprehensive neural matrix health check and optimization"""
        if not self.neural_health_monitor:
            return {"error": "Neural health monitor not available"}
        
        try:
            # Run integrity check
            integrity_results = self.neural_health_monitor.check_neural_integrity()
            
            # Run performance optimization
            optimization_results = self.neural_health_monitor.optimize_performance()
            
            # Run cleanup if needed
            cleanup_results = self.neural_health_monitor.run_cleanup_protocols(self.sessions)
            
            return {
                "integrity": integrity_results,
                "optimization": optimization_results,
                "cleanup": cleanup_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Neural health check failed: {e}")
            return {"error": str(e)}
    
    def get_neural_health_dashboard(self) -> Dict[str, Any]:
        """Get real-time neural matrix health dashboard"""
        if not self.neural_health_monitor:
            return {"error": "Neural health monitor not available"}
        
        try:
            return self.neural_health_monitor.get_comprehensive_health_report(self.sessions)
        except Exception as e:
            self.logger.error(f"Neural health dashboard failed: {e}")
            return {"error": str(e)}

# Convenience function for simple usage
async def ask_persona(persona_id: str, message: str, session_id: Optional[str] = None) -> str:
    """Simple convenience function to get a persona response"""
    engine = VALISEngine()
    result = await engine.get_persona_response(persona_id, message, session_id)
    
    if result.get("success"):
        return result.get("response", "No response generated")
    else:
        return f"Error: {result.get('error', 'Unknown error')}"