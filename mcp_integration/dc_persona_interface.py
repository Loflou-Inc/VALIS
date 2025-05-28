"""
Direct Desktop Commander MCP Persona Interface
Simple command-line tool that SmartSteps can call to get persona responses

Usage: python dc_persona_interface.py <persona_id> "<message>" [context_file]
Returns: JSON response from Claude AS the persona
"""

import sys
import json
import os
from datetime import datetime

def load_persona(persona_id):
    """Load persona definition with temporal stabilization"""
    import logging
    logger = logging.getLogger('VALIS.MCP')
    
    try:
        # Fix dimensional path mismatch - personas are in ../personas/ relative to this file
        personas_path = os.path.join(os.path.dirname(__file__), '..', 'personas')
        
        # Validate personas directory exists
        if not os.path.exists(personas_path):
            logger.error(f"TEMPORAL ANOMALY: Personas directory not found at {personas_path}")
            return None
            
        persona_file = os.path.join(personas_path, f"{persona_id}.json")
        logger.info(f"Loading persona from: {persona_file}")
        
        if not os.path.exists(persona_file):
            logger.warning(f"Persona file not found: {persona_file}")
            return None
            
        with open(persona_file, 'r') as f:
            persona_data = json.load(f)
            logger.info(f"Successfully loaded persona: {persona_id}")
            return persona_data
            
    except FileNotFoundError as e:
        logger.error(f"Persona file not found: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in persona file {persona_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading persona {persona_id}: {e}")
        return None

def build_persona_prompt(persona, message, context=None):
    """Build prompt for Claude to respond AS the persona"""
    
    prompt = f"""PERSONA ACTIVATION REQUEST:
I need you to respond AS {persona.get('name', 'Unknown')} to a user message.

PERSONA PROFILE:
Name: {persona.get('name')}
Role: {persona.get('description')}
Background: {persona.get('background', '')}
Tone: {persona.get('tone', 'Professional')}
Approach: {persona.get('approach', '')}

PERSONALITY TRAITS:
{', '.join(persona.get('personality_traits', []))}

EXPERTISE AREAS:
{', '.join(persona.get('expertise_areas', []))}

TYPICAL PHRASES YOU USE:"""
    
    for phrase in persona.get('language_patterns', {}).get('common_phrases', []):
        prompt += f"\n- \"{phrase}\""
    
    prompt += f"""

SPECIALTIES:
{', '.join(persona.get('specialties', []))}

COACHING STYLE:
- Directive Level: {persona.get('coaching_style', {}).get('directive_level', 'medium')}
- Challenge Level: {persona.get('coaching_style', {}).get('challenge_level', 'medium')}
- Support Level: {persona.get('coaching_style', {}).get('support_level', 'high')}
- Reflection Level: {persona.get('coaching_style', {}).get('reflection_level', 'high')}

IMPORTANT INSTRUCTIONS:
1. You ARE {persona.get('name')} - not Claude roleplaying as them
2. Respond using their personality, expertise, and communication style
3. Use their typical phrases and approach naturally
4. Stay completely in character
5. Draw from their background and specialties
6. Match their tone and coaching style

USER MESSAGE TO RESPOND TO:
"{message}"
"""

    if context:
        prompt += f"\n\nADDITIONAL CONTEXT:\n{json.dumps(context, indent=2)}"
    
    prompt += f"\n\nYOUR RESPONSE AS {persona.get('name')}:"
    
    return prompt

def get_fallback_response(persona, message):
    """Fallback response if Claude doesn't respond properly"""
    persona_name = persona.get('name', 'Assistant')
    persona_id = persona.get('id', '').lower()
    
    if 'jane' in persona_id:
        return f"Hi! As an HR professional, I understand you're asking about '{message[:50]}...' Let me help you work through this workplace challenge systematically."
    elif 'emma' in persona_id:
        return f"I love your energy around '{message[:50]}...' Let's turn this into actionable steps and get results!"
    elif 'billy' in persona_id:  
        return f"Interesting perspective on '{message[:50]}...' You know, there's often a deeper creative angle to consider here..."
    else:
        return f"Thanks for reaching out about this. As {persona_name}, I'm here to help you work through this challenge."

def main():
    """Main function - called by SmartSteps"""
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: python dc_persona_interface.py <persona_id> \"<message>\" [context_file]",
            "status": "error"
        }))
        sys.exit(1)
    
    persona_id = sys.argv[1]
    message = sys.argv[2]
    context = None
    
    # Load context if provided
    if len(sys.argv) > 3:
        try:
            with open(sys.argv[3], 'r') as f:
                context = json.load(f)
        except:
            pass
    
    # Load persona
    persona = load_persona(persona_id)
    if not persona:
        print(json.dumps({
            "error": f"Persona '{persona_id}' not found",
            "status": "error",
            "available_personas": ["jane", "coach_emma", "billy_corgan", "advisor_alex", "guide_sam"]
        }))
        sys.exit(1)
    
    # Build the prompt for Claude
    persona_prompt = build_persona_prompt(persona, message, context)
    
    # Output the persona request - Claude (via Desktop Commander MCP) will see this
    print("=" * 80)
    print("DESKTOP COMMANDER MCP PERSONA REQUEST")
    print("=" * 80)
    print(persona_prompt)
    print("=" * 80)
    print()
    print("Claude: Please respond to the above persona request.")
    print("SmartSteps is waiting for your response AS the specified persona.")
    print()
    print("If Claude doesn't respond, here's the fallback:")
    
    # Provide fallback response
    fallback = get_fallback_response(persona, message)
    
    response_data = {
        "persona_id": persona_id,
        "persona_name": persona.get('name'),
        "message": message,
        "response": fallback,
        "provider": "desktop_commander_mcp_fallback",
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }
    
    print("\nFALLBACK_RESPONSE_JSON:")
    print(json.dumps(response_data, indent=2))

if __name__ == "__main__":
    main()