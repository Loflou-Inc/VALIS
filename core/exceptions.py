"""
VALIS Custom Exceptions
Provides specific exception types for better error handling and debugging
"""


class ValisError(Exception):
    """Base exception for all VALIS-related errors"""
    pass


class PersonaError(ValisError):
    """Errors related to persona management and state"""
    pass


class PersonaNotFoundError(PersonaError):
    """Raised when a requested persona cannot be found"""
    pass


class PersonaLoadError(PersonaError):
    """Raised when a persona fails to load properly"""
    pass


class AlignmentError(ValisError):
    """Errors related to trait alignment calculations"""
    pass


class AlignmentCalculationError(AlignmentError):
    """Raised when alignment calculation fails due to invalid input"""
    pass


class EmotionError(ValisError):
    """Errors related to emotion classification and state management"""
    pass


class EmotionClassificationError(EmotionError):
    """Raised when emotion classification fails"""
    pass

class MemoryError(ValisError):
    """Errors related to memory operations"""
    pass


class MemoryConsolidationError(MemoryError):
    """Raised when memory consolidation process fails"""
    pass


class MemoryQueryError(MemoryError):
    """Raised when memory queries fail"""
    pass


class MortalityError(ValisError):
    """Errors related to agent mortality and lifecycle"""
    pass


class FinalThoughtsGenerationError(MortalityError):
    """Raised when final thoughts generation fails"""
    pass


class LegacyScoreCalculationError(MortalityError):
    """Raised when legacy score calculation fails"""
    pass


class ReflectionError(ValisError):
    """Errors related to agent reflection and metacognition"""
    pass


class ReflectionGenerationError(ReflectionError):
    """Raised when reflection generation fails"""
    pass


class DatabaseError(ValisError):
    """Errors related to database operations"""
    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails"""
    pass


class ConfigurationError(ValisError):
    """Errors related to system configuration"""
    pass


class ProviderError(ValisError):
    """Errors related to AI provider operations"""
    pass