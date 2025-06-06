"""
VALIS Operator Tools - Persona Preview & Testing CLI
Internal tools for persona management and testing
"""

import os
import sys
import json
import requests
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse

# Add VALIS modules to path
sys.path.append('C:\\VALIS\\valis2')
sys.path.append('C:\\VALIS\\vault')

from persona_vault import PersonaVault
from fission.ingest import FissionIngestionEngine
from fission.fuse import FissionFusionEngine

class VALISOperatorTools:
    """
    CLI tools for VALIS operators to manage and test personas
    """
    
    def __init__(self):
        self.vault = PersonaVault()
        self.ingester = FissionIngestionEngine()
        self.fusioner = FissionFusionEngine()
        self.fission_api_base = "http://localhost:8001/api/fission"
        self.valis_api_base = "http://localhost:8000/api"
    
    def create_persona_from_files(self, file_paths: List[str], persona_name: str, 
                                 auto_activate: bool = False) -> str:
        """
        Create a persona from local files using Mr. Fission pipeline
        """
        print(f"Creating persona '{persona_name}' from {len(file_paths)} files...")
        
        # Validate files exist
        for path in file_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"File not found: {path}")
        
        try:
            # Step 1: Ingest files
            print("Step 1: Ingesting files...")
            if len(file_paths) == 1:
                ingestion_result = self.ingester.ingest_file(file_paths[0])
            else:
                ingestion_result = self.ingester.batch_ingest(file_paths)
            
            print(f"  Ingested {len(ingestion_result.get('files', [ingestion_result]))} files")
            
            # Step 2: Fuse persona
            print("Step 2: Fusing persona blueprint...")
            blueprint = self.fusioner.fuse_persona(ingestion_result, persona_name)
            
            fusion_confidence = blueprint.schema["fusion_metadata"]["fusion_confidence"]
            print(f"  Fusion confidence: {fusion_confidence:.2f}")
            
            # Step 3: Store in vault
            print("Step 3: Storing in persona vault...")
            status = "active" if auto_activate else "draft"
            persona_uuid = self.vault.store_persona(blueprint.schema, status=status)
            
            print(f"  Persona stored: {persona_uuid}")
            print(f"  Status: {status}")
            
            return persona_uuid
            
        except Exception as e:
            print(f"Error creating persona: {e}")
            raise
    
    def preview_persona(self, identifier: str) -> Dict[str, Any]:
        """
        Generate a detailed preview of a persona
        """
        print(f"Generating preview for persona: {identifier}")
        
        # Get persona from vault
        blueprint_data = self.vault.get_persona(identifier)
        if not blueprint_data:
            raise ValueError(f"Persona '{identifier}' not found in vault")
        
        # Create blueprint object for preview
        from fission.fuse import PersonaBlueprint
        blueprint = PersonaBlueprint()
        blueprint.schema = blueprint_data
        
        # Generate preview
        preview = self.fusioner.preview_persona(blueprint)
        
        # Add vault metadata
        personas = self.vault.list_personas()
        vault_data = next((p for p in personas if p['name'] == identifier or p['uuid'] == identifier), {})
        
        preview['vault_metadata'] = {
            'status': vault_data.get('status', 'unknown'),
            'created_at': vault_data.get('created_at'),
            'updated_at': vault_data.get('updated_at'),
            'version_count': vault_data.get('version_count', 1),
            'is_forkable': vault_data.get('is_forkable', True)
        }
        
        return preview
    
    def test_persona_sandbox(self, identifier: str, test_inputs: List[str]) -> Dict[str, Any]:
        """
        Test a persona in a sandbox environment
        """
        print(f"Testing persona '{identifier}' in sandbox...")
        
        # Start sandbox session
        session_id = self.vault.start_session(identifier, "operator_test")
        print(f"Started sandbox session: {session_id}")
        
        test_results = {
            "session_id": session_id,
            "persona": identifier,
            "test_inputs": test_inputs,
            "responses": [],
            "started_at": datetime.now().isoformat()
        }
        
        try:
            # Get persona blueprint
            blueprint = self.vault.get_persona(identifier)
            if not blueprint:
                raise ValueError(f"Persona '{identifier}' not found")
            
            # Simulate responses based on persona traits
            for i, test_input in enumerate(test_inputs):
                print(f"  Test {i+1}: {test_input[:50]}...")
                
                # Generate simulated response based on persona characteristics
                response = self._simulate_persona_response(blueprint, test_input)
                
                test_results["responses"].append({
                    "input": test_input,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                print(f"    Response: {response[:100]}...")
        
        finally:
            # End session
            self.vault.end_session(session_id, len(test_inputs))
            test_results["ended_at"] = datetime.now().isoformat()
        
        return test_results
    
    def _simulate_persona_response(self, blueprint: Dict[str, Any], input_text: str) -> str:
        """
        Simulate a persona response based on blueprint characteristics
        """
        # Extract persona traits
        tone = blueprint.get("traits", {}).get("tone", "balanced")
        archetypes = blueprint.get("archetypes", [])
        domains = blueprint.get("domain", [])
        comm_style = blueprint.get("traits", {}).get("communication_style", {})
        
        # Build response based on traits
        response_parts = []
        
        # Add greeting based on archetypes
        if "The Caregiver" in archetypes:
            response_parts.append("Thank you for sharing that with me.")
        elif "The Sage" in archetypes:
            response_parts.append("That's an interesting perspective to explore.")
        elif "The Hero" in archetypes:
            response_parts.append("I appreciate your courage in bringing this up.")
        else:
            response_parts.append("I hear what you're saying.")
        
        # Add domain-specific response
        if "therapy" in domains:
            response_parts.append("This sounds like an opportunity for deeper understanding.")
        elif "coaching" in domains:
            response_parts.append("What would success look like for you in this situation?")
        elif "spiritual" in domains:
            response_parts.append("There may be wisdom to be found in this experience.")
        else:
            response_parts.append("Let's explore this together.")
        
        # Adjust based on communication style
        if comm_style.get("vocabulary") == "sophisticated":
            response_parts.append("This presents intriguing possibilities for growth.")
        elif comm_style.get("expressiveness") == "high":
            response_parts.append("I'm excited to help you work through this!")
        else:
            response_parts.append("I'm here to support you.")
        
        return " ".join(response_parts)
    
    def list_vault_personas(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all personas in the vault with metadata
        """
        personas = self.vault.list_personas(status=status)
        
        print(f"\nPersonas in vault ({len(personas)} total):")
        print("-" * 80)
        
        for persona in personas:
            print(f"Name: {persona['name']}")
            print(f"UUID: {persona['uuid']}")
            print(f"Type: {persona['type']} | Status: {persona['status']}")
            print(f"Archetypes: {', '.join(persona.get('archetypes', []))}")
            print(f"Domains: {', '.join(persona.get('domains', []))}")
            print(f"Confidence: {persona.get('fusion_confidence', 0):.2f}")
            print(f"Created: {persona['created_at']}")
            print(f"Versions: {persona['version_count']}")
            print("-" * 80)
        
        return personas
    
    def activate_persona(self, identifier: str) -> bool:
        """
        Activate a persona for production use
        """
        print(f"Activating persona: {identifier}")
        
        result = self.vault.update_status(
            identifier, 
            "active", 
            "Activated by operator for production use"
        )
        
        if result:
            print(f"  Persona '{identifier}' is now active")
        else:
            print(f"  Failed to activate persona '{identifier}'")
        
        return result
    
    def archive_persona(self, identifier: str, reason: str = None) -> bool:
        """
        Archive a persona
        """
        print(f"Archiving persona: {identifier}")
        
        description = f"Archived by operator: {reason}" if reason else "Archived by operator"
        result = self.vault.update_status(identifier, "archived", description)
        
        if result:
            print(f"  Persona '{identifier}' has been archived")
        else:
            print(f"  Failed to archive persona '{identifier}'")
        
        return result
    
    def fork_persona(self, source_identifier: str, new_name: str, 
                    changes: Dict[str, Any] = None) -> str:
        """
        Create a fork of an existing persona
        """
        print(f"Forking persona '{source_identifier}' -> '{new_name}'")
        
        try:
            new_uuid = self.vault.fork_persona(source_identifier, new_name, changes)
            print(f"  Fork created: {new_uuid}")
            return new_uuid
        except Exception as e:
            print(f"  Fork failed: {e}")
            raise
    
    def show_persona_history(self, identifier: str) -> List[Dict[str, Any]]:
        """
        Show the version history of a persona
        """
        history = self.vault.get_persona_history(identifier)
        
        print(f"\nHistory for persona: {identifier}")
        print("-" * 60)
        
        for entry in history:
            print(f"Version {entry['version_number']} - {entry['timestamp']}")
            print(f"  Type: {entry['change_type']}")
            print(f"  Description: {entry['change_description']}")
            print(f"  Hash: {entry['blueprint_hash'][:16]}...")
            print("-" * 60)
        
        return history
    
    def vault_stats(self) -> Dict[str, Any]:
        """
        Show vault statistics
        """
        stats = self.vault.get_vault_stats()
        
        print("\nVault Statistics:")
        print("=" * 40)
        print(f"Total personas: {stats['total_personas']}")
        print(f"Active sessions: {stats['active_sessions']}")
        
        print(f"\nPersonas by status:")
        for status, count in stats['personas_by_status'].items():
            print(f"  {status}: {count}")
        
        print(f"\nRecent personas:")
        for persona in stats['recent_personas']:
            print(f"  {persona['name']} - {persona['created_at']}")
        
        return stats


def main():
    """
    Main CLI interface for VALIS operator tools
    """
    parser = argparse.ArgumentParser(description="VALIS Operator Tools - Persona Management")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create persona command
    create_parser = subparsers.add_parser('create', help='Create persona from files')
    create_parser.add_argument('name', help='Persona name')
    create_parser.add_argument('files', nargs='+', help='Source files')
    create_parser.add_argument('--activate', action='store_true', help='Activate immediately')
    
    # Preview persona command
    preview_parser = subparsers.add_parser('preview', help='Preview persona')
    preview_parser.add_argument('identifier', help='Persona name or UUID')
    
    # Test persona command
    test_parser = subparsers.add_parser('test', help='Test persona in sandbox')
    test_parser.add_argument('identifier', help='Persona name or UUID')
    test_parser.add_argument('--inputs', nargs='+', default=[
        "I'm feeling overwhelmed today",
        "Can you help me understand my emotions?",
        "What should I do when I'm stressed?"
    ], help='Test inputs')
    
    # List personas command
    list_parser = subparsers.add_parser('list', help='List personas in vault')
    list_parser.add_argument('--status', help='Filter by status')
    
    # Activate persona command
    activate_parser = subparsers.add_parser('activate', help='Activate persona')
    activate_parser.add_argument('identifier', help='Persona name or UUID')
    
    # Archive persona command
    archive_parser = subparsers.add_parser('archive', help='Archive persona')
    archive_parser.add_argument('identifier', help='Persona name or UUID')
    archive_parser.add_argument('--reason', help='Reason for archiving')
    
    # Fork persona command
    fork_parser = subparsers.add_parser('fork', help='Fork persona')
    fork_parser.add_argument('source', help='Source persona name or UUID')
    fork_parser.add_argument('new_name', help='New persona name')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show persona history')
    history_parser.add_argument('identifier', help='Persona name or UUID')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show vault statistics')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize operator tools
    tools = VALISOperatorTools()
    
    try:
        if args.command == 'create':
            persona_uuid = tools.create_persona_from_files(
                args.files, args.name, args.activate
            )
            print(f"\nPersona created: {persona_uuid}")
            
        elif args.command == 'preview':
            preview = tools.preview_persona(args.identifier)
            print(f"\nPersona Preview: {preview['name']}")
            print(f"Summary: {preview['summary']}")
            print(f"Sample Quote: \"{preview['sample_quote']}\"")
            print(f"Sample Response: \"{preview['sample_response']}\"")
            print(f"Confidence: {preview['confidence']:.2f}")
            print(f"Status: {preview['vault_metadata']['status']}")
            
        elif args.command == 'test':
            results = tools.test_persona_sandbox(args.identifier, args.inputs)
            print(f"\nSandbox Test Results:")
            print(f"Session: {results['session_id']}")
            for i, result in enumerate(results['responses']):
                print(f"\nTest {i+1}:")
                print(f"Input: {result['input']}")
                print(f"Response: {result['response']}")
            
        elif args.command == 'list':
            tools.list_vault_personas(args.status)
            
        elif args.command == 'activate':
            tools.activate_persona(args.identifier)
            
        elif args.command == 'archive':
            tools.archive_persona(args.identifier, args.reason)
            
        elif args.command == 'fork':
            new_uuid = tools.fork_persona(args.source, args.new_name)
            print(f"Fork created: {new_uuid}")
            
        elif args.command == 'history':
            tools.show_persona_history(args.identifier)
            
        elif args.command == 'stats':
            tools.vault_stats()
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
