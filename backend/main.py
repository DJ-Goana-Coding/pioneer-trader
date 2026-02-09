# ================================================================
# 🚀 PIONEER TRADER BACKEND - CITADEL GATEWAY
# ================================================================
from fastapi import FastAPI, Depends
import asyncio
import uvicorn
from backend.core.logging_config import setup_logging
from backend.core.security import get_current_admin

logger = setup_logging("main")
app = FastAPI(title="Citadel API")

# GLOBAL ENGINE HOLDER
vortex = None

@app.on_event("startup")
async def startup_event():
    """Starts the Vortex Engine on API Ignition"""
    global vortex
    try:
        # DELAYED IMPORT TO PREVENT CIRCULAR LOOPS
        from backend.services.vortex import VortexBerserker
        vortex = VortexBerserker()
        
        # Engage Background Loop
        asyncio.create_task(vortex.start())
        logger.info("🏰 CITADEL: VortexBerserker Engine Engaged")
    except Exception as e:
        logger.error(f"🚨 IGNITION FAILURE: {e}")

@app.head("/")
async def health_check_head():
    """Health check endpoint for HEAD requests from deployment platforms"""
    return

@app.get("/")
async def root():
    return {"status": "Citadel Online", "engine": "Vortex V6.9 Berserker"}

@app.get("/health")
async def health():
    """Public health check endpoint for load balancers"""
    return {
        "status": "ok",
        "Safety Locks": "ENGAGED ✅"
    }

@app.get("/telemetry")
async def get_telemetry(current_user: str = Depends(get_current_admin)):
    """Protected telemetry endpoint - requires authentication"""
    if not vortex: 
        return {"status": "Starting..."}
    
    # Get slot allocation counts
    piranha_count = sum(1 for pos in vortex.active_slots.values() if pos.get('wing') == 'piranha')
    harvester_count = sum(1 for pos in vortex.active_slots.values() if pos.get('wing') == 'harvester')
    bear_count = sum(1 for pos in vortex.active_slots.values() if pos.get('wing') == 'bear')
    crab_count = sum(1 for pos in vortex.active_slots.values() if pos.get('wing') == 'crab')
    banker_count = sum(1 for pos in vortex.active_slots.values() if pos.get('wing') == 'banker')
    sniper_count = sum(1 for pos in vortex.active_slots.values() if pos.get('wing') == 'sniper')
    
    # Build fleet allocation string
    fleet_parts = []
    if piranha_count > 0:
        fleet_parts.append(f"{piranha_count} {'Piranha' if piranha_count == 1 else 'Piranhas'}")
    if harvester_count > 0:
        fleet_parts.append(f"{harvester_count} {'Harvester' if harvester_count == 1 else 'Harvesters'}")
    if bear_count > 0:
        fleet_parts.append(f"{bear_count} {'Bear' if bear_count == 1 else 'Bears'}")
    if crab_count > 0:
        fleet_parts.append(f"{crab_count} {'Crab' if crab_count == 1 else 'Crabs'}")
    if banker_count > 0:
        fleet_parts.append(f"{banker_count} Banker{'s' if banker_count > 1 else ''}")
    if sniper_count > 0:
        fleet_parts.append(f"{sniper_count} {'Sniper' if sniper_count == 1 else 'Snipers'}")
    
    fleet_allocation = " + ".join(fleet_parts) if fleet_parts else "No active positions"
    
    return {
        "status": "Active",
        "fleet_allocation": fleet_allocation,
        "wallet": f"${vortex.wallet_balance:.2f}" if hasattr(vortex, 'wallet_balance') else "N/A",
        "equity": f"${vortex.total_equity:.2f}" if hasattr(vortex, 'total_equity') else "N/A",
        "slots": vortex.slot_status if hasattr(vortex, 'slot_status') else {},
        "active_positions": len(vortex.active_slots) if hasattr(vortex, 'active_slots') else 0
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=7860)