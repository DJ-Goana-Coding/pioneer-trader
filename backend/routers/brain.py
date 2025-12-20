from fastapi import APIRouter, Depends
from backend.core.security import get_current_user

router = APIRouter(prefix="/brain", tags=["brain"])

# Static Brain Knowledge Base (Mock)
KNOWLEDGE_BASE = {
    "strategies": [
        {"name": "Golden Cross", "description": "SMA 20 crosses above SMA 50"},
        {"name": "RSI Oversold", "description": "RSI < 30 indicates potential buy"}
    ],
    "risk_rules": [
        {"rule": "Max Notional", "value": "100 USDT"},
        {"rule": "Stop Loss", "value": "2%"}
    ]
}

@router.get("/knowledge", dependencies=[Depends(get_current_user)])
async def get_knowledge():
    return KNOWLEDGE_BASE
