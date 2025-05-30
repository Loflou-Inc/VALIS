"""
VALIS Providers Module
AI Provider implementations for VALIS
"""

from .desktop_commander_provider import DesktopCommanderProvider
from .hardcoded_fallback import HardcodedFallbackProvider

# Import API providers with graceful degradation
try:
    from .anthropic_provider import AnthropicProvider
    ANTHROPIC_AVAILABLE = True
except ImportError as e:
    AnthropicProvider = None
    ANTHROPIC_AVAILABLE = False

try:
    from .openai_provider import OpenAIProvider
    OPENAI_AVAILABLE = True
except ImportError as e:
    OpenAIProvider = None
    OPENAI_AVAILABLE = False

__all__ = [
    "DesktopCommanderProvider", 
    "HardcodedFallbackProvider",
    "AnthropicProvider",
    "OpenAIProvider"
]
