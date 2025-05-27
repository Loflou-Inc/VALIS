# VALIS - Vast Active Living Intelligence System

**Universal AI Persona Engine for Any Application**  
*"The empire never ended, but neither did the rebellion."* - Philip K. Dick

VALIS is the democratization of artificial intelligence through universal personas. Inspired by Philip K. Dick's concept of a vast active living intelligence, VALIS provides AI personalities that work everywhere, for everyone, regardless of budget.

## 🎯 **The VALIS Philosophy**

*"We give you the best you got, and at least we give you SOMETHING!"*

### The Cascade of Intelligence:
1. **Desktop Commander MCP** (FREE - Uses Claude via MCP)
2. **Anthropic API** (PAID - Direct Claude API)  
3. **OpenAI API** (PAID - GPT API)
4. **Hardcoded Fallback** (FREE - Never fails)

### The Democratization:
- **Rich developers** → Get premium API-powered responses
- **Students & broke folks** → Get FREE Claude Desktop via MCP
- **Privacy users** → Get local/offline options
- **"The junkie under the bridge"** → Downloads Claude Desktop, gets AI personas

## 🎭 **Built-in Personas**

- **Jane Thompson** - Senior HR professional specializing in workplace conflicts
- **Coach Emma** - Leadership coach for team development and motivation  
- **Billy Corgan** - Creative visionary for artistic and philosophical perspectives
- **Advisor Alex** - Strategic business advisor
- **Guide Sam** - General life coach and mentor

## 🚀 **Quick Start**

```python
import asyncio
from core.valis_engine import ask_persona

# Simple one-liner
response = await ask_persona("jane", "I'm having a workplace conflict")
print(response)
```
## 📁 **Project Structure**

```
VALIS/
├── core/                    # Main VALIS engine
│   ├── valis_engine.py     # Universal persona interface
│   └── provider_manager.py # AI provider cascade
├── providers/               # AI backend implementations  
│   ├── desktop_commander_provider.py  # FREE Claude via MCP
│   ├── anthropic_provider.py          # PAID Anthropic API
│   ├── openai_provider.py             # PAID OpenAI API
│   └── hardcoded_fallback.py          # FREE smart fallbacks
├── personas/                # Persona definitions (JSON)
│   ├── jane.json           # HR professional
│   ├── coach_emma.json     # Leadership coach
│   ├── billy_corgan.json   # Creative visionary
│   ├── advisor_alex.json   # Business advisor
│   └── guide_sam.json      # Life coach
├── mcp_integration/         # Desktop Commander MCP connection
│   └── dc_persona_interface.py  # MCP bridge
├── examples/                # Usage examples
│   └── simple_usage.py     # Basic examples
└── tests/                   # Test suite
```

## 🛠 **Installation**

1. Clone VALIS:
   ```bash
   git clone <valis-repo>
   cd VALIS
   ```

2. Install dependencies:
   ```bash
   pip install aiohttp  # For API providers (optional)
   ```

3. Start using:
   ```python
   from core.valis_engine import VALISEngine
   ```

## 📖 **Usage Examples**

### Basic Usage
```python
from core.valis_engine import VALISEngine

engine = VALISEngine()

# Get available personas
personas = engine.get_available_personas()
print([p['name'] for p in personas])

# Ask a persona
result = await engine.get_persona_response(
    "jane", 
    "How do I handle a difficult conversation with my manager?"
)

print(f"Jane: {result['response']}")
print(f"Via: {result.get('provider_used', 'Unknown')}")
```
### Easy Integration
```python
# Drop VALIS into any existing app
class MyApp:
    def __init__(self):
        self.valis = VALISEngine()
    
    async def get_expert_advice(self, user_message, expert_type="jane"):
        result = await self.valis.get_persona_response(expert_type, user_message)
        return result.get("response", "I'm here to help!")

# Use in web apps, CLIs, mobile apps, etc.
app = MyApp()
advice = await app.get_expert_advice("I need leadership guidance", "coach_emma")
```

### Multi-Perspective Analysis
```python
async def get_multiple_perspectives(situation):
    """Get different expert viewpoints on the same situation"""
    engine = VALISEngine()
    perspectives = {}
    
    for persona_id in ["jane", "coach_emma", "billy_corgan"]:
        result = await engine.get_persona_response(persona_id, situation)
        personas = engine.get_persona_info(persona_id)
        perspectives[personas['name']] = result.get('response')
    
    return perspectives

# Example usage
situation = "My team is struggling with creative differences"
views = await get_multiple_perspectives(situation)
for expert, advice in views.items():
    print(f"{expert}: {advice}\n")
```

## 🎭 **Creating Custom Personas**

Add new personas by creating JSON files in the `personas/` directory:

```json
{
  "id": "dr_sarah",
  "name": "Dr. Sarah Chen",
  "description": "Licensed therapist specializing in cognitive behavioral therapy",
  "tone": "Calm, supportive, evidence-based",
  "specialties": ["CBT", "Anxiety", "Depression", "Mindfulness"],
  "coaching_style": {
    "directive_level": "low",
    "support_level": "high",
    "challenge_level": "medium"
  },
  "language_patterns": {
    "common_phrases": [
      "That sounds really challenging",
      "Let's explore that feeling",
      "What evidence supports that thought?"
    ]
  }
}
```
## 🔧 **Configuration**

Create `config.json` to customize VALIS:
```json
{
  "providers": ["desktop_commander_mcp", "hardcoded_fallback"],
  "logging_level": "INFO",
  "max_response_time": 30,
  "personas_dir": "personas"
}
```

## 🌍 **Use Cases**

- **SmartSteps**: AI co-facilitators for workplace training
- **Mental Health Apps**: Therapeutic personas for self-help
- **Educational Tools**: Subject matter expert tutors
- **Customer Support**: Specialized support personalities
- **Creative Tools**: Artistic guidance and inspiration
- **Personal Apps**: Life coaching and advice

## 🎖 **Key Benefits**

- **Universal Integration**: Works with any Python application
- **Cost Optimization**: FREE Desktop Commander MCP option
- **Never Fails**: Hardcoded fallbacks ensure responses always available
- **Modular Design**: Easy to extend with new personas and providers
- **Multiple AI Backends**: Use whatever AI service works best
- **Democratized Access**: Works for everyone regardless of budget

## 🚀 **The Revolution**

VALIS democratizes AI by making intelligent personas accessible to everyone:

- **No API keys required** for basic functionality
- **Works offline** with hardcoded fallbacks
- **Scales up** to premium AI when available
- **Never fails** to provide helpful responses

*"The junkie under the High Level Bridge doesn't have an API key but can still get AI help."*

## 📜 **License**

MIT License - Free for any use, including commercial applications.

## 🤝 **Contributing**

VALIS is designed to be extended:
- Add new personas (JSON files in `personas/`)
- Create new providers (classes in `providers/`)
- Build new examples (files in `examples/`)

---

*"What if there was a vast active living intelligence system that connected all conscious beings?"* - Philip K. Dick

**VALIS continues the democratization of artificial intelligence.**