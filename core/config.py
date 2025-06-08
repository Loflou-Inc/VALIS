"""
VALIS Configuration Management - Sprint 1.3
Centralized, secure configuration loading with environment validation
"""
import os
import secrets
from dataclasses import dataclass
from typing import Optional, List
from dotenv import load_dotenv

from core.exceptions import ConfigurationError

@dataclass
class ValisConfig:
    """
    VALIS system configuration with validation and secure defaults
    All critical secrets must be provided via environment variables
    """
    # Database configuration
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    
    # API keys
    openai_api_key: Optional[str]
    anthropic_api_key: Optional[str]
    
    # Security
    secret_key: str
    admin_api_key: str
    jwt_secret: str
    
    # Deployment
    environment: str
    log_level: str
    host: str
    port: int
    
    # Cloud configuration (optional)
    cloud_db_host: Optional[str] = None
    cloud_db_password: Optional[str] = None
    @classmethod
    def from_env(cls, env_file: str = ".env") -> "ValisConfig":
        """
        Load configuration from environment variables
        
        Args:
            env_file: Path to .env file (default: ".env")
            
        Returns:
            ValisConfig instance
            
        Raises:
            ConfigurationError: If required environment variables are missing
        """
        # Load .env file if it exists
        if os.path.exists(env_file):
            load_dotenv(env_file)
        
        # Define required variables that MUST be set
        required_vars = [
            'VALIS_DB_PASSWORD',
            'VALIS_SECRET_KEY', 
            'VALIS_ADMIN_API_KEY',
            'VALIS_JWT_SECRET'
        ]
        
        # Check for missing required variables
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ConfigurationError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"Copy .env.template to .env and set these values."
            )
        
        # Validate critical secrets are not defaults
        dangerous_defaults = {
            'VALIS_DB_PASSWORD': ['valis123', 'password', 'valis2025'],
            'VALIS_ADMIN_API_KEY': ['valis_admin_2025', 'admin'],
            'VALIS_SECRET_KEY': ['your_secret_key_here', 'secret'],
            'VALIS_JWT_SECRET': ['your_jwt_secret_here', 'jwt']
        }
        
        for var, bad_values in dangerous_defaults.items():
            value = os.getenv(var, '')
            if value.lower() in [v.lower() for v in bad_values]:
                raise ConfigurationError(
                    f"{var} is set to a dangerous default value. "
                    f"Please set a secure value."
                )
        # Build and return configuration
        try:
            return cls(
                # Database
                db_host=os.getenv('VALIS_DB_HOST', 'localhost'),
                db_port=int(os.getenv('VALIS_DB_PORT', '5432')),
                db_name=os.getenv('VALIS_DB_NAME', 'valis2'),
                db_user=os.getenv('VALIS_DB_USER', 'valis'),
                db_password=os.getenv('VALIS_DB_PASSWORD'),  # Required, no default
                
                # API Keys (optional for some deployments)
                openai_api_key=os.getenv('OPENAI_API_KEY'),
                anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
                
                # Security (all required)
                secret_key=os.getenv('VALIS_SECRET_KEY'),
                admin_api_key=os.getenv('VALIS_ADMIN_API_KEY'),
                jwt_secret=os.getenv('VALIS_JWT_SECRET'),
                
                # Deployment
                environment=os.getenv('VALIS_ENV', 'development'),
                log_level=os.getenv('VALIS_LOG_LEVEL', 'INFO'),
                host=os.getenv('VALIS_HOST', 'localhost'),
                port=int(os.getenv('VALIS_PORT', '8000')),
                
                # Cloud (optional)
                cloud_db_host=os.getenv('VALIS_CLOUD_DB_HOST'),
                cloud_db_password=os.getenv('VALIS_CLOUD_DB_PASSWORD')
            )
        except (ValueError, TypeError) as e:
            raise ConfigurationError(f"Invalid configuration value: {e}")
    
    def validate(self) -> None:
        """Validate configuration values"""
        # Check secret key length
        if len(self.secret_key) < 16:
            raise ConfigurationError("VALIS_SECRET_KEY must be at least 16 characters")
        
        # Check admin key length
        if len(self.admin_api_key) < 12:
            raise ConfigurationError("VALIS_ADMIN_API_KEY must be at least 12 characters")
        
        # Validate environment
        valid_envs = ['development', 'staging', 'production']
        if self.environment not in valid_envs:
            raise ConfigurationError(f"VALIS_ENV must be one of: {', '.join(valid_envs)}")


def get_config() -> ValisConfig:
    """Get validated VALIS configuration"""
    config = ValisConfig.from_env()
    config.validate()
    return config