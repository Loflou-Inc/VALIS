"""
VALIS Vault to Main Database Bridge
Connects vault persona management to main VALIS consciousness database
"""

import sys
import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Add paths
sys.path.append('C:\\VALIS\\valis2')
sys.path.append('C:\\VALIS\\vault')

from memory.db import db
from persona_vault import PersonaVault

class VaultDBBridge:
    """
    Bridge between vault persona management and main VALIS database
    """
    
    def __init__(self):
        self.vault = PersonaVault()
    
    def get_main_db_schema(self) -> Dict[str, List[str]]:
        """Get schema of main VALIS database"""
        try:
            # Get all table names
            tables = db.query("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            schema = {}
            for table in tables:
                table_name = table['table_name']
                
                # Get columns for each table
                columns = db.query("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """, (table_name,))
                
                schema[table_name] = [
                    f"{col['column_name']} ({col['data_type']})" 
                    for col in columns
                ]
            
            return schema
            
        except Exception as e:
            print(f"Error getting schema: {e}")
            return {}
    
    def deploy_vault_persona_to_main_db(self, persona_identifier: str) -> str:
        """
        Deploy a vault persona to the main VALIS database
        """
        # Get persona from vault
        blueprint = self.vault.get_persona(persona_identifier)
        if not blueprint:
            raise ValueError(f"Persona '{persona_identifier}' not found in vault")
        
        # Check if persona already exists in main DB
        existing = db.query(
            "SELECT id FROM persona_profiles WHERE name = %s",
            (blueprint['name'],)
        )
        
        if existing:
            raise ValueError(f"Persona '{blueprint['name']}' already exists in main database")
        
        # Convert vault blueprint to main DB format
        persona_data = self._convert_blueprint_to_db_format(blueprint)
        
        # Insert into main database
        persona_id = db.insert('persona_profiles', persona_data)
        
        # Create agent record if table exists
        agent_data = self._create_agent_record(persona_id, blueprint)
        if agent_data:  # Only insert if agent data was created
            agent_id = db.insert('agents', agent_data)
        else:
            agent_id = persona_id  # Use persona_id as fallback
        
        # Insert initial memories if any
        self._insert_persona_memories(agent_id, blueprint)
        
        # Update vault status to deployed
        self.vault.update_status(
            persona_identifier, 
            "active",
            f"Deployed to main VALIS database as {persona_id}"
        )
        
        return persona_id
    
    def _convert_blueprint_to_db_format(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert vault blueprint to main database persona_profiles format
        """
        traits = blueprint.get('traits', {})
        archetypes = blueprint.get('archetypes', [])
        domains = blueprint.get('domain', [])
        
        # Create role based on domains and archetypes
        if 'therapy' in domains or 'The Caregiver' in archetypes:
            role = 'Mental Health Counselor'
        elif 'coaching' in domains or 'The Hero' in archetypes:
            role = 'Personal Development Coach'
        elif 'spiritual' in domains or 'The Sage' in archetypes:
            role = 'Spiritual Guide'
        else:
            role = 'AI Assistant'
        
        # Create bio from blueprint
        bio = self._generate_bio_from_blueprint(blueprint)
        
        # Create system prompt
        system_prompt = self._generate_prompt_template(blueprint)
        
        # Create persona data matching actual schema
        persona_data = {
            'id': str(uuid.uuid4()),
            'name': blueprint['name'],
            'role': role,
            'bio': bio,
            'system_prompt': system_prompt,
            'traits': json.dumps({
                'archetypes': archetypes,
                'domains': domains,
                'tone': traits.get('tone', 'balanced'),
                'communication_style': traits.get('communication_style', {}),
                'vault_source': True
            }),
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
            'default_context_mode': 'comprehensive'
        }
        
        return persona_data
    
    def _generate_bio_from_blueprint(self, blueprint: Dict[str, Any]) -> str:
        """
        Generate bio text from blueprint data
        """
        name = blueprint['name']
        traits = blueprint.get('traits', {})
        archetypes = blueprint.get('archetypes', [])
        domains = blueprint.get('domain', [])
        tone = traits.get('tone', 'balanced')
        
        bio_parts = [f"{name} is a {tone} AI assistant"]
        
        if archetypes:
            archetype_str = ', '.join(archetypes)
            bio_parts.append(f"embodying the archetypes of {archetype_str}")
        
        if domains:
            domain_str = ', '.join(domains)
            bio_parts.append(f"with expertise in {domain_str}")
        
        # Add memory seeds as background
        memory_seeds = blueprint.get('memory_seeds', [])
        key_concepts = [
            seed['content'] for seed in memory_seeds 
            if seed.get('type') == 'key_concept'
        ]
        
        if key_concepts:
            bio_parts.append(f"Known for understanding {', '.join(key_concepts[:3])}")
        
        bio_parts.append(f"Created from {len(blueprint.get('source_material', []))} source materials")
        
        return '. '.join(bio_parts) + '.'
    
    def _generate_prompt_template(self, blueprint: Dict[str, Any]) -> str:
        """
        Generate prompt template for the persona
        """
        name = blueprint['name']
        traits = blueprint.get('traits', {})
        archetypes = blueprint.get('archetypes', [])
        boundaries = blueprint.get('boundaries', {})
        
        template_parts = [
            f"You are {name}, an AI assistant with a unique personality.",
            f"Your communication style is {traits.get('tone', 'balanced')}."
        ]
        
        if archetypes:
            template_parts.append(f"You embody the archetypes of {', '.join(archetypes)}.")
        
        if boundaries.get('use_mystical_language'):
            template_parts.append("You may use symbolic and mystical language when appropriate.")
        
        if boundaries.get('allow_direct_advice'):
            template_parts.append("You can provide direct advice and guidance.")
        
        template_parts.append("Respond authentically based on your personality and background.")
        
        return ' '.join(template_parts)
    
    def _create_agent_record(self, persona_id: str, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create agent record for the persona - but first check if agents table exists
        """
        # Check if agents table exists
        try:
            db.query("SELECT COUNT(*) FROM agents LIMIT 1")
            agents_table_exists = True
        except:
            agents_table_exists = False
            
        if not agents_table_exists:
            print("Note: agents table does not exist, skipping agent record creation")
            return {}
        
        fusion_metadata = blueprint.get('fusion_metadata', {})
        
        agent_data = {
            'id': str(uuid.uuid4()),
            'name': blueprint['name'],
            'persona_id': persona_id,
            'status': 'active',
            'created_at': datetime.now(timezone.utc),
            'last_interaction': datetime.now(timezone.utc),
            'interaction_count': 0,
            'config': json.dumps({
                'blueprint_source': 'vault_deployment',
                'fusion_confidence': fusion_metadata.get('fusion_confidence', 0.0),
                'archetypes': blueprint.get('archetypes', []),
                'domains': blueprint.get('domain', []),
                'vault_persona_id': blueprint.get('id')
            })
        }
        
        return agent_data
    
    def _insert_persona_memories(self, agent_id: str, blueprint: Dict[str, Any]) -> None:
        """
        Insert persona memory seeds into main database
        """
        memory_seeds = blueprint.get('memory_seeds', [])
        
        for seed in memory_seeds:
            memory_data = {
                'id': str(uuid.uuid4()),
                'persona_id': agent_id,  # Use persona_id instead of agent_uuid
                'content': seed.get('content', ''),
                'tags': [seed.get('type', 'vault_seed')],
                'category': self._map_memory_type(seed.get('type', 'episodic')),
                'relevance_score': float(seed.get('importance', 1.0)) / 10.0,
                'token_estimate': len(seed.get('content', '').split()) * 2,
                'created_at': datetime.now(timezone.utc),
                'last_used': datetime.now(timezone.utc),
                'is_symbolic': seed.get('type') in ['key_concept', 'visual_memory'],
                'symbolic_type': seed.get('type'),
                'resonance_score': float(seed.get('importance', 1.0)) / 10.0,
                'symbolic_tags': [seed.get('type', 'vault_seed')],
                'source_content_ids': []
            }
            
            try:
                db.insert('canon_memories', memory_data)
                print(f"Inserted memory: {seed.get('content', '')[:50]}...")
            except Exception as e:
                print(f"Warning: Failed to insert memory seed: {e}")
                print(f"Memory data keys: {list(memory_data.keys())}")
    
    def _map_memory_type(self, seed_type: str) -> str:
        """Map vault seed types to main DB memory types"""
        type_mapping = {
            'key_concept': 'canonical',
            'named_entity': 'canonical',
            'visual_memory': 'episodic',
            'core_value': 'canonical',
            'manual': 'canonical'
        }
        return type_mapping.get(seed_type, 'episodic')
    
    def list_vault_vs_main_personas(self) -> Dict[str, List[Dict]]:
        """
        Compare personas in vault vs main database
        """
        # Get vault personas
        vault_personas = self.vault.list_personas()
        
        # Get main DB personas
        main_personas = db.query("SELECT id, name, role, created_at FROM persona_profiles ORDER BY name")
        
        return {
            'vault_personas': vault_personas,
            'main_db_personas': main_personas,
            'vault_count': len(vault_personas),
            'main_db_count': len(main_personas)
        }
    
    def sync_persona_status(self, vault_identifier: str, main_db_id: str) -> bool:
        """
        Sync status between vault and main database
        """
        try:
            # Get vault persona status
            vault_personas = self.vault.list_personas()
            vault_persona = next(
                (p for p in vault_personas if p['name'] == vault_identifier or p['uuid'] == vault_identifier),
                None
            )
            
            if not vault_persona:
                return False
            
            # Update main database agent status
            status_mapping = {
                'active': 'active',
                'draft': 'inactive',
                'archived': 'archived',
                'locked': 'locked'
            }
            
            main_status = status_mapping.get(vault_persona['status'], 'active')
            
            affected_rows = db.execute(
                "UPDATE agents SET status = %s, updated_at = %s WHERE persona_id = %s",
                (main_status, datetime.now(timezone.utc), main_db_id)
            )
            
            return affected_rows > 0
            
        except Exception as e:
            print(f"Error syncing status: {e}")
            return False


def deploy_jane_from_vault():
    """
    Deploy Jane from vault to main VALIS database
    """
    print("=== DEPLOYING JANE FROM VAULT TO MAIN VALIS DATABASE ===")
    
    bridge = VaultDBBridge()
    
    try:
        # Check current state
        comparison = bridge.list_vault_vs_main_personas()
        print(f"Vault personas: {comparison['vault_count']}")
        print(f"Main DB personas: {comparison['main_db_count']}")
        
        # Find Jane in vault
        jane_found = False
        for persona in comparison['vault_personas']:
            if persona['name'].lower() == 'jane':
                jane_found = True
                print(f"Found Jane in vault: {persona['uuid']} (status: {persona['status']})")
                break
        
        if not jane_found:
            print("ERROR: Jane not found in vault")
            return False
        
        # Deploy Jane
        print("Deploying Jane to main database...")
        persona_id = bridge.deploy_vault_persona_to_main_db('Jane')
        print(f"SUCCESS: Jane deployed with ID {persona_id}")
        
        # Verify deployment
        jane_main = db.query("SELECT * FROM persona_profiles WHERE id = %s", (persona_id,))
        if jane_main:
            jane_data = jane_main[0]
            print(f"Verified: {jane_data['name']} - {jane_data['role']}")
            print(f"Bio: {jane_data['bio'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        return False


def show_main_db_schema():
    """
    Show the main VALIS database schema
    """
    print("=== MAIN VALIS DATABASE SCHEMA ===")
    
    bridge = VaultDBBridge()
    schema = bridge.get_main_db_schema()
    
    for table_name, columns in schema.items():
        print(f"\n{table_name}:")
        for column in columns:
            print(f"  - {column}")


if __name__ == "__main__":
    print("=== VALIS VAULT TO MAIN DATABASE BRIDGE ===")
    
    # Show schema
    show_main_db_schema()
    
    # Deploy Jane
    success = deploy_jane_from_vault()
    
    if success:
        print("\n=== BRIDGE OPERATIONAL - JANE IS NOW IN MAIN VALIS DATABASE ===")
    else:
        print("\n=== BRIDGE FAILED - MANUAL INTERVENTION REQUIRED ===")
