"""
Vortex Engine API Router
Provides control endpoints for the hardened trading engine.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict
from backend.core.dependencies import get_current_user

router = APIRouter(
    prefix="/vortex",
    tags=["vortex"],
    responses={404: {"description": "Not found"}},
)


@router.post("/start")
async def start_vortex(request: Request, current_user: Dict = Depends(get_current_user)):
    """Start the Vortex Berserker Engine."""
    try:
        vortex = request.app.state.vortex
        await vortex.start()
        
        return {
            "status": "running",
            "message": "Vortex Berserker Engine activated",
            "configuration": vortex.get_status()['configuration']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_vortex(request: Request, current_user: Dict = Depends(get_current_user)):
    """Stop the Vortex Berserker Engine and close all positions."""
    try:
        vortex = request.app.state.vortex
        await vortex.stop()
        
        return {
            "status": "stopped",
            "message": "Vortex engine stopped, all positions closed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_vortex_status(request: Request):
    """Get current status of the Vortex engine."""
    try:
        vortex = request.app.state.vortex
        return vortex.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions")
async def get_positions(request: Request, current_user: Dict = Depends(get_current_user)):
    """Get all active positions in the vortex engine."""
    try:
        vortex = request.app.state.vortex
        status = vortex.get_status()
        
        return {
            "positions": status['positions'],
            "count": status['active_positions']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

