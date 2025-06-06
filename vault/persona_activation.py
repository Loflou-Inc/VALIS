"""
VALIS Persona Activation Interface
Integration layer between persona blueprints and VALIS runtime
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import uuid

# Add VALIS modules to path
sys.path.append('C:\\VALIS\\valis2')
sys.path.append('C:\\VALIS\\vault')

from persona_vault import PersonaVault

class PersonaActivationInterface:
    """
    Bridges persona blueprints with VALIS consciousness runtime
    """
    
    def __init__(self):
        self.vault = PersonaVault()
        self.active_personas = {}  # session_id -> persona_runtime
    
    def load_persona_blueprint(self, persona_identifier: str) -> Dict[str, Any]:
        """
        Load and validate a persona blueprint for activation
        """
        blueprint = self.vault.get_persona(persona_identifier)
        if not blueprint:
            raise ValueError(f"Persona '{persona_identifier}' not found in vault")
        
        # Validate blueprint has required fields for VALIS runtime
        required_fields = ['name', 'traits', 'archetypes', 'memory_seeds']
        missing_fields = [field for field in required_fields if field not in blueprint]
        
        if missing_fields:
            raise ValueError(f"Blueprint missing required fields: {missing_fields}")
        
        return blueprint
    
    def create_valis_persona_config(self, blueprint: Dict[str, Any], 
                                   session_id: str) -> Dict[str, Any]:
        """
        Convert persona blueprint into VALIS runtime configuration
        """
        # Extract persona traits
        traits = blueprint.get('traits', {})
        archetypes = blueprint.get('archetypes', [])
        domains = blueprint.get('domain', [])
        boundaries = blueprint.get('boundaries', {})
        memory_seeds = blueprint.get('memory_seeds', [])
        
        # Create VALIS agent configuration
        valis_config = {
            "agent_id": blueprint.get('id', str(uuid.uuid4())),
            "session_id": session_id,
            "persona_name": blueprint.get('name', 'Unknown'),
            "persona_type": blueprint.get('type', 'interface'),
            
            # Core traits
            "personality": {
                "tone": traits.get('tone', 'balanced'),
                "personality_scores": traits.get('personality_scores', {}),
                "emotional_baseline": traits.get('emotional_baseline', {}),
                "communication_style": traits.get('communication_style', {})
            },
            
            # Archetypal influences
            "archetypes": {
                "primary": archetypes[0] if archetypes else None,
                "secondary": archetypes[1] if len(archetypes) > 1 else None,
                "all_archetypes": archetypes
            },
            
            # Domain expertise
            "domains": domains,
            
            # Operational boundaries
            "boundaries": {
                "allow_direct_advice": boundaries.get('allow_direct_advice', True),
                "use_mystical_language": boundaries.get('use_mystical_language', False),
                "confidence_level": boundaries.get('confidence_level', 'moderate'),
                "formality_level": boundaries.get('formality_level', 'casual')
            },
            
            # Memory configuration
            "memory_config": {
                "mode": blueprint.get('memory_mode', 'canonical+reflective'),
                "dreams_enabled": blueprint.get('dreams_enabled', True),
                "replay_mode": blueprint.get('replay_mode', 'standard'),
                "symbolic_awareness": traits.get('symbolic_awareness', True)
            },
            
            # Initial memory seeds
            "initial_memories": self._convert_memory_seeds(memory_seeds),
            
            # Activation metadata
            "activation_metadata": {
                "blueprint_source": blueprint.get('source_material', []),
                "fusion_confidence": blueprint.get('fusion_metadata', {}).get('fusion_confidence', 0.0),
                "activated_at": datetime.now(timezone.utc).isoformat(),
                "vault_status": "active"
            }
        }
        
        return valis_config
    
    def _convert_memory_seeds(self, memory_seeds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert persona memory seeds into VALIS memory format
        """
        valis_memories = []
        
        for seed in memory_seeds:
            seed_type = seed.get('type', 'unknown')
            content = seed.get('content', '')
            source = seed.get('source', 'persona_blueprint')
            importance = seed.get('importance', 1.0)
            
            # Convert to VALIS memory format
            valis_memory = {
                "uuid": str(uuid.uuid4()),
                "memory_type": self._map_memory_type(seed_type),
                "content": content,
                "is_symbolic": seed_type in ['key_concept', 'visual_memory'],
                "symbolic_type": seed_type,
                "resonance_score": float(importance) / 10.0,  # Normalize to 0-1
                "source": source,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "agent_uuid": None,  # Will be set when assigned to agent
                "memory_tags": [seed_type, "persona_seed"]
            }
            
            valis_memories.append(valis_memory)
        
        return valis_memories
    
    def _map_memory_type(self, seed_type: str) -> str:
        """
        Map persona seed types to VALIS memory types
        """
        type_mapping = {
            "key_concept": "canonical",
            "named_entity": "canonical", 
            "visual_memory": "episodic",
            "core_value": "canonical",
            "manual": "canonical"
        }
        
        return type_mapping.get(seed_type, "episodic")
    
    def create_dreamfilter_config(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create dreamfilter configuration based on persona traits
        """
        traits = blueprint.get('traits', {})
        archetypes = blueprint.get('archetypes', [])
        boundaries = blueprint.get('boundaries', {})
        
        # Determine symbolic transformation style
        symbolic_style = "balanced"
        if "The Sage" in archetypes:
            symbolic_style = "wisdom_focused"
        elif "The Caregiver" in archetypes:
            symbolic_style = "nurturing_metaphors"
        elif "The Magician" in archetypes:
            symbolic_style = "mystical_heavy"
        elif "The Creator" in archetypes:
            symbolic_style = "creative_imagery"
        
        # Configure dreamfilter parameters
        dreamfilter_config = {
            "symbolic_transformation": {
                "style": symbolic_style,
                "intensity": 0.7 if boundaries.get('use_mystical_language') else 0.4,
                "archetypal_bias": archetypes[:2] if archetypes else []
            },
            
            "metaphor_generation": {
                "enabled": True,
                "complexity": traits.get('communication_style', {}).get('vocabulary', 'moderate'),
                "emotional_coloring": traits.get('emotional_baseline', {})
            },
            
            "symbolic_memory_integration": {
                "enabled": traits.get('symbolic_awareness', True),
                "resonance_threshold": 0.3,
                "max_symbols_per_response": 3
            }
        }
        
        return dreamfilter_config
    
    def activate_persona(self, persona_identifier: str, session_id: str = None) -> Dict[str, Any]:
        """
        Fully activate a persona in the VALIS runtime
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Load blueprint
        blueprint = self.load_persona_blueprint(persona_identifier)
        
        # Create VALIS configuration
        valis_config = self.create_valis_persona_config(blueprint, session_id)
        
        # Create dreamfilter configuration
        dreamfilter_config = self.create_dreamfilter_config(blueprint)
        
        # Create persona runtime instance
        persona_runtime = {
            "session_id": session_id,
            "persona_name": blueprint['name'],
            "valis_config": valis_config,
            "dreamfilter_config": dreamfilter_config,
            "blueprint": blueprint,
            "activation_time": datetime.now(timezone.utc).isoformat(),
            "status": "active"
        }
        
        # Store in active personas
        self.active_personas[session_id] = persona_runtime
        
        # Update vault session
        self.vault.start_session(persona_identifier, session_id)
        
        return persona_runtime
    
    def deactivate_persona(self, session_id: str, interaction_count: int = 0) -> bool:
        """
        Deactivate an active persona
        """
        if session_id not in self.active_personas:
            return False
        
        # End vault session
        self.vault.end_session(session_id, interaction_count)
        
        # Remove from active personas
        del self.active_personas[session_id]
        
        return True
    
    def get_active_persona(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an active persona by session ID
        """
        return self.active_personas.get(session_id)
    
    def list_active_personas(self) -> List[Dict[str, Any]]:
        """
        List all currently active personas
        """
        active_list = []
        
        for session_id, persona_runtime in self.active_personas.items():
            active_list.append({
                "session_id": session_id,
                "persona_name": persona_runtime["persona_name"],
                "activation_time": persona_runtime["activation_time"],
                "status": persona_runtime["status"]
            })
        
        return active_list
    
    def inject_persona_memory(self, session_id: str, memory_content: str, 
                            memory_type: str = "episodic") -> bool:
        """
        Inject a new memory into an active persona
        """
        if session_id not in self.active_personas:
            return False
        
        persona_runtime = self.active_personas[session_id]
        
        # Create new memory
        new_memory = {
            "uuid": str(uuid.uuid4()),
            "memory_type": memory_type,
            "content": memory_content,
            "is_symbolic": False,
            "resonance_score": 0.5,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "agent_uuid": persona_runtime["valis_config"]["agent_id"],
            "memory_tags": ["runtime_injection"]
        }
        
        # Add to persona's memory collection
        if "runtime_memories" not in persona_runtime:
            persona_runtime["runtime_memories"] = []
        
        persona_runtime["runtime_memories"].append(new_memory)
        
        return True
    
    def update_persona_trait(self, session_id: str, trait_path: str, 
                           new_value: Any) -> bool:
        """
        Update a persona trait during runtime
        """
        if session_id not in self.active_personas:
            return False
        
        persona_runtime = self.active_personas[session_id]
        
        # Navigate to the trait using dot notation
        parts = trait_path.split('.')
        target = persona_runtime["valis_config"]
        
        for part in parts[:-1]:
            if part not in target:
                return False
            target = target[part]
        
        # Update the final value
        target[parts[-1]] = new_value
        
        # Log the change
        if "trait_changes" not in persona_runtime:
            persona_runtime["trait_changes"] = []
        
        persona_runtime["trait_changes"].append({
            "trait_path": trait_path,
            "old_value": target.get(parts[-1]),
            "new_value": new_value,
            "changed_at": datetime.now(timezone.utc).isoformat()
        })
        
        return True


class VALISPersonaSelector:
    """
    Persona selector override for VALIS MCP Server integration
    """
    
    def __init__(self):
        self.activation_interface = PersonaActivationInterface()
    
    def select_persona(self, persona_identifier: str = None, 
                      user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Select and configure a persona for VALIS interaction
        """
        if persona_identifier:
            # Explicit persona selection
            try:
                persona_runtime = self.activation_interface.activate_persona(persona_identifier)
                return persona_runtime["valis_config"]
            except Exception as e:
                print(f"Failed to activate persona '{persona_identifier}': {e}")
                return self._get_default_config()
        
        elif user_preferences:
            # Select persona based on user preferences
            return self._select_by_preferences(user_preferences)
        
        else:
            # Default configuration
            return self._get_default_config()
    
    def _select_by_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select persona based on user preferences
        """
        # Get available personas from vault
        vault = PersonaVault()
        personas = vault.list_personas(status="active")
        
        if not personas:
            return self._get_default_config()
        
        # Simple matching based on domains
        preferred_domains = preferences.get('domains', [])
        
        best_match = None
        best_score = 0
        
        for persona in personas:
            persona_domains = persona.get('domains', [])
            match_score = len(set(preferred_domains) & set(persona_domains))
            
            if match_score > best_score:
                best_score = match_score
                best_match = persona
        
        if best_match:
            try:
                persona_runtime = self.activation_interface.activate_persona(best_match['uuid'])
                return persona_runtime["valis_config"]
            except Exception as e:
                print(f"Failed to activate matched persona: {e}")
        
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default VALIS configuration when no persona is available
        """
        return {
            "agent_id": str(uuid.uuid4()),
            "session_id": str(uuid.uuid4()),
            "persona_name": "Default VALIS",
            "persona_type": "assistant",
            "personality": {
                "tone": "helpful, balanced",
                "personality_scores": {},
                "emotional_baseline": {},
                "communication_style": {"vocabulary": "accessible"}
            },
            "archetypes": {"primary": None, "secondary": None, "all_archetypes": []},
            "domains": ["general"],
            "boundaries": {
                "allow_direct_advice": True,
                "use_mystical_language": False,
                "confidence_level": "moderate",
                "formality_level": "casual"
            },
            "memory_config": {
                "mode": "standard",
                "dreams_enabled": False,
                "replay_mode": "none",
                "symbolic_awareness": False
            },
            "initial_memories": []
        }


# Example usage and testing
if __name__ == "__main__":
    print("=== VALIS PERSONA ACTIVATION INTERFACE ===")
    
    # Initialize activation interface
    activator = PersonaActivationInterface()
    
    # Test persona activation (if Jane exists)
    try:
        persona_runtime = activator.activate_persona("Jane")
        print(f"Activated persona: {persona_runtime['persona_name']}")
        print(f"Session ID: {persona_runtime['session_id']}")
        print(f"Archetypes: {persona_runtime['valis_config']['archetypes']['all_archetypes']}")
        print(f"Domains: {persona_runtime['valis_config']['domains']}")
        
        # Test memory injection
        success = activator.inject_persona_memory(
            persona_runtime['session_id'],
            "This is a test memory injected during runtime",
            "episodic"
        )
        print(f"Memory injection: {'Success' if success else 'Failed'}")
        
        # Test trait update
        success = activator.update_persona_trait(
            persona_runtime['session_id'],
            "personality.tone",
            "warm, understanding"
        )
        print(f"Trait update: {'Success' if success else 'Failed'}")
        
        # List active personas
        active = activator.list_active_personas()
        print(f"Active personas: {len(active)}")
        
        # Deactivate
        activator.deactivate_persona(persona_runtime['session_id'])
        print("Persona deactivated")
        
    except Exception as e:
        print(f"Persona activation test failed: {e}")
    
    # Test persona selector
    selector = VALISPersonaSelector()
    config = selector.select_persona("Jane")
    print(f"Selected persona config: {config['persona_name']}")
    
    print("\n=== PERSONA ACTIVATION INTERFACE ONLINE ===")
