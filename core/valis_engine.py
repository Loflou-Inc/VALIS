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
from typing import Dict, List, Optional, Any
from pathlib import Path

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
        
        # Load personas and providers
        self._initialize_personas()
        self._initialize_providers()
        
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
        """Get a response from a specific persona"""
        if persona_id not in self.personas:
            return {
                "success": False,
                "error": f"Unknown persona: {persona_id}",
                "available_personas": list(self.personas.keys())
            }
        
        persona = self.personas[persona_id]
        
        try:
            # Get response through provider cascade
            result = await self.provider_manager.get_response(
                persona=persona,
                message=message,
                session_id=session_id,
                context=context
            )
            
            self.logger.info(f"Response generated for {persona_id} via {result.get('provider_used', 'unknown')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting response for {persona_id}: {e}")
            return {"success": False, "error": str(e), "persona_id": persona_id}    
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

# Convenience function for simple usage
async def ask_persona(persona_id: str, message: str, session_id: Optional[str] = None) -> str:
    """Simple convenience function to get a persona response"""
    engine = VALISEngine()
    result = await engine.get_persona_response(persona_id, message, session_id)
    
    if result.get("success"):
        return result.get("response", "No response generated")
    else:
        return f"Error: {result.get('error', 'Unknown error')}"