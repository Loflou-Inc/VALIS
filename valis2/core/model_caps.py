"""
VALIS 2.0 Model Capability Map
Defines token limits and preferred context modes per model
"""

MODEL_CAPS = {
    "local_mistral": {
        "max_tokens": 8192,
        "preferred_mode": "tight",
        "input_token_limit": 6000,
        "description": "Local Mistral 7B - Limited context window"
    },
    "anthropic_claude": {
        "max_tokens": 100000,
        "preferred_mode": "full", 
        "input_token_limit": 95000,
        "description": "Claude - Large context window"
    },
    "openai_gpt4": {
        "max_tokens": 32000,
        "preferred_mode": "balanced",
        "input_token_limit": 28000,
        "description": "GPT-4 - Medium context window"
    },
    "openai_gpt3": {
        "max_tokens": 4096,
        "preferred_mode": "tight",
        "input_token_limit": 3500,
        "description": "GPT-3.5 - Small context window"
    },
    "hardcoded_fallback": {
        "max_tokens": 1000,
        "preferred_mode": "tight",
        "input_token_limit": 800,
        "description": "Fallback - No real model"
    }
}

# Context mode configurations
CONTEXT_MODE_LIMITS = {
    "tight": {
        "persona_bio": 1,
        "canon_memory": 1, 
        "working_memory": 1,
        "client_facts": 0,
        "session_history": 0,
        "description": "Minimal context for resource-constrained models"
    },
    "balanced": {
        "persona_bio": 3,
        "canon_memory": 3,
        "working_memory": 2,
        "client_facts": 3,
        "session_history": 1,
        "description": "Standard context for most use cases"
    },
    "full": {
        "persona_bio": 10,
        "canon_memory": 15,
        "working_memory": 10,
        "client_facts": 10,
        "session_history": 5,
        "description": "Maximum context for large models"
    }
}

def get_model_caps(model_name: str) -> dict:
    """Get model capabilities, fallback to default if unknown"""
    return MODEL_CAPS.get(model_name, MODEL_CAPS["hardcoded_fallback"])

def get_context_limits(mode: str) -> dict:
    """Get context mode limits, fallback to balanced if unknown"""
    return CONTEXT_MODE_LIMITS.get(mode, CONTEXT_MODE_LIMITS["balanced"])

def recommend_context_mode(model_name: str, persona_context_mode: str = None) -> str:
    """Recommend context mode based on model and persona preference"""
    model_caps = get_model_caps(model_name)
    model_preferred = model_caps["preferred_mode"]
    
    # Persona preference takes priority if specified
    if persona_context_mode and persona_context_mode in CONTEXT_MODE_LIMITS:
        return persona_context_mode
    
    return model_preferred
