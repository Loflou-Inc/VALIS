"""
VALIS Providers Module
AI Provider implementations for VALIS

Sprint 2 Cleanup: Only active, tested providers are imported.
Legacy providers moved to providers/legacy/
"""

# Import only active providers
from .desktop_commander_mcp_persistent import PersistentDesktopCommanderMCPProvider
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

# Clean registry - only active providers
__all__ = [
    "PersistentDesktopCommanderMCPProvider",  # Claude integration (persistent)
    "HardcodedFallbackProvider",              # Fallback provider
    "AnthropicProvider",                      # Anthropic API
    "OpenAIProvider"                          # OpenAI API
]
