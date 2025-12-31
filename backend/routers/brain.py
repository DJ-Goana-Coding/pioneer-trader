from fastapi import APIRouter, Depends, Request
from backend.core.security import get_current_user

router = APIRouter(prefix="/brain", tags=["brain"])

# V19 Enhanced Knowledge Base
KNOWLEDGE_BASE = {
    "strategies": [
        {"name": "Golden Cross", "description": "SMA 20 crosses above SMA 50"},
        {"name": "RSI Oversold", "description": "RSI < 30 indicates potential buy"},
        {"name": "Swarm Consensus", "description": "6x Phi-3.5 drones vote on market direction"}
    ],
    "risk_rules": [
        {"rule": "Max Notional", "value": "100 USDT"},
        {"rule": "Stop Loss", "value": "2%"},
        {"rule": "Safety Modulator", "value": "0-10 scale for trade aggression"}
    ],
    "v19_architecture": {
        "node_08": "Pioneer Trader - Jules Execution Engine",
        "swarm": "6x Phi-3.5 Mini (INT4) drones",
        "security": "Red Flag Malware Hunter",
        "archival": "Shadow Archive (1TB persistent storage)",
        "ui": "T.I.A. Citadel - Overkill/Zen modes"
    },
    "fleet_nodes": [
        {"id": "Node 01", "name": "T.I.A's Citadel", "role": "Infinite Cockpit", "cpu": "8 vCPU (Pro)"},
        {"id": "Node 02", "name": "Pioneer Trader", "role": "Jules Execution", "cpu": "8 vCPU (Pro)"},
        {"id": "Node 04-07", "name": "Sentinel Scout", "role": "Ant Swarm", "cpu": "6 vCPU total"},
        {"id": "Node 09", "name": "Soul Vault", "role": "Shadow Archive", "cpu": "1TB Storage"}
    ]
}

@router.get("/knowledge", dependencies=[Depends(get_current_user)])
async def get_knowledge():
    return KNOWLEDGE_BASE

@router.get("/fleet-status", dependencies=[Depends(get_current_user)])
async def get_fleet_status(request: Request):
    """Get V19 Fleet status"""
    swarm = request.app.state.swarm
    scanner = request.app.state.scanner
    archival = request.app.state.archival
    
    return {
        "fleet": "V19 Distributed Hive",
        "nodes": KNOWLEDGE_BASE["fleet_nodes"],
        "swarm_status": swarm.get_status(),
        "security_status": scanner.get_status(),
        "archival_status": archival.get_session_stats()
    }
