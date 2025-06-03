# VALIS Provider Development Guide
## Creating Custom Intelligence Sources

### Overview
The VALIS Provider Registry enables plug-and-play AI provider development.
Adding new intelligence sources requires ZERO core code changes!

### Creating a Custom Provider

```python
# providers/my_custom_provider.py
from providers.base_provider import BaseProvider, register_provider

@register_provider("my_custom_ai")
class MyCustomProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self.name = "My Custom AI"
        self.cost = "FREE"
    
    async def is_available(self) -> bool:
        return True  # Add your availability logic
    
    async def get_response(self, persona, message, session_id=None, context=None):
        try:
            response_text = f"Hello from {persona.get('name', 'AI')}!"
            return {
                "success": True,
                "response": response_text,
                "provider": self.name,
                "metadata": {"tokens_used": 42}
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": self.name
            }
```

### Usage
Add `"my_custom_ai"` to your provider list config.

### Required Methods
- `async def is_available() -> bool`
- `async def get_response(...) -> dict`

### Response Format
Return dict with: `success`, `response`, `provider`, `error`, `metadata`

The democratization of AI is now truly extensible! 🚀
