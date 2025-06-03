#!/usr/bin/env python3
"""
Config Management API Extensions
Doc Brown's Temporal Configuration Control Endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
from pathlib import Path

from core.config_manager import config_manager, reload_valis_engine

# Create config management router
config_router = APIRouter(prefix="/config", tags=["configuration"])

class ConfigUpdateRequest(BaseModel):
    config: Dict[str, Any]
    force: bool = False
    create_snapshot: bool = True

class ConfigResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class SnapshotRequest(BaseModel):
    description: str = "Manual snapshot"

@config_router.get("/current", response_model=ConfigResponse)
async def get_current_config():
    """Get current active configuration"""
    try:
        # Use cross-platform path resolution
        config_file = Path(__file__).parent.parent / "config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            return ConfigResponse(
                success=True,
                message="Current config retrieved",
                data=config_data
            )
        else:
            return ConfigResponse(
                success=False,
                message="Config file not found"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading config: {e}")

@config_router.get("/ui", response_model=ConfigResponse)
async def get_ui_config():
    """Get UI editing configuration (.valis_config.json)"""
    try:
        # Use cross-platform path resolution
        ui_config_file = Path(__file__).parent.parent / ".valis_config.json"
        if ui_config_file.exists():
            with open(ui_config_file, 'r') as f:
                config_data = json.load(f)
            return ConfigResponse(
                success=True,
                message="UI config retrieved",
                data=config_data
            )
        else:
            # Create UI config from current config
            config_manager.copy_to_ui_config()
            return await get_ui_config()  # Recursive call after creation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading UI config: {e}")

@config_router.post("/apply", response_model=ConfigResponse)
async def apply_ui_config(force: bool = False, background_tasks: BackgroundTasks = None):
    """Apply UI configuration to active system"""
    try:
        success, message = config_manager.apply_ui_config(force=force)
        
        if success and background_tasks:
            # Schedule engine reload in background
            background_tasks.add_task(reload_valis_engine)
        
        return ConfigResponse(
            success=success,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying config: {e}")
