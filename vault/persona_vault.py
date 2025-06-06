"""
VALIS Persona Vault System
Persistent storage and lifecycle management for persona blueprints
"""

import json
import os
import uuid
import shutil
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import sqlite3
import hashlib

class PersonaVault:
    """
    Central repository for persona blueprints with versioning and lifecycle management
    """
    
    def __init__(self, vault_path: str = "C:\\VALIS\\vault\\personas"):
        self.vault_path = vault_path
        self.history_path = os.path.join(vault_path, "history")
        self.db_path = os.path.join(vault_path, "vault.db")
        
        # Ensure directories exist
        os.makedirs(vault_path, exist_ok=True)
        os.makedirs(self.history_path, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize the persona vault database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS personas (
                    uuid TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT DEFAULT 'interface',
                    status TEXT DEFAULT 'draft',
                    archetypes TEXT,
                    domains TEXT,
                    source_material TEXT,
                    fusion_confidence REAL,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    activated_at TIMESTAMP,
                    blueprint_hash TEXT,
                    is_forkable BOOLEAN DEFAULT 1,
                    fork_source TEXT,
                    version_count INTEGER DEFAULT 1
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS persona_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    persona_uuid TEXT,
                    version_number INTEGER,
                    timestamp TIMESTAMP,
                    change_type TEXT,
                    change_description TEXT,
                    blueprint_hash TEXT,
                    file_path TEXT,
                    FOREIGN KEY (persona_uuid) REFERENCES personas (uuid)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS persona_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    persona_uuid TEXT,
                    session_id TEXT,
                    user_id TEXT,
                    started_at TIMESTAMP,
                    ended_at TIMESTAMP,
                    interaction_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (persona_uuid) REFERENCES personas (uuid)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_personas_name ON personas (name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_personas_status ON personas (status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_personas_type ON personas (type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_history_persona ON persona_history (persona_uuid)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_persona ON persona_sessions (persona_uuid)")
            
            conn.commit()
    
    def store_persona(self, blueprint: Dict[str, Any], status: str = "draft") -> str:
        """
        Store a persona blueprint in the vault
        Returns the persona UUID
        """
        # Extract metadata
        persona_uuid = blueprint.get("id", str(uuid.uuid4()))
        name = blueprint.get("name", f"unnamed_{persona_uuid[:8]}")
        persona_type = blueprint.get("type", "interface")
        archetypes = json.dumps(blueprint.get("archetypes", []))
        domains = json.dumps(blueprint.get("domain", []))
        source_material = json.dumps(blueprint.get("source_material", []))
        fusion_confidence = blueprint.get("fusion_metadata", {}).get("fusion_confidence", 0.0)
        
        # Calculate blueprint hash
        blueprint_json = json.dumps(blueprint, sort_keys=True)
        blueprint_hash = hashlib.sha256(blueprint_json.encode()).hexdigest()
        
        # Save blueprint file
        blueprint_filename = f"{name.lower().replace(' ', '_')}.json"
        blueprint_path = os.path.join(self.vault_path, blueprint_filename)
        
        with open(blueprint_path, 'w', encoding='utf-8') as f:
            json.dump(blueprint, f, indent=2, default=str)
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now(timezone.utc)
            
            # Check if persona already exists
            existing = conn.execute(
                "SELECT uuid, version_count FROM personas WHERE uuid = ?", 
                (persona_uuid,)
            ).fetchone()
            
            if existing:
                # Update existing persona
                version_count = existing[1] + 1
                
                conn.execute("""
                    UPDATE personas SET
                        name = ?, type = ?, status = ?, archetypes = ?,
                        domains = ?, source_material = ?, fusion_confidence = ?,
                        updated_at = ?, blueprint_hash = ?, version_count = ?
                    WHERE uuid = ?
                """, (
                    name, persona_type, status, archetypes, domains,
                    source_material, fusion_confidence, now, blueprint_hash,
                    version_count, persona_uuid
                ))
                
                # Save version history
                history_filename = f"{name.lower().replace(' ', '_')}_{now.strftime('%Y-%m-%d_%H%M%S')}.json"
                history_path = os.path.join(self.history_path, history_filename)
                shutil.copy2(blueprint_path, history_path)
                
                # Log history
                conn.execute("""
                    INSERT INTO persona_history 
                    (persona_uuid, version_number, timestamp, change_type, 
                     change_description, blueprint_hash, file_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    persona_uuid, version_count, now, "update",
                    f"Blueprint updated to version {version_count}",
                    blueprint_hash, history_path
                ))
                
            else:
                # Insert new persona
                conn.execute("""
                    INSERT INTO personas 
                    (uuid, name, type, status, archetypes, domains, source_material,
                     fusion_confidence, created_at, updated_at, blueprint_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    persona_uuid, name, persona_type, status, archetypes, domains,
                    source_material, fusion_confidence, now, now, blueprint_hash
                ))
                
                # Log initial creation
                conn.execute("""
                    INSERT INTO persona_history 
                    (persona_uuid, version_number, timestamp, change_type, 
                     change_description, blueprint_hash, file_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    persona_uuid, 1, now, "create",
                    f"Persona '{name}' created",
                    blueprint_hash, blueprint_path
                ))
            
            conn.commit()
        
        return persona_uuid
    
    def get_persona(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a persona blueprint by UUID or name
        """
        with sqlite3.connect(self.db_path) as conn:
            # Try UUID first, then name
            result = conn.execute(
                "SELECT name FROM personas WHERE uuid = ? OR name = ?",
                (identifier, identifier)
            ).fetchone()
            
            if not result:
                return None
            
            name = result[0]
            blueprint_filename = f"{name.lower().replace(' ', '_')}.json"
            blueprint_path = os.path.join(self.vault_path, blueprint_filename)
            
            if os.path.exists(blueprint_path):
                with open(blueprint_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        return None
    
    def list_personas(self, status: Optional[str] = None, 
                     persona_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all personas with optional filtering
        """
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM personas"
            params = []
            
            conditions = []
            if status:
                conditions.append("status = ?")
                params.append(status)
            if persona_type:
                conditions.append("type = ?")
                params.append(persona_type)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY updated_at DESC"
            
            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description]
            
            personas = []
            for row in cursor.fetchall():
                persona_data = dict(zip(columns, row))
                
                # Parse JSON fields
                if persona_data['archetypes']:
                    persona_data['archetypes'] = json.loads(persona_data['archetypes'])
                if persona_data['domains']:
                    persona_data['domains'] = json.loads(persona_data['domains'])
                if persona_data['source_material']:
                    persona_data['source_material'] = json.loads(persona_data['source_material'])
                
                personas.append(persona_data)
            
            return personas
    
    def update_status(self, identifier: str, new_status: str, 
                     change_description: str = None) -> bool:
        """
        Update persona status (draft, active, archived, locked)
        """
        valid_statuses = ["draft", "active", "archived", "locked"]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now(timezone.utc)
            
            # Update status
            result = conn.execute("""
                UPDATE personas SET status = ?, updated_at = ?,
                       activated_at = CASE WHEN ? = 'active' THEN ? ELSE activated_at END
                WHERE uuid = ? OR name = ?
            """, (new_status, now, new_status, now, identifier, identifier))
            
            if result.rowcount == 0:
                return False
            
            # Get persona UUID for history
            persona_uuid = conn.execute(
                "SELECT uuid FROM personas WHERE uuid = ? OR name = ?",
                (identifier, identifier)
            ).fetchone()[0]
            
            # Log status change
            description = change_description or f"Status changed to {new_status}"
            conn.execute("""
                INSERT INTO persona_history 
                (persona_uuid, version_number, timestamp, change_type, change_description)
                VALUES (?, (SELECT version_count FROM personas WHERE uuid = ?), ?, ?, ?)
            """, (persona_uuid, persona_uuid, now, "status_change", description))
            
            conn.commit()
            return True
    
    def fork_persona(self, source_identifier: str, new_name: str, 
                    changes: Dict[str, Any] = None) -> str:
        """
        Create a new persona based on an existing one
        """
        # Get source persona
        source_blueprint = self.get_persona(source_identifier)
        if not source_blueprint:
            raise ValueError(f"Source persona '{source_identifier}' not found")
        
        # Check if source is forkable
        with sqlite3.connect(self.db_path) as conn:
            is_forkable = conn.execute(
                "SELECT is_forkable FROM personas WHERE uuid = ? OR name = ?",
                (source_identifier, source_identifier)
            ).fetchone()[0]
            
            if not is_forkable:
                raise ValueError(f"Persona '{source_identifier}' is not forkable")
        
        # Create new blueprint
        new_blueprint = source_blueprint.copy()
        new_blueprint["id"] = str(uuid.uuid4())
        new_blueprint["name"] = new_name
        new_blueprint["created_at"] = datetime.now(timezone.utc).isoformat()
        
        # Apply changes if provided
        if changes:
            for key, value in changes.items():
                new_blueprint[key] = value
        
        # Mark as fork
        new_blueprint["fusion_metadata"]["fork_source"] = source_blueprint["id"]
        new_blueprint["fusion_metadata"]["fork_created_at"] = datetime.now(timezone.utc).isoformat()
        
        # Store the forked persona
        return self.store_persona(new_blueprint, status="draft")
    
    def get_persona_history(self, identifier: str) -> List[Dict[str, Any]]:
        """
        Get the version history of a persona
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get persona UUID
            result = conn.execute(
                "SELECT uuid FROM personas WHERE uuid = ? OR name = ?",
                (identifier, identifier)
            ).fetchone()
            
            if not result:
                return []
            
            persona_uuid = result[0]
            
            # Get history
            cursor = conn.execute("""
                SELECT version_number, timestamp, change_type, change_description, 
                       blueprint_hash, file_path
                FROM persona_history 
                WHERE persona_uuid = ?
                ORDER BY version_number DESC
            """, (persona_uuid,))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def start_session(self, persona_identifier: str, user_id: str = "system") -> str:
        """
        Start a new session with a persona
        """
        with sqlite3.connect(self.db_path) as conn:
            # Verify persona exists and is active
            result = conn.execute(
                "SELECT uuid, status FROM personas WHERE uuid = ? OR name = ?",
                (persona_identifier, persona_identifier)
            ).fetchone()
            
            if not result:
                raise ValueError(f"Persona '{persona_identifier}' not found")
            
            persona_uuid, status = result
            if status not in ["active", "draft"]:
                raise ValueError(f"Persona is {status} and cannot start sessions")
            
            # Create new session
            session_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            conn.execute("""
                INSERT INTO persona_sessions 
                (persona_uuid, session_id, user_id, started_at)
                VALUES (?, ?, ?, ?)
            """, (persona_uuid, session_id, user_id, now))
            
            conn.commit()
            return session_id
    
    def end_session(self, session_id: str, interaction_count: int = 0) -> bool:
        """
        End a persona session
        """
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now(timezone.utc)
            
            result = conn.execute("""
                UPDATE persona_sessions 
                SET ended_at = ?, interaction_count = ?, status = 'ended'
                WHERE session_id = ?
            """, (now, interaction_count, session_id))
            
            conn.commit()
            return result.rowcount > 0
    
    def get_vault_stats(self) -> Dict[str, Any]:
        """
        Get vault statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Persona counts by status
            cursor = conn.execute("""
                SELECT status, COUNT(*) 
                FROM personas 
                GROUP BY status
            """)
            stats["personas_by_status"] = dict(cursor.fetchall())
            
            # Total personas
            stats["total_personas"] = conn.execute("SELECT COUNT(*) FROM personas").fetchone()[0]
            
            # Active sessions
            stats["active_sessions"] = conn.execute(
                "SELECT COUNT(*) FROM persona_sessions WHERE status = 'active'"
            ).fetchone()[0]
            
            # Most recent personas
            cursor = conn.execute("""
                SELECT name, created_at 
                FROM personas 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            stats["recent_personas"] = [{"name": row[0], "created_at": row[1]} for row in cursor.fetchall()]
            
            return stats


# Utility functions for the vault system
def migrate_mr_fission_personas():
    """
    Migrate existing Mr. Fission personas to the vault system
    """
    vault = PersonaVault()
    fission_persona_dir = "C:\\VALIS\\vault\\personas"
    
    migrated_count = 0
    
    for filename in os.listdir(fission_persona_dir):
        if filename.endswith('.json') and filename != 'vault.db':
            filepath = os.path.join(fission_persona_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    blueprint = json.load(f)
                
                # Store in vault (will handle duplicates)
                persona_uuid = vault.store_persona(blueprint, status="draft")
                print(f"Migrated {filename} -> {persona_uuid}")
                migrated_count += 1
                
            except Exception as e:
                print(f"Failed to migrate {filename}: {e}")
    
    print(f"Migration complete: {migrated_count} personas migrated")
    return migrated_count


# Example usage and testing
if __name__ == "__main__":
    print("=== VALIS PERSONA VAULT SYSTEM ===")
    
    # Initialize vault
    vault = PersonaVault()
    
    # Test with Jane persona if it exists
    jane_path = "C:\\VALIS\\vault\\personas\\test_jane.json"
    if os.path.exists(jane_path):
        with open(jane_path, 'r', encoding='utf-8') as f:
            jane_blueprint = json.load(f)
        
        # Store Jane in vault
        jane_uuid = vault.store_persona(jane_blueprint, status="draft")
        print(f"Jane stored with UUID: {jane_uuid}")
        
        # Test retrieval
        retrieved = vault.get_persona("Jane")
        if retrieved:
            print(f"Retrieved persona: {retrieved['name']}")
        
        # Test status update
        vault.update_status("Jane", "active", "Ready for testing")
        print("Jane activated for testing")
        
        # Start a test session
        session_id = vault.start_session("Jane", "test_user")
        print(f"Test session started: {session_id}")
        
        # End session
        vault.end_session(session_id, interaction_count=5)
        print("Test session ended")
    
    # Show vault stats
    stats = vault.get_vault_stats()
    print(f"\nVault Statistics:")
    print(f"Total personas: {stats['total_personas']}")
    print(f"Active sessions: {stats['active_sessions']}")
    print(f"Personas by status: {stats['personas_by_status']}")
    
    print("\n=== PERSONA VAULT ONLINE ===")
