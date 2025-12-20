from fastapi import APIRouter, Depends
from backend.core.security import get_current_user
from backend.core.config import settings

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

@router.get("/health")
async def health_check():
    return {"status": "ok", "mode": settings.EXECUTION_MODE}

@router.get("/status", dependencies=[Depends(get_current_user)])
async def system_status():
    return {
        "system": "Pioneer-Admiral V1",
        "status": "operational",
        "mode": settings.EXECUTION_MODE,
        "risk_clamp": settings.MAX_ORDER_NOTIONAL
    }
