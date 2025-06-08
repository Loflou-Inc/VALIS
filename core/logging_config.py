"""
VALIS Structured Logging Configuration
Provides JSON-formatted logging with persona/session context
"""
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any


class ValisFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs with VALIS context"""
    
    def format(self, record):
        # Base log entry structure
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage()
        }
        
        # Add VALIS-specific context if available
        if hasattr(record, 'persona_id'):
            log_entry['persona_id'] = record.persona_id
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'alignment_score'):
            log_entry['alignment_score'] = record.alignment_score
        if hasattr(record, 'emotion_state'):
            log_entry['emotion_state'] = record.emotion_state
        if hasattr(record, 'operation'):
            log_entry['operation'] = record.operation
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
            
        return json.dumps(log_entry)

class ValisLoggerAdapter(logging.LoggerAdapter):
    """Adapter that automatically adds VALIS context to log records"""
    
    def __init__(self, logger, persona_id=None, session_id=None):
        self.persona_id = persona_id
        self.session_id = session_id
        super().__init__(logger, {})
    
    def process(self, msg, kwargs):
        # Add context to every log record
        extra = kwargs.get('extra', {})
        if self.persona_id:
            extra['persona_id'] = self.persona_id
        if self.session_id:
            extra['session_id'] = self.session_id
        kwargs['extra'] = extra
        return msg, kwargs


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Set up structured logging for VALIS"""
    logger = logging.getLogger('valis')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ValisFormatter())
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(ValisFormatter())
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_valis_logger(persona_id: Optional[str] = None, session_id: Optional[str] = None) -> ValisLoggerAdapter:
    """Get a VALIS logger with automatic context injection"""
    base_logger = logging.getLogger('valis')
    return ValisLoggerAdapter(base_logger, persona_id, session_id)

# Performance monitoring helpers
def log_operation_start(logger: logging.Logger, operation: str, **context):
    """Log the start of an operation with timing context"""
    extra = {'operation': operation, 'phase': 'start', **context}
    logger.info(f"Starting {operation}", extra=extra)


def log_operation_end(logger: logging.Logger, operation: str, success: bool = True, **context):
    """Log the completion of an operation"""
    extra = {'operation': operation, 'phase': 'end', 'success': success, **context}
    level = 'info' if success else 'error'
    getattr(logger, level)(f"Completed {operation}", extra=extra)


def log_alignment_check(logger: logging.Logger, persona_id: str, alignment_score: float, transcript_length: int):
    """Log trait alignment evaluation results"""
    extra = {
        'persona_id': persona_id,
        'alignment_score': alignment_score,
        'transcript_length': transcript_length,
        'operation': 'alignment_check'
    }
    logger.info(f"Alignment check completed: {alignment_score:.3f}", extra=extra)


def log_emotion_classification(logger: logging.Logger, persona_id: str, emotion_state: str, confidence: float):
    """Log emotion classification results"""
    extra = {
        'persona_id': persona_id,
        'emotion_state': emotion_state,
        'confidence': confidence,
        'operation': 'emotion_classification'
    }
    logger.info(f"Emotion classified as {emotion_state}", extra=extra)


def log_memory_consolidation(logger: logging.Logger, persona_id: str, memories_processed: int, symbolic_memories_created: int):
    """Log memory consolidation results"""
    extra = {
        'persona_id': persona_id,
        'memories_processed': memories_processed,
        'symbolic_memories_created': symbolic_memories_created,
        'operation': 'memory_consolidation'
    }
    logger.info(f"Memory consolidation: {memories_processed} -> {symbolic_memories_created}", extra=extra)