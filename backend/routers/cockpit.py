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
from backend.services.garage_manager import garage_manager, GarageBay

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
            "tia_admiral_bridge": "ACTIVE",
            "garage_manager": "ACTIVE"
        }
    }


# ═══════════════════════════════════════════════════════════
# GARAGE ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/garage/status")
async def get_garage_status():
    """Get Genesis Garage status
    
    Returns:
        Complete garage status including active bay and available Ferraris
    """
    garage_status = garage_manager.get_garage_status()
    tia_status = tia_agent.get_status()
    
    return {
        "garage": garage_status,
        "tia_risk": tia_status["risk_level"],
        "recommended_bay": garage_manager.get_bay_for_risk(
            tia_agent.current_risk
        ).value
    }


@router.post("/garage/select")
async def select_ferrari(bay: Optional[str] = None):
    """Select a Ferrari from the garage
    
    Args:
        bay: Optional bay name to force selection (01_ELITE, 02_ATOMIC, etc.)
             If not provided, T.I.A. selects based on risk level
    
    Returns:
        Selection result with active Ferrari details
    """
    try:
        force_bay = GarageBay(bay) if bay else None
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid bay: {bay}. Must be one of: {[b.value for b in GarageBay]}"
        )
    
    engine = garage_manager.select_ferrari(force_bay=force_bay)
    
    if engine:
        return {
            "success": True,
            "message": f"Ferrari {garage_manager.current_bay.value} selected and active",
            "active_bay": garage_manager.current_bay.value,
            "engine_status": engine.get_status() if hasattr(engine, 'get_status') else None
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load Ferrari from bay {bay or 'auto-selected'}"
        )


@router.post("/garage/reload")
async def reload_garage_engines():
    """Reload all garage engines (clear cache)
    
    Useful after manually updating Ferrari code.
    
    Returns:
        Reload confirmation
    """
    garage_manager.reload_engines()
    
    return {
        "success": True,
        "message": "Garage engines cache cleared. Engines will reload on next selection."
    }


@router.post("/garage/execute")
async def execute_garage_strategy(market_data: dict, config: Optional[dict] = None):
    """Execute the currently active Ferrari's strategy
    
    Args:
        market_data: Current market data and indicators
        config: Optional strategy configuration
    
    Returns:
        Trading signals and recommendations from active Ferrari
    """
    result = garage_manager.execute_current_strategy(market_data, config)
    
    return {
        "result": result,
        "active_bay": garage_manager.current_bay.value if garage_manager.current_bay else None,
        "tia_risk": tia_agent.get_status()["risk_level"]
    }
