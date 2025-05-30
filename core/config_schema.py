"""
SPRINT 2.8: Configurability Evolution - Configuration Schema
===========================================================

Pydantic schema to eliminate hardcoded temporal constants!
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional

class CircuitBreakerConfig(BaseModel):
    failure_threshold: int = Field(default=3, ge=1, le=10)
    timeout_minutes: int = Field(default=5, ge=1, le=60)

class PerformanceConfig(BaseModel):
    max_concurrent_requests: int = Field(default=10, ge=1, le=100)
    provider_timeout: int = Field(default=30, ge=5, le=300)
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)
    retry_schedule: List[int] = Field(default=[1, 2, 4], min_items=1, max_items=10)
    
    @validator('retry_schedule')
    def validate_retry_schedule(cls, v):
        if not all(delay > 0 and delay <= 60 for delay in v):
            raise ValueError("All retry delays must be between 1 and 60 seconds")
        return v

class FeaturesConfig(BaseModel):
    enable_neural_health_monitor: bool = True
    enable_circuit_breaker: bool = True
    enable_retry_logic: bool = True

class VALISConfig(BaseModel):
    providers: List[str] = Field(default=["desktop_commander_mcp", "hardcoded_fallback"])
    logging_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    enable_memory: bool = True
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)
    
    @validator('providers')
    def validate_providers(cls, v):
        if not v:
            raise ValueError("At least one provider must be specified")
        if 'hardcoded_fallback' not in v:
            v.append('hardcoded_fallback')
        return v
    
    class Config:
        extra = "allow"
        validate_assignment = True