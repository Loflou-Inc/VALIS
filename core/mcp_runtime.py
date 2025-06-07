#!/usr/bin/env python3
"""
MCPRuntime - The Brain of VALIS 2.0
Smart prompt composition based on client and persona context
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys
import os

from memory.query_client import memory
from core.model_caps import get_context_limits, get_model_caps, recommend_context_mode
from core.synthetic_cognition_manager import SyntheticCognitionManager
from agents.personality_engine import PersonalityEngine

logger = logging.getLogger("MCPRuntime")

class MCPRuntime:
    """
    Memory-aware Cognitive Processor Runtime
    
    Accepts: prompt, client_id, persona_id
    Returns: composed prompt payload with metadata
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config"
        self.personas = {}
        self.memory_cache = {}
        
        # Initialize synthetic cognition manager
        self.cognition_manager = SyntheticCognitionManager()
        
        # Initialize personality expression engine
        self.personality_engine = PersonalityEngine()
        
        # Session tracking for trait evolution
        self.session_transcripts = {}  # Store transcripts for trait analysis
        self.session_feedback = {}     # Store feedback for trait evolution
        
        # Load persona data
        self._load_personas()
        
        logger.info("🧠 MCPRuntime initialized with synthetic cognition and personality engine")
    
    def compose_prompt(self, prompt: str, client_id: str, persona_id: str, 
                      context_mode: str = "balanced", model_name: str = "local_mistral",
                      session_id: str = None) -> Dict[str, Any]:
        """
        Compose final prompt string with persona and memory context
        
        Args:
            prompt: User input message
            client_id: Client identifier for memory lookup
            persona_id: Persona to use for response
            context_mode: "tight" | "balanced" | "full"
            
        Returns:
            {
                "final_prompt": str,
                "metadata": {
                    "persona_used": str,
                    "context_mode": str,
                    "memory_layers": dict,
                    "token_estimate": int
                }
            }
        """
        
        logger.info(f"=== MCP PROMPT COMPOSITION ===")
        logger.info(f"Persona: {persona_id}")
        logger.info(f"Client: {client_id}")
        logger.info(f"Context Mode: {context_mode}")
        logger.info(f"Input: {prompt[:100]}...")
        
        # Get persona data
        persona_data = self._get_persona_data(persona_id)
        
        # Load memory layers (now with model-aware context)
        memory_layers = self._load_memory_layers(client_id, persona_id, context_mode, model_name)
        
        # Load synthetic cognition state
        cognition_state = None
        if session_id:
            try:
                cognition_state = self.cognition_manager.get_cognition_state(persona_id, session_id)
                logger.info(f"Loaded cognition state: self={cognition_state['self']['confidence']:.2f}, mood={cognition_state['emotion']['mood']}")
            except Exception as e:
                logger.error(f"Failed to load cognition state: {e}")
                cognition_state = None
        
        # Load prompt template
        template = self._load_prompt_template(persona_id)
        
        # Compose final prompt
        final_prompt = self._build_final_prompt(
            template, persona_data, memory_layers, prompt, cognition_state
        )
        
        # Apply personality expression if cognition state is available
        if cognition_state and session_id:
            try:
                final_prompt = self.personality_engine.inject_personality(
                    final_prompt, 
                    persona_data, 
                    cognition_state.get('emotion', {}),
                    cognition_state.get('self', {})
                )
                logger.info(f"Applied personality expression for {persona_id}")
            except Exception as e:
                logger.error(f"Personality injection failed: {e}")
        
        # Estimate tokens (rough)
        token_estimate = len(final_prompt) // 4
        
        metadata = {
            "persona_used": persona_id,
            "context_mode": memory_layers.get("context_mode_used", context_mode),
            "context_mode_requested": context_mode,
            "model_name": model_name,
            "memory_layers": {
                "persona_bio": len(memory_layers.get("persona_bio", [])),
                "canon_memory": len(memory_layers.get("canon_memory", [])),
                "working_memory": len(memory_layers.get("working_memory", [])),
                "client_facts": len(memory_layers.get("client_facts", {}))
            },
            "context_limits": memory_layers.get("context_limits", {}),
            "cognition_state": {
                "enabled": cognition_state is not None,
                "confidence": cognition_state.get('self', {}).get('confidence', 0.5) if cognition_state else 0.5,
                "mood": cognition_state.get('emotion', {}).get('mood', 'neutral') if cognition_state else 'neutral'
            },
            "token_estimate": token_estimate
        }
        
        logger.info(f"Final prompt: {token_estimate} tokens")
        logger.info(f"Memory layers: {metadata['memory_layers']}")
        
        # Structured diagnostic logging
        diagnostic_log = {
            "persona": persona_id,
            "client": client_id,
            "mode": metadata["context_mode"],
            "mode_requested": context_mode,
            "model": model_name,
            "layers": metadata["memory_layers"],
            "tokens_estimated": token_estimate,
            "context_limits": metadata["context_limits"]
        }
        logger.info(f"DIAGNOSTIC: {json.dumps(diagnostic_log)}")
        
        return {
            "final_prompt": final_prompt,
            "metadata": metadata
        }
    
    def _load_personas(self):
        """Load persona definitions from config"""
        try:
            personas_file = Path(self.config_path) / "personas.json"
            if personas_file.exists():
                with open(personas_file, 'r') as f:
                    self.personas = json.load(f)
                logger.info(f"Loaded {len(self.personas)} personas")
            else:
                # Default personas
                self.personas = {
                    "jane": {
                        "name": "Jane Thompson",
                        "role": "HR Business Partner",
                        "bio": "Experienced HR professional with 15 years in talent development"
                    },
                    "kai": {
                        "name": "Kai",
                        "role": "AI Assistant", 
                        "bio": "Helpful AI assistant focused on clear communication"
                    }
                }
                logger.info("Using default personas")
        except Exception as e:
            logger.error(f"Failed to load personas: {e}")
            self.personas = {}
    
    def _get_persona_data(self, persona_id: str) -> Dict[str, Any]:
        """Get persona data or default"""
        return self.personas.get(persona_id, {
            "name": persona_id.title(),
            "role": "AI Assistant",
            "bio": f"AI assistant in {persona_id} mode"
        })
    
    def _load_memory_layers(self, client_id: str, persona_id: str, 
                           context_mode: str, model_name: str) -> Dict[str, Any]:
        """Load memory layers from database based on context mode and model capabilities"""
        
        logger.info(f"Loading memory layers for persona {persona_id}, client {client_id}")
        
        # Get persona data first to check for default context mode
        persona_data = memory.get_persona(persona_id)
        persona_context_mode = None
        if persona_data and persona_data.get('default_context_mode'):
            persona_context_mode = persona_data['default_context_mode']
        
        # Determine final context mode using model capabilities and persona preference
        final_context_mode = recommend_context_mode(model_name, persona_context_mode)
        if context_mode != "balanced":  # User override takes highest priority
            final_context_mode = context_mode
        
        # Get context limits for the final mode
        limits = get_context_limits(final_context_mode)
        
        logger.info(f"Using context mode: {final_context_mode} with limits: {limits}")
        
        try:
            # Load persona bio from database
            persona_bio = []
            if persona_data:
                if persona_data.get('bio'):
                    persona_bio.append(persona_data['bio'])
                if persona_data.get('traits') and limits["persona_bio"] > 1:
                    persona_bio.append(f"Traits: {persona_data['traits']}")
            
            # Load canon memories with context limit
            canon_memories = memory.get_top_canon(persona_id, limits["canon_memory"])
            canon_content = [item["content"] for item in canon_memories]
            
            # Load working memories with context limit
            working_memories = memory.get_recent_working(persona_id, client_id, limits["working_memory"])
            working_content = [item["content"] for item in working_memories]
            
            # Load client facts with context limit
            client_data = memory.get_client(client_id)
            client_facts = {}
            if client_data and limits["client_facts"] > 0:
                if client_data.get('name'):
                    client_facts['name'] = client_data['name']
                if client_data.get('traits'):
                    traits = client_data['traits']
                    if isinstance(traits, str):
                        try:
                            traits = json.loads(traits)
                        except:
                            pass
                    if isinstance(traits, dict):
                        # Limit client facts based on context mode
                        fact_count = 0
                        for key, value in traits.items():
                            if fact_count >= limits["client_facts"]:
                                break
                            client_facts[key] = value
                            fact_count += 1
            
            # Truncate persona bio if needed
            if len(persona_bio) > limits["persona_bio"]:
                persona_bio = persona_bio[:limits["persona_bio"]]
            
            logger.info(f"Loaded: {len(canon_content)} canon, {len(working_content)} working, {len(client_facts)} client facts")
            
            return {
                "persona_bio": persona_bio,
                "canon_memory": canon_content,
                "working_memory": working_content,
                "client_facts": client_facts,
                "context_mode_used": final_context_mode,
                "context_limits": limits
            }
            
        except Exception as e:
            logger.error(f"Failed to load memory from database: {e}")
            # Fallback to minimal data
            return {
                "persona_bio": ["Fallback: Database unavailable"],
                "canon_memory": [],
                "working_memory": [],
                "client_facts": {},
                "context_mode_used": "tight",
                "context_limits": get_context_limits("tight")
            }
    
    def _load_prompt_template(self, persona_id: str) -> str:
        """Load prompt template for persona"""
        
        template_file = Path("core/prompt_templates") / f"{persona_id}.txt"
        
        if template_file.exists():
            try:
                return template_file.read_text()
            except:
                pass
        
        # Default template
        return """You are {persona_name}, {persona_role}.

{persona_bio}

{memory_context}

Current conversation:
User: {user_input}
{persona_name}:"""
    
    def _build_final_prompt(self, template: str, persona_data: Dict, 
                           memory_layers: Dict, user_input: str, cognition_state: Dict = None) -> str:
        """Build the final prompt string"""
        
        # Build memory context section
        memory_context = ""
        
        if memory_layers.get("persona_bio"):
            memory_context += "Background:\n"
            for bio_item in memory_layers["persona_bio"]:
                memory_context += f"- {bio_item}\n"
            memory_context += "\n"
        
        if memory_layers.get("canon_memory"):
            memory_context += "Key Facts:\n"
            for fact in memory_layers["canon_memory"]:
                memory_context += f"- {fact}\n"
            memory_context += "\n"
        
        if memory_layers.get("client_facts"):
            memory_context += "About this user:\n"
            for key, value in memory_layers["client_facts"].items():
                memory_context += f"- {key}: {value}\n"
            memory_context += "\n"
        
        # Add synthetic cognition state if available
        if cognition_state:
            memory_context += "Current state:\n"
            awareness_text = cognition_state.get('integration', {}).get('awareness_text', '')
            if awareness_text:
                memory_context += f"- {awareness_text}\n"
            memory_context += "\n"
        
        # Fill template
        final_prompt = template.format(
            persona_name=persona_data.get("name", "Assistant"),
            persona_role=persona_data.get("role", "AI Assistant"),
            persona_bio=persona_data.get("bio", ""),
            memory_context=memory_context.strip(),
            user_input=user_input
        )
        
        return final_prompt
    def track_session_interaction(self, session_id: str, user_input: str, 
                                 ai_response: str, feedback: Dict[str, Any] = None):
        """Track session interactions for trait evolution analysis"""
        try:
            # Build transcript
            if session_id not in self.session_transcripts:
                self.session_transcripts[session_id] = []
            
            self.session_transcripts[session_id].append({
                "user": user_input,
                "ai": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Track feedback
            if feedback:
                if session_id not in self.session_feedback:
                    self.session_feedback[session_id] = []
                self.session_feedback[session_id].append(feedback)
            
            # Limit memory usage - keep only last 50 interactions per session
            if len(self.session_transcripts[session_id]) > 50:
                self.session_transcripts[session_id] = self.session_transcripts[session_id][-50:]
                
        except Exception as e:
            logger.error(f"Failed to track session interaction: {e}")
    
    def trigger_personality_evolution(self, session_id: str, persona_id: str) -> Dict[str, Any]:
        """
        Trigger personality evolution for a completed session
        Called when session ends or after significant interactions
        """
        try:
            logger.info(f"Triggering personality evolution for {persona_id} session {session_id}")
            
            # Get session data
            transcript_data = self.session_transcripts.get(session_id, [])
            feedback_data = self.session_feedback.get(session_id, [])
            
            # Build full transcript text
            full_transcript = ""
            for interaction in transcript_data:
                full_transcript += f"User: {interaction['user']}\nAI: {interaction['ai']}\n\n"
            
            # Trigger evolution through personality engine
            evolution_result = self.personality_engine.evolve_personality_from_session(
                session_id, persona_id, full_transcript, feedback_data
            )
            
            # Clean up session data to prevent memory bloat
            if session_id in self.session_transcripts:
                del self.session_transcripts[session_id]
            if session_id in self.session_feedback:
                del self.session_feedback[session_id]
            
            logger.info(f"Personality evolution completed for {persona_id}")
            return evolution_result
            
        except Exception as e:
            logger.error(f"Personality evolution failed: {e}")
            return {"error": str(e)}
    
    def get_personality_evolution_status(self, persona_id: str) -> Dict[str, Any]:
        """Get current personality evolution status for a persona"""
        try:
            return self.personality_engine.get_evolving_personality_state(persona_id)
        except Exception as e:
            logger.error(f"Failed to get evolution status: {e}")
            return {"error": str(e)}
