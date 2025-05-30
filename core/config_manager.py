"""SPRINT 2.8: Configuration Manager"""

import json
import logging
from pathlib import Path
from typing import Optional
from pydantic import ValidationError
from core.config_schema import VALISConfig

class ConfigurationManager:
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger('VALIS.Config')
        self.config_path = Path(config_path) if config_path else Path("config.json")
        self._config: Optional[VALISConfig] = None
        
    def load_config(self) -> VALISConfig:
        """Load and validate configuration with graceful fallback"""
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                self._config = VALISConfig(**config_data)
                self.logger.info(f"Configuration loaded from {self.config_path}")
                return self._config
                
            except (json.JSONDecodeError, ValidationError, Exception) as e:
                self.logger.warning(f"Config load failed: {e}, using defaults")
        else:
            self.logger.info(f"Config file not found, using defaults")
        
        # Fallback to defaults
        self._config = VALISConfig()
        return self._config
    
    def get_config(self) -> VALISConfig:
        """Get current configuration, loading if necessary"""
        if self._config is None:
            return self.load_config()
        return self._config

# Global configuration manager instance
_config_manager = ConfigurationManager()

def get_config() -> VALISConfig:
    """Get the global VALIS configuration"""
    return _config_manager.get_config()
