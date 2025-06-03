#!/usr/bin/env python3
"""
VALIS Memory-Aware Inference Pipeline
The missing piece that actually uses memory in chat flows
"""

import json
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add VALIS root to path
sys.path.append(str(Path(__file__).parent))

try:
    from core.valis_memory import MemoryRouter
    from core.valis_engine import VALISEngine
    from core.persona_router import PersonaRouter
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"VALIS components not available: {e}")
    COMPONENTS_AVAILABLE = False

class VALISInferencePipeline:
    """Memory-aware chat pipeline that actually uses the memory system"""
    
    def __init__(self):
        if not COMPONENTS_AVAILABLE:
            raise RuntimeError("VALIS components not available")
            
        self.memory_router = MemoryRouter()
        self.valis_engine = VALISEngine()
        self.persona_router = PersonaRouter()
        
    def run_memory_aware_chat(self, persona_id: str, client_id: str, user_message: str, 
                             session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a complete memory-aware chat cycle
        Returns response with debug info about memory usage
        """
        
        print(f"MEMORY-AWARE CHAT PIPELINE")
        print(f"Persona: {persona_id}")
        print(f"Client: {client_id}")
        print(f"Message: {user_message}")
        print()
        
        # STEP 1: Load persona definition
        persona_file = Path(__file__).parent / "personas" / f"{persona_id}.json"
        if not persona_file.exists():
            raise ValueError(f"Persona {persona_id} not found at {persona_file}")
            
        with open(persona_file, 'r', encoding='utf-8') as f:
            persona_data = json.load(f)
        
        print(f"SUCCESS: Loaded persona: {persona_data.get('name', persona_id)}")
        
        # STEP 2: Get complete memory payload
        session_history = self._get_session_history(session_id) if session_id else []
        
        memory_payload = self.memory_router.get_memory_payload(
            persona_id=persona_id,
            client_id=client_id,
            session_history=session_history,
            current_message=user_message
        )
        
        print(f"MEMORY PAYLOAD:")
        self._print_memory_debug(memory_payload)
        
        # STEP 3: Format enriched prompt
        enriched_prompt = self._format_prompt_from_memory(memory_payload, persona_data)
        
        print(f"ENRICHED PROMPT:")
        print(f"Length: {len(enriched_prompt)} characters")
        print("Preview:")
        print(enriched_prompt[:200] + "..." if len(enriched_prompt) > 200 else enriched_prompt)
        print()
        
        # STEP 4: Get LLM response using VALIS engine
        start_time = datetime.now()
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            response_data = loop.run_until_complete(
                self.valis_engine.get_persona_response(
                    persona_id=persona_id,
                    message=enriched_prompt,
                    session_id=session_id or f"dev_{client_id}",
                    context={
                        "client_id": client_id,
                        "memory_enhanced": True,
                        "session_history": session_history
                    }
                )
            )
            
        finally:
            loop.close()
            
        processing_time = (datetime.now() - start_time).total_seconds()
        
        response_text = response_data.get("response", "No response generated")
        provider_used = response_data.get("provider", "Unknown")
        
        print(f"LLM RESPONSE:")
        print(f"Provider: {provider_used}")
        print(f"Processing time: {processing_time:.2f}s")
        print(f"Response: {response_text}")
        print()
        
        # STEP 5: Process memory tags from user message (BEFORE sending to LLM)
        tags_processed = self._process_memory_tags(
            user_message=user_message,
            persona_id=persona_id,
            client_id=client_id
        )
        
        if tags_processed:
            print(f"TAGS PROCESSED: {tags_processed}")
        else:
            print("No memory tags found in response")
        
        return {
            "success": True,
            "response": response_text,
            "provider": provider_used,
            "processing_time": processing_time,
            "memory_used": memory_payload,
            "tags_processed": tags_processed,
            "persona_id": persona_id,
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_session_history(self, session_id: str) -> list:
        """Get session history (simplified for now)"""
        # TODO: Implement proper session storage
        return []
    
    def _format_prompt_from_memory(self, memory_payload: Dict[str, Any], persona_data: Dict[str, Any]) -> str:
        """Format enriched prompt with memory context"""
        
        # Basic persona intro
        name = persona_data.get("name", memory_payload["persona_id"])
        description = persona_data.get("description", "AI Assistant")
        tone = persona_data.get("tone", "helpful")
        
        intro = f"You are {name}, {description}. Your tone is {tone}."
        
        # Memory layers
        canon_section = ""
        if memory_payload.get("canonized_identity"):
            canon_facts = memory_payload["canonized_identity"]
            if canon_facts:
                canon_section = "\\n\\nCanonized experiences:\\n" + "\\n".join([
                    f"- {fact}" for fact in canon_facts[:5]  # Limit to 5 most recent
                ])
        
        client_section = ""
        if memory_payload.get("client_profile", {}).get("facts"):
            client_facts = memory_payload["client_profile"]["facts"]
            if client_facts:
                client_section = "\\n\\nWhat you know about this client:\\n" + "\\n".join([
                    f"- {key}: {value}" for key, value in client_facts.items()
                ])
        
        working_section = ""
        if memory_payload.get("working_memory"):
            working_memories = memory_payload["working_memory"]
            if working_memories:
                working_section = "\\n\\nRecent observations:\\n" + "\\n".join([
                    f"- {memory}" for memory in working_memories[-3:]  # Last 3
                ])
        
        history_section = ""
        if memory_payload.get("session_history"):
            history = memory_payload["session_history"]
            if history:
                history_section = "\\n\\nRecent conversation:\\n" + "\\n".join([
                    f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" 
                    for msg in history[-4:]  # Last 4 exchanges
                ])
        
        # Current message
        current_message = memory_payload.get("message", "")
        
        # Assemble full prompt
        full_prompt = (
            f"{intro}"
            f"{canon_section}"
            f"{client_section}" 
            f"{working_section}"
            f"{history_section}"
            f"\\n\\nUser: {current_message}"
            f"\\nAssistant:"
        )
        
        return full_prompt
    
    def _process_memory_tags(self, user_message: str, persona_id: str, client_id: str) -> list:
        """Process memory tags in user input BEFORE sending to LLM"""
        tags_found = []
        
        # Look for #canon tags
        if "#canon" in user_message.lower():
            # Extract content for canonization
            canon_content = user_message.replace("#canon", "").strip()
            
            # Add to canon memory
            canon_file = Path(__file__).parent / "memory" / "personas" / persona_id / "canon.json"
            canon_file.parent.mkdir(parents=True, exist_ok=True)
            
            if canon_file.exists():
                with open(canon_file, 'r', encoding='utf-8') as f:
                    canon_data = json.load(f)
            else:
                canon_data = []
            
            canon_entry = {
                "timestamp": datetime.now().isoformat(),
                "content": canon_content,
                "source": "user_input"
            }
            
            canon_data.append(canon_entry)
            
            with open(canon_file, 'w', encoding='utf-8') as f:
                json.dump(canon_data, f, indent=2, ensure_ascii=False)
            
            tags_found.append("canon")
            print(f"SAVED CANON: {canon_content}")
        
        # Look for #client_fact tags
        if "#client_fact" in user_message.lower():
            # Extract client fact
            fact_content = user_message.replace("#client_fact", "").strip()
            
            # Add to client profile
            client_file = Path(__file__).parent / "memory" / "clients" / client_id / f"{persona_id}_profile.json"
            client_file.parent.mkdir(parents=True, exist_ok=True)
            
            if client_file.exists():
                with open(client_file, 'r', encoding='utf-8') as f:
                    client_data = json.load(f)
            else:
                client_data = {"facts": {}, "preferences": {}}
            
            client_data["facts"][f"fact_{len(client_data['facts']) + 1}"] = fact_content
            
            with open(client_file, 'w', encoding='utf-8') as f:
                json.dump(client_data, f, indent=2, ensure_ascii=False)
            
            tags_found.append("client_fact")
            print(f"SAVED CLIENT FACT: {fact_content}")
        
        # Look for #working_memory tags  
        if "#working_memory" in user_message.lower():
            # Extract working memory
            working_content = user_message.replace("#working_memory", "").strip()
            
            # Add to working memory
            working_file = Path(__file__).parent / "memory" / "personas" / persona_id / "working.json"
            working_file.parent.mkdir(parents=True, exist_ok=True)
            
            if working_file.exists():
                with open(working_file, 'r', encoding='utf-8') as f:
                    working_data = json.load(f)
            else:
                working_data = []
            
            working_data.append(working_content)
            
            # Keep only last 10 working memories
            if len(working_data) > 10:
                working_data = working_data[-10:]
            
            with open(working_file, 'w', encoding='utf-8') as f:
                json.dump(working_data, f, indent=2, ensure_ascii=False)
            
            tags_found.append("working_memory")
            print(f"SAVED WORKING MEMORY: {working_content}")
        
        return tags_found
    
    def _print_memory_debug(self, memory_payload: Dict[str, Any]):
        """Print memory debug information"""
        print(f"  Core Biography: {len(memory_payload.get('core_biography', []))} entries")
        print(f"  Canonized Identity: {len(memory_payload.get('canonized_identity', []))} entries")
        
        client_facts = memory_payload.get('client_profile', {}).get('facts', {})
        print(f"  Client Profile: {len(client_facts)} facts")
        
        print(f"  Working Memory: {len(memory_payload.get('working_memory', []))} entries")
        print(f"  Session History: {len(memory_payload.get('session_history', []))} messages")
        print()

# CLI for testing
def main():
    """CLI interface for testing memory-aware chat"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VALIS Memory-Aware Chat Test")
    parser.add_argument("--persona", default="marty", help="Persona ID")
    parser.add_argument("--client", default="dev_test", help="Client ID")
    parser.add_argument("--message", required=True, help="User message")
    parser.add_argument("--session", help="Session ID")
    
    args = parser.parse_args()
    
    try:
        pipeline = VALISInferencePipeline()
        result = pipeline.run_memory_aware_chat(
            persona_id=args.persona,
            client_id=args.client,
            user_message=args.message,
            session_id=args.session
        )
        
        print("=" * 60)
        print("SUCCESS: PIPELINE COMPLETE")
        print(f"Success: {result['success']}")
        print(f"Provider: {result['provider']}")
        print(f"Processing time: {result['processing_time']:.2f}s")
        print(f"Tags processed: {result['tags_processed']}")
        
    except Exception as e:
        print(f"FAILED: PIPELINE FAILED: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
