#!/usr/bin/env python3
"""
VALIS Structured Logging Configuration - Sprint 1.2
Professional logging setup with context tracking for cognitive operations
"""
import logging
import json
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path


class ValisLogFormatter(logging.Formatter):
    """
    Custom formatter for VALIS logs with structured JSON output
    Includes persona_id, session_id, and cognitive context
    """
    
    def format(self, record):
        """Format log record with VALIS-specific context"""
        
        # Extract VALIS-specific context from record
        persona_id = getattr(record, 'persona_id', None)
        session_id = getattr(record, 'session_id', None)
        cognitive_module = getattr(record, 'cognitive_module', None)
        operation = getattr(record, 'operation', None)
        error_type = getattr(record, 'error_type', None)
        
        # Build structured log entry
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Add VALIS context if available
        if persona_id:
            log_entry['persona_id'] = persona_id
        if session_id:
            log_entry['session_id'] = session_id
        if cognitive_module:
            log_entry['cognitive_module'] = cognitive_module
        if operation:
            log_entry['operation'] = operation
        if error_type:
            log_entry['error_type'] = error_type
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


class ValisLogger:
    """
    VALIS-specific logger with context management
    Tracks cognitive operations across the system
    """
    
    def __init__(self, name: str, log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
        
        self.context = {}
    
    def _setup_handlers(self):
        """Setup console and file handlers with structured formatting"""
        
        # Console handler with human-readable format for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = (
            '%(asctime)s | %(levelname)-8s | %(module)s.%(funcName)s:%(lineno)d | %(message)s'
        )
        console_handler.setFormatter(logging.Formatter(console_format))
        
        # File handler with JSON format for production
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "valis.jsonl")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(ValisLogFormatter())
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def set_context(self, **context):
        """Set persistent context for subsequent log messages"""
        self.context.update(context)
    
    def clear_context(self):
        """Clear persistent context"""
        self.context.clear()
    
    def _add_context(self, extra: Dict[str, Any]) -> Dict[str, Any]:
        """Add persistent context to log extra data"""
        merged = self.context.copy()
        if extra:
            merged.update(extra)
        return merged
    
    def debug(self, message: str, **extra):
        """Log debug message with context"""
        self.logger.debug(message, extra=self._add_context(extra))
    
    def info(self, message: str, **extra):
        """Log info message with context"""
        self.logger.info(message, extra=self._add_context(extra))
    
    def warning(self, message: str, **extra):
        """Log warning message with context"""
        self.logger.warning(message, extra=self._add_context(extra))
    
    def error(self, message: str, exc_info: bool = False, **extra):
        """Log error message with context and optional exception info"""
        self.logger.error(message, exc_info=exc_info, extra=self._add_context(extra))
    
    def critical(self, message: str, exc_info: bool = True, **extra):
        """Log critical message with context and exception info"""
        self.logger.critical(message, exc_info=exc_info, extra=self._add_context(extra))


# Global logger factory
_loggers = {}

def get_valis_logger(name: str, log_level: str = "INFO") -> ValisLogger:
    """
    Get or create a VALIS logger instance
    
    Args:
        name: Logger name (usually module name)
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        ValisLogger instance
    """
    if name not in _loggers:
        _loggers[name] = ValisLogger(name, log_level)
    return _loggers[name]


def configure_valis_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """
    Configure global VALIS logging settings
    
    Args:
        log_level: Global log level
        log_dir: Directory for log files
    """
    # Create log directory
    Path(log_dir).mkdir(exist_ok=True)
    
    # Configure root logger to prevent other libraries from interfering
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)  # Suppress noise from other libraries
    
    # Set VALIS namespace to desired level
    valis_logger = logging.getLogger('agents')
    valis_logger.setLevel(getattr(logging, log_level.upper()))
    
    memory_logger = logging.getLogger('memory')
    memory_logger.setLevel(getattr(logging, log_level.upper()))
    
    core_logger = logging.getLogger('core')
    core_logger.setLevel(getattr(logging, log_level.upper()))


# Context managers for cognitive operations
class CognitiveOperation:
    """Context manager for tracking cognitive operations"""
    
    def __init__(self, logger: ValisLogger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now(timezone.utc)
        self.logger.info(
            f"Starting {self.operation}",
            operation=self.operation,
            **self.context
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = datetime.now(timezone.utc) - self.start_time
        
        if exc_type is None:
            self.logger.info(
                f"Completed {self.operation}",
                operation=self.operation,
                duration_ms=duration.total_seconds() * 1000,
                **self.context
            )
        else:
            self.logger.error(
                f"Failed {self.operation}: {exc_val}",
                operation=self.operation,
                duration_ms=duration.total_seconds() * 1000,
                error_type=exc_type.__name__,
                exc_info=True,
                **self.context
            )
        
        return False  # Don't suppress exceptions


# Initialize logging on import
configure_valis_logging()
