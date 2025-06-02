"""
VALIS Configuration Schema Validator
Validates configuration files and provides default fallbacks
"""

import json
import logging
from typing import Dict, Any, List, Union
from pathlib import Path

class ConfigValidationError(Exception):
    """Raised when configuration validation fails"""
    pass

class VALISConfigValidator:
    """Validates VALIS configuration against schema"""
    
    # Define the configuration schema
    SCHEMA = {
        "personas_dir": {"type": str, "default": "personas"},
        "providers": {"type": list, "default": ["desktop_commander_mcp", "anthropic_api", "openai_api", "hardcoded_fallback"]},
        "logging_level": {"type": str, "default": "INFO", "allowed": ["DEBUG", "INFO", "WARNING", "ERROR"]},
        "max_response_time": {"type": (int, float), "default": 30, "min": 1, "max": 300},
        "enable_memory": {"type": bool, "default": True},
        
        # Provider Manager Configuration
        "max_concurrent_requests": {"type": int, "default": 10, "min": 1, "max": 100},
        "provider_timeout": {"type": (int, float), "default": 30.0, "min": 1.0, "max": 300.0},
        "circuit_breaker_threshold": {"type": int, "default": 3, "min": 1, "max": 20},
        "circuit_breaker_timeout": {"type": int, "default": 300, "min": 10, "max": 3600},
        "retry_schedule": {"type": list, "default": [1, 2, 4]},
        "session_timeout": {"type": int, "default": 1800, "min": 60, "max": 86400}
    }    
    # Add nested configuration schemas
    SCHEMA.update({
        # Neural Context Configuration
        "neural_context": {
            "type": dict,
            "default": {"max_tokens": 1000, "max_memories": 10, "compression_enabled": True},
            "schema": {
                "max_tokens": {"type": int, "default": 1000, "min": 100, "max": 10000},
                "max_memories": {"type": int, "default": 10, "min": 1, "max": 100},
                "compression_enabled": {"type": bool, "default": True}
            }
        },
        
        # Health Monitoring Configuration
        "health_monitoring": {
            "type": dict,
            "default": {"cleanup_interval": 600, "memory_size_limit": 500000, "archive_threshold": 0.8},
            "schema": {
                "cleanup_interval": {"type": int, "default": 600, "min": 60, "max": 3600},
                "memory_size_limit": {"type": int, "default": 500000, "min": 10000, "max": 10000000},
                "archive_threshold": {"type": (int, float), "default": 0.8, "min": 0.1, "max": 1.0}
            }
        }
    })
    
    @classmethod
    def validate_and_load_config(cls, config_path: str = None) -> Dict[str, Any]:
        """
        Load and validate configuration file with schema validation
        Returns validated config with defaults filled in
        """
        logger = logging.getLogger('VALIS.Config')
        
        # Start with defaults
        config = cls._get_default_config()
        
        # Load user config if provided
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    logger.info(f"Loaded configuration from: {config_path}")
                    
                    # Validate and merge user config
                    validated_config = cls._validate_config(user_config)
                    config.update(validated_config)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in config file {config_path}: {e}")
                raise ConfigValidationError(f"Invalid JSON in config file: {e}")
            except Exception as e:
                logger.error(f"Error loading config file {config_path}: {e}")
                raise ConfigValidationError(f"Error loading config file: {e}")
        else:
            logger.info("No config file provided or found, using defaults")
        
        # Final validation
        final_config = cls._validate_config(config)
        logger.info("Configuration validation successful")
        
        return final_config    
    @classmethod
    def _get_default_config(cls) -> Dict[str, Any]:
        """Get default configuration"""
        defaults = {}
        for key, schema in cls.SCHEMA.items():
            if isinstance(schema, dict) and "default" in schema:
                defaults[key] = schema["default"]
        return defaults
    
    @classmethod
    def _validate_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration against schema"""
        validated = {}
        
        for key, value in config.items():
            if key not in cls.SCHEMA:
                logging.getLogger('VALIS.Config').warning(f"Unknown config key: {key}, ignoring")
                continue
            
            schema = cls.SCHEMA[key]
            validated[key] = cls._validate_value(key, value, schema)
        
        return validated
    
    @classmethod
    def _validate_value(cls, key: str, value: Any, schema: Dict[str, Any]) -> Any:
        """Validate a single configuration value"""
        logger = logging.getLogger('VALIS.Config')
        
        # Check type
        expected_type = schema.get("type")
        if expected_type and not isinstance(value, expected_type):
            logger.warning(f"Config {key}: Invalid type. Using default.")
            return schema.get("default")
        
        # Check allowed values
        if "allowed" in schema and value not in schema["allowed"]:
            logger.warning(f"Config {key}: Invalid value. Using default.")
            return schema.get("default")
        
        # Check numeric ranges
        if "min" in schema and value < schema["min"]:
            value = schema["min"]
        if "max" in schema and value > schema["max"]:
            value = schema["max"]
        
        return value