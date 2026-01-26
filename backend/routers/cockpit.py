# ================================================================
# 🎛️ COCKPIT ROUTER - T.I.A. Command Center API
# ================================================================
# API endpoints for the T.I.A. Cockpit Dashboard
# Connects T.I.A., Admiral, and Vortex for unified control
# ================================================================

from fastapi import APIRouter, Request, HTTPException
from typing import Optional
from pydantic import BaseModel

from backend.services.tia_agent import tia_agent
from backend.services.admiral_engine import admiral_engine
from backend.services.tia_admiral_bridge import tia_admiral_bridge

router = APIRouter(prefix="/cockpit", tags=["cockpit"])


# ═══════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════

class AuthorizeRequest(BaseModel):
    """Request to authorize Admiral"""
    force: bool = False  # Force authorization even if risk is HIGH


class RevokeRequest(BaseModel):
    """Request to revoke Admiral access"""
    reason: str = "Manual revocation"


class AegisSnapshot(BaseModel):
    """System snapshot for T.I.A. analysis"""
    wallet_balance: float
    total_equity: float
    active_slots: int
    starting_capital: float = 94.50


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/status")
async def get_cockpit_status(request: Request):
    """Get full cockpit status (T.I.A. + Admiral + Vortex)
    
    Returns:
        Complete system status for the cockpit dashboard
    """
    # Get T.I.A. status
    tia_status = tia_agent.get_status()
    
    # Get Admiral status
    admiral_status = admiral_engine.get_status()
    
    # Get Vortex status from app state (if available)
    vortex_status = {}
    if hasattr(request.app.state, "vortex"):
        vortex = request.app.state.vortex
        vortex_status = {
            "wallet_balance": vortex.wallet_balance,
            "total_equity": vortex.total_equity,
            "total_profit": vortex.total_profit,
            "active_slots": vortex.active_slots,
            "is_slot_guarded": vortex.is_slot_guarded
        }
    
    # Get bridge authorization status
    auth_status = tia_admiral_bridge.get_authorization_status()
    
    return {
        "status": "ACTIVE",
        "timestamp": tia_status["last_assessment"],
        "tia": tia_status,
        "admiral": admiral_status,
        "vortex": vortex_status,
        "authorization": auth_status
    }


@router.post("/authorize")
async def authorize_admiral(req: AuthorizeRequest):
    """T.I.A. authorizes Admiral for premium access
    
    Args:
        req: Authorization request with optional force flag
        
    Returns:
        Authorization result
    """
    result = tia_admiral_bridge.authorize_admiral(force=req.force)
    
    if not result["success"]:
        raise HTTPException(status_code=403, detail=result["message"])
    
    return result


@router.post("/revoke")
async def revoke_admiral(req: RevokeRequest):
    """T.I.A. revokes Admiral's premium access
    
    Args:
        req: Revocation request with reason
        
    Returns:
        Revocation result
    """
    result = tia_admiral_bridge.revoke_admiral(reason=req.reason)
    return result


@router.get("/capabilities")
async def get_capabilities():
    """Get current Admiral capabilities
    
    Returns:
        List of premium capabilities and their status
    """
    return tia_admiral_bridge.get_capabilities()


@router.get("/tia/summary")
async def get_tia_summary():
    """Get T.I.A.'s current risk assessment
    
    Returns:
        T.I.A. risk summary with confidence and recommendations
    """
    summary = tia_agent.produce_summary()
    return summary


@router.post("/tia/consume")
async def consume_aegis_snapshot(snapshot: AegisSnapshot):
    """Feed system snapshot to T.I.A. for analysis
    
    Args:
        snapshot: Current system metrics
        
    Returns:
        Confirmation of snapshot consumption
    """
    tia_agent.consume_aegis(snapshot.dict())
    
    return {
        "success": True,
        "message": "Snapshot consumed by T.I.A.",
        "snapshots_in_buffer": len(tia_agent.aegis_snapshots)
    }


@router.get("/events")
async def get_authorization_events(limit: int = 20):
    """Get authorization event history
    
    Args:
        limit: Maximum number of events to return (default: 20)
        
    Returns:
        List of recent authorization events
    """
    events = tia_admiral_bridge.get_event_history(limit=limit)
    return {
        "events": events,
        "count": len(events)
    }


@router.get("/health")
async def cockpit_health():
    """Cockpit health check endpoint
    
    Returns:
        Health status of all cockpit components
    """
    return {
        "status": "HEALTHY",
        "components": {
            "tia_agent": "ACTIVE",
            "admiral_engine": "ACTIVE",
            "tia_admiral_bridge": "ACTIVE"
        }
    }
