from fastapi import APIRouter, Depends, Request
from backend.core.security import get_current_user
from backend.core.config import settings

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

@router.get("/health")
async def health_check():
    return {"status": "ok", "mode": settings.EXECUTION_MODE}

@router.get("/status", dependencies=[Depends(get_current_user)])
async def system_status(request: Request):
    swarm = request.app.state.swarm
    scanner = request.app.state.scanner
    archival = request.app.state.archival
    
    return {
        "system": "Pioneer-Admiral V1 - V19 Fleet Command",
        "status": "operational",
        "mode": settings.EXECUTION_MODE,
        "risk_clamp": settings.MAX_ORDER_NOTIONAL,
        "ui_theme": settings.UI_THEME,
        "safety_modulator": settings.SAFETY_MODULATOR,
        "swarm": swarm.get_status(),
        "security": scanner.get_status(),
        "archival": archival.get_archive_stats()
    }

@router.get("/swarm", dependencies=[Depends(get_current_user)])
async def swarm_status(request: Request):
    """Get detailed swarm status"""
    swarm = request.app.state.swarm
    return swarm.get_status()

@router.get("/security", dependencies=[Depends(get_current_user)])
async def security_status(request: Request):
    """Get security and malware protection status"""
    scanner = request.app.state.scanner
    return {
        "scanner": scanner.get_status(),
        "isolated_items": scanner.get_isolated_items()
    }

@router.get("/archival", dependencies=[Depends(get_current_user)])
async def archival_status(request: Request):
    """Get archival and logging status"""
    archival = request.app.state.archival
    return {
        "stats": archival.get_archive_stats(),
        "session": archival.get_session_stats(),
        "recent_logs": archival.get_recent_logs(10)
    }
