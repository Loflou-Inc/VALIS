#!/usr/bin/env python3
"""
VALIS Engine Memory Integration Example
Shows how to integrate 5-layer memory system with VALIS engine
"""

import sys
from pathlib import Path

# Add VALIS root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.valis_memory import MemoryRouter

class VALISMemoryIntegration:
    """Example integration of memory system with VALIS engine"""
    
    def __init__(self):
        self.memory_router = MemoryRouter()
    
    def get_persona_response_with_memory(self, persona_id: str, user_message: str, 
                                       client_id: str = None, session_history: list = None):
        """
        Example of how VALIS engine would generate response with memory
        This replaces the basic persona loading with full memory-aware processing
        """
        
        # Get complete memory payload
        memory_payload = self.memory_router.get_memory_payload(
            persona_id=persona_id,
            client_id=client_id,
            session_history=session_history or [],
            current_message=user_message
        )
        
        # Create memory-enhanced prompt (this would go to any provider)
        enhanced_prompt = self._build_memory_enhanced_prompt(memory_payload)
        
        # Simulate provider response (in real implementation, this goes to Claude/OpenAI/etc)
        simulated_response = self._simulate_provider_response(memory_payload, user_message)
        
        # Process response for memory tags
        tag_results = self.memory_router.process_response_tags(
            persona_id, 
            simulated_response, 
            client_id, 
            user_message
        )
        
        # Add to working memory if significant
        if len(user_message) > 20:  # Simple heuristic
            self.memory_router.add_working_memory(
                persona_id,
                f"Discussed: {user_message[:100]}",
                "conversation_topic"
            )
        
        return {
            "response": simulated_response,
            "memory_used": True,
            "memory_layers": len([k for k in memory_payload.keys() if memory_payload[k]]),
            "tags_processed": tag_results
        }
    
    def _build_memory_enhanced_prompt(self, memory_payload: dict) -> str:
        """Build prompt with all memory layers for provider"""
        
        prompt_parts = []
        
        # Core persona
        core = memory_payload['core_biography']
        if core:
            prompt_parts.append(f"You are {core.get('name', 'Assistant')}: {core.get('description', '')}")
            prompt_parts.append(f"Background: {core.get('background', '')}")
            prompt_parts.append(f"Approach: {core.get('approach', '')}")
        
        # Canonized identity
        canon = memory_payload['canonized_identity']
        if canon:
            prompt_parts.append("\nKEY EXPERIENCES (Canon):")
            for entry in canon[-3:]:  # Last 3 canon entries
                prompt_parts.append(f"- {entry['content'][:150]}...")
        
        # Client profile
        client_profile = memory_payload['client_profile']
        if client_profile and client_profile.get('facts'):
            prompt_parts.append("\nCLIENT CONTEXT:")
            for key, value in client_profile['facts'].items():
                prompt_parts.append(f"- {key}: {value}")
        
        # Working memory
        working_memory = memory_payload['working_memory']
        if working_memory:
            prompt_parts.append("\nRECENT OBSERVATIONS:")
            for entry in working_memory[-3:]:  # Last 3 working memories
                prompt_parts.append(f"- {entry['content']}")
        
        # Session history
        session_history = memory_payload['session_history']
        if session_history:
            prompt_parts.append("\nCONVERSATION HISTORY:")
            for msg in session_history[-3:]:  # Last 3 messages
                role = msg['role'].upper()
                content = msg['content'][:100]
                prompt_parts.append(f"{role}: {content}...")
        
        # Current message
        current_message = memory_payload['message']
        if current_message:
            prompt_parts.append(f"\nCURRENT MESSAGE: {current_message}")
        
        prompt_parts.append("\nRespond as this persona with full context awareness.")
        
        return "\n".join(prompt_parts)
    
    def _simulate_provider_response(self, memory_payload: dict, user_message: str) -> str:
        """Simulate what a provider would return (for demo purposes)"""
        
        persona_name = memory_payload['core_biography'].get('name', 'Assistant')
        
        # Check if user is talking about conflicts (Jane's specialty)
        if any(word in user_message.lower() for word in ['conflict', 'disagreement', 'team', 'fight']):
            if 'architecture' in user_message.lower():
                # Demonstrates working memory processing
                return f"""I can see this is about technical team conflicts, which I encounter frequently. Based on my experience, architecture disagreements often stem from unclear decision-making authority rather than technical merit alone.

Let me apply my Systems Thinking Framework here: What's the underlying process issue? Do your engineers have a clear escalation path for architecture decisions? #working_memory

For your specific situation, I recommend establishing an Architecture Review Board with rotating membership. #client_fact:recommended_solution=architecture_review_board

This pattern of technical conflict resolution has become a key part of my methodology after seeing it work at multiple companies. #canon"""
            else:
                return f"""As an HR professional with 15+ years of experience, I understand how challenging team conflicts can be. Let's break this down systematically and look at the underlying dynamics at play."""
        
        return f"""Hello! I'm {persona_name}. I'm here to help with your workplace challenges. Can you tell me more about what's going on?"""


def demo_integration():
    """Demo the VALIS memory integration"""
    
    print("*** VALIS Memory Integration Demo ***")
    print("=" * 45)
    
    # Initialize integration
    integration = VALISMemoryIntegration()
    
    # Simulate conversation with memory
    session_history = [
        {"role": "user", "content": "Hi Jane, I need help with my team"},
        {"role": "assistant", "content": "Of course! I'm here to help with team dynamics. What specific challenges are you facing?"}
    ]
    
    # New user message about technical conflicts
    user_message = "My engineers keep having heated arguments about microservices vs monolith architecture"
    
    print(f"User Message: {user_message}")
    print()
    
    # Get memory-enhanced response
    result = integration.get_persona_response_with_memory(
        persona_id="jane",
        user_message=user_message,
        client_id="user_123",
        session_history=session_history
    )
    
    print("RESPONSE WITH MEMORY:")
    print("-" * 30)
    print(result['response'])
    print()
    
    print("MEMORY INTEGRATION STATS:")
    print(f"- Memory layers used: {result['memory_layers']}")
    print(f"- Tags processed: {sum(result['tags_processed'].values())}")
    print(f"- Canon processed: {result['tags_processed']['canon_processed']}")
    print(f"- Client fact processed: {result['tags_processed']['client_fact_processed']}")
    print(f"- Working memory processed: {result['tags_processed']['working_memory_processed']}")
    
    print()
    print("*** Memory system fully integrated with VALIS! ***")


if __name__ == "__main__":
    demo_integration()
