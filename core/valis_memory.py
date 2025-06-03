#!/usr/bin/env python3
"""
VALIS Memory Architecture - Sprint 6
5-Layer Memory System for Universal AI Persona Platform

Memory Layers:
1. Core Persona - Static authored backstory (permanent)
2. Canonized Identity - LLM-created events marked as canon (permanent) 
3. Client Profile - Per-user facts/preferences (persistent)
4. Working Memory - Short-term musings, observations (FIFO rotating)
5. Session History - Current conversation turns (ephemeral)
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class MemoryRouter:
    """Central memory management system for VALIS personas"""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent  # VALIS root
        
        self.base_path = Path(base_path)
        self.personas_path = self.base_path / "personas"
        self.memory_path = self.base_path / "memory"
        self.clients_path = self.memory_path / "clients"
        self.persona_memory_path = self.memory_path / "personas"
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Configuration
        self.working_memory_max_entries = 50  # Configurable FIFO limit
    
    def _ensure_directories(self):
        """Ensure all memory directories exist"""
        for path in [self.memory_path, self.clients_path, self.persona_memory_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def get_memory_payload(self, persona_id: str, client_id: str = None, 
                          session_history: List[Dict] = None, 
                          current_message: str = "") -> Dict[str, Any]:
        """
        Get complete memory payload for prompt injection
        
        Returns structured dictionary with all 5 memory layers:
        {
            "persona_id": "jane",
            "core_biography": [...],
            "canonized_identity": [...], 
            "client_profile": {...},
            "working_memory": [...],
            "session_history": [...],
            "message": "Current user message"
        }
        """
        try:
            # Layer 1: Core Persona (static backstory)
            core_biography = self._load_core_persona(persona_id)
            
            # Layer 2: Canonized Identity (permanent events)
            canonized_identity = self._load_canonized_identity(persona_id)
            
            # Layer 3: Client Profile (per-user facts)
            client_profile = self._load_client_profile(persona_id, client_id) if client_id else {}
            
            # Layer 4: Working Memory (FIFO observations)
            working_memory = self._load_working_memory(persona_id)
            
            # Layer 5: Session History (current conversation)
            session_history = session_history or []
            
            payload = {
                "persona_id": persona_id,
                "core_biography": core_biography,
                "canonized_identity": canonized_identity,
                "client_profile": client_profile,
                "working_memory": working_memory,
                "session_history": session_history,
                "message": current_message
            }
            
            logger.debug(f"Memory payload generated for {persona_id}, client: {client_id}")
            return payload
            
        except Exception as e:
            logger.error(f"Error generating memory payload: {e}")
            # Return minimal payload on error
            return {
                "persona_id": persona_id,
                "core_biography": {},
                "canonized_identity": [],
                "client_profile": {},
                "working_memory": [],
                "session_history": session_history or [],
                "message": current_message
            }
    
    def _load_core_persona(self, persona_id: str) -> Dict[str, Any]:
        """Load Layer 1: Core Persona from personas/{id}.json"""
        core_path = self.personas_path / f"{persona_id}.json"
        
        if not core_path.exists():
            logger.warning(f"Core persona file not found: {core_path}")
            return {}
        
        try:
            with open(core_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading core persona {persona_id}: {e}")
            return {}
    
    def _load_canonized_identity(self, persona_id: str) -> List[Dict[str, Any]]:
        """Load Layer 2: Canonized Identity from personas/{id}/canon.json"""
        canon_dir = self.personas_path / persona_id
        canon_path = canon_dir / "canon.json"
        
        if not canon_path.exists():
            return []
        
        try:
            with open(canon_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading canonized identity for {persona_id}: {e}")
            return []
    
    def _load_client_profile(self, persona_id: str, client_id: str) -> Dict[str, Any]:
        """Load Layer 3: Client Profile from memory/clients/{client_id}/{persona_id}_profile.json"""
        if not client_id:
            return {}
        
        client_dir = self.clients_path / client_id
        profile_path = client_dir / f"{persona_id}_profile.json"
        
        if not profile_path.exists():
            return {}
        
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading client profile for {persona_id}, client {client_id}: {e}")
            return {}
    
    def _load_working_memory(self, persona_id: str) -> List[Dict[str, Any]]:
        """Load Layer 4: Working Memory from memory/personas/{id}/working.json"""
        working_path = self.persona_memory_path / persona_id / "working.json"
        
        if not working_path.exists():
            return []
        
        try:
            with open(working_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading working memory for {persona_id}: {e}")
            return []
    
    # Canonization Methods (Layer 2)
    def canonize_response(self, persona_id: str, response_text: str, 
                         source_prompt: str = "", metadata: Dict = None) -> bool:
        """
        Add response to canonized identity (permanent storage)
        Used when response contains #canon tag
        """
        try:
            canon_dir = self.personas_path / persona_id
            canon_dir.mkdir(exist_ok=True)
            canon_path = canon_dir / "canon.json"
            
            # Load existing canon entries
            canon_entries = []
            if canon_path.exists():
                with open(canon_path, 'r', encoding='utf-8') as f:
                    canon_entries = json.load(f)
            
            # Create new canon entry
            canon_entry = {
                "timestamp": datetime.now().isoformat(),
                "content": response_text,
                "source_prompt": source_prompt,
                "metadata": metadata or {},
                "canon_id": len(canon_entries) + 1
            }
            
            # Append and save (immutable by design)
            canon_entries.append(canon_entry)
            
            with open(canon_path, 'w', encoding='utf-8') as f:
                json.dump(canon_entries, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Canonized response for {persona_id}: canon_id {canon_entry['canon_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error canonizing response for {persona_id}: {e}")
            return False
    
    # Client Profile Methods (Layer 3)
    def add_client_fact(self, persona_id: str, client_id: str, 
                       key: str, value: Any, metadata: Dict = None) -> bool:
        """
        Add or update client-specific fact
        Used when response contains #client_fact tag
        """
        try:
            client_dir = self.clients_path / client_id
            client_dir.mkdir(parents=True, exist_ok=True)
            profile_path = client_dir / f"{persona_id}_profile.json"
            
            # Load existing profile
            profile = {}
            if profile_path.exists():
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
            
            # Ensure structure
            if "facts" not in profile:
                profile["facts"] = {}
            if "metadata" not in profile:
                profile["metadata"] = {}
            
            # Add/update fact
            profile["facts"][key] = value
            profile["metadata"][key] = {
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            profile["last_updated"] = datetime.now().isoformat()
            
            # Save profile
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Added client fact for {persona_id}, client {client_id}: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding client fact: {e}")
            return False
    
    # Working Memory Methods (Layer 4)
    def add_working_memory(self, persona_id: str, content: str, 
                          memory_type: str = "observation", metadata: Dict = None) -> bool:
        """
        Add entry to working memory (FIFO queue with max limit)
        """
        try:
            working_dir = self.persona_memory_path / persona_id
            working_dir.mkdir(parents=True, exist_ok=True)
            working_path = working_dir / "working.json"
            
            # Load existing working memory
            working_memory = []
            if working_path.exists():
                with open(working_path, 'r', encoding='utf-8') as f:
                    working_memory = json.load(f)
            
            # Create new memory entry
            memory_entry = {
                "timestamp": datetime.now().isoformat(),
                "content": content,
                "type": memory_type,
                "metadata": metadata or {}
            }
            
            # Add new entry and enforce FIFO limit
            working_memory.append(memory_entry)
            if len(working_memory) > self.working_memory_max_entries:
                working_memory = working_memory[-self.working_memory_max_entries:]
            
            # Save working memory
            with open(working_path, 'w', encoding='utf-8') as f:
                json.dump(working_memory, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Added working memory for {persona_id}: {memory_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding working memory for {persona_id}: {e}")
            return False
    
    def get_recent_memory(self, persona_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent working memory entries"""
        working_memory = self._load_working_memory(persona_id)
        return working_memory[-limit:] if working_memory else []
    
    # Response Processing and Tagging Logic
    def process_response_tags(self, persona_id: str, response_text: str, 
                            client_id: str = None, source_prompt: str = "") -> Dict[str, bool]:
        """
        Process response for memory tags and route to appropriate storage
        
        Supported tags:
        - #canon - Add to canonized identity
        - #client_fact:key=value - Add to client profile
        - #working_memory - Add to working memory
        
        Returns dict indicating which tags were processed
        """
        results = {
            "canon_processed": False,
            "client_fact_processed": False,
            "working_memory_processed": False
        }
        
        try:
            # Process #canon tag
            if "#canon" in response_text:
                success = self.canonize_response(persona_id, response_text, source_prompt)
                results["canon_processed"] = success
                
                # Also add to working memory for immediate context
                if success:
                    self.add_working_memory(persona_id, f"Canonized: {response_text[:100]}...", "canon")
            
            # Process #client_fact tags
            import re
            client_fact_pattern = r'#client_fact:(\w+)=([^#\n]+)'
            fact_matches = re.findall(client_fact_pattern, response_text)
            
            for key, value in fact_matches:
                if client_id:
                    success = self.add_client_fact(persona_id, client_id, key.strip(), value.strip())
                    results["client_fact_processed"] = success
            
            # Process #working_memory tag
            if "#working_memory" in response_text:
                # Extract content after tag for working memory
                clean_content = response_text.replace("#working_memory", "").strip()
                success = self.add_working_memory(persona_id, clean_content, "tagged_memory")
                results["working_memory_processed"] = success
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing response tags: {e}")
            return results
    
    # Session History Utilities (Layer 5)
    @staticmethod
    def normalize_session_history(messages: List[Dict]) -> List[Dict[str, str]]:
        """
        Normalize session history to standard format:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        """
        normalized = []
        for msg in messages:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                normalized.append({
                    "role": msg["role"],
                    "content": str(msg["content"])
                })
        return normalized
    
    @staticmethod
    def format_session_history_as_string(session_history: List[Dict]) -> str:
        """Format session history as single string for prompt injection"""
        if not session_history:
            return "No previous conversation."
        
        formatted_lines = []
        for msg in session_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted_lines.append(f"{role.upper()}: {content}")
        
        return "\n".join(formatted_lines)
    
    # Configuration Methods
    def set_working_memory_limit(self, limit: int):
        """Configure working memory FIFO limit"""
        self.working_memory_max_entries = max(1, limit)
        logger.info(f"Working memory limit set to {self.working_memory_max_entries}")
    
    def get_memory_stats(self, persona_id: str) -> Dict[str, Any]:
        """Get memory statistics for a persona"""
        try:
            stats = {
                "persona_id": persona_id,
                "core_persona_exists": (self.personas_path / f"{persona_id}.json").exists(),
                "canonized_entries": len(self._load_canonized_identity(persona_id)),
                "working_memory_entries": len(self._load_working_memory(persona_id)),
                "client_profiles": 0
            }
            
            # Count client profiles
            for client_dir in self.clients_path.iterdir():
                if client_dir.is_dir():
                    profile_path = client_dir / f"{persona_id}_profile.json"
                    if profile_path.exists():
                        stats["client_profiles"] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting memory stats for {persona_id}: {e}")
            return {"error": str(e)}


# Utility Functions for VALIS Engine Integration
def create_memory_router(base_path: str = None) -> MemoryRouter:
    """Factory function to create MemoryRouter instance"""
    return MemoryRouter(base_path)


def test_memory_system():
    """Basic test function for memory system"""
    router = create_memory_router()
    
    # Test payload generation
    payload = router.get_memory_payload("jane", "test_user", 
                                       [{"role": "user", "content": "Hello"}],
                                       "Test message")
    
    print("Memory payload generated successfully:")
    print(f"Persona: {payload['persona_id']}")
    print(f"Core biography keys: {list(payload['core_biography'].keys())}")
    print(f"Memory layers: {len(payload)} total")
    
    return payload


if __name__ == "__main__":
    # Run basic test
    test_memory_system()
