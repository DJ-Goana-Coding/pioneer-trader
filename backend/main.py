from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.core.config import settings
from backend.core.security_constants import MIN_API_KEY_LENGTH, MIN_SECRET_KEY_LENGTH
from backend.routers import auth, telemetry, brain, vortex
from backend.services.swarm import SwarmController
from backend.services.malware_protection import scanner
from backend.services.archival import archival_service
from backend.services.vortex import VortexBerserker

def is_placeholder_credential(value: str) -> bool:
    """
    Check if a credential value appears to be a placeholder.
    
    Args:
        value: The credential value to check
        
    Returns:
        True if value is a placeholder, False if it appears to be a real credential
    """
    if not value:
        return True
    if "PLACEHOLDER" in value.upper():
        return True
    if "YOUR_" in value.upper():
        return True
    if len(value) < MIN_API_KEY_LENGTH:  # Real API keys are typically longer
        return True
    return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("=" * 80)
    print(f"🔥 BERSERKER V6.9 - Hardened MEXC Trading Engine")
    print(f"Mode: {settings.EXECUTION_MODE} | UI Theme: {settings.UI_THEME}")
    print(f"Safety Modulator: {settings.SAFETY_MODULATOR}/10")
    
    # 🛡️ SECURITY CHECK: Validate credentials are not placeholders
    if settings.EXECUTION_MODE in ["LIVE", "TESTNET"]:
        security_warnings = []
        
        if is_placeholder_credential(settings.MEXC_API_KEY):
            security_warnings.append("❌ MEXC_API_KEY is not configured or contains PLACEHOLDER")
        
        if is_placeholder_credential(settings.MEXC_SECRET_KEY):
            security_warnings.append("❌ MEXC_SECRET_KEY is not configured or contains PLACEHOLDER")
        
        if is_placeholder_credential(settings.SECRET_KEY) or len(settings.SECRET_KEY) < MIN_SECRET_KEY_LENGTH:
            security_warnings.append(f"❌ SECRET_KEY is weak (minimum {MIN_SECRET_KEY_LENGTH} characters) or contains placeholder text")
        
        if security_warnings:
            print("\n" + "!" * 80)
            print("🚨 SECURITY ERROR: Cannot start in LIVE/TESTNET mode with placeholder credentials!")
            print("!" * 80)
            for warning in security_warnings:
                print(warning)
            print("\n📋 Action Required:")
            print("1. Copy .env.example to .env")
            print("2. Replace PLACEHOLDER values with your actual MEXC credentials")
            print("3. NEVER commit the .env file to git")
            print("4. See SECURITY_CHECKLIST.md for detailed instructions")
            print("!" * 80)
            raise ValueError("Invalid credentials - cannot start in LIVE mode with placeholders")
    
    print("=" * 80)
    
    # ⚡ PRIMARY SERVICE: Vortex Berserker Engine (MEXC-exclusive)
    vortex_engine = VortexBerserker()
    await vortex_engine.initialize()
    print(f"🔥 Vortex Berserker: ARMED")
    print(f"   Stake: ${settings.VORTEX_STAKE_USDT} USDT per trade")
    print(f"   Ejector Seat: {settings.VORTEX_STOP_LOSS_PCT*100}% stop-loss (MANDATORY)")
    print(f"   Pulse: {settings.VORTEX_PULSE_SECONDS}s aggressive interval")
    print(f"   Slots: 7 parallel ({len(vortex_engine.universe)} pairs)")
    print(f"   Exchange: MEXC ONLY (market orders only)")
    
    # Initialize V19 Swarm Intelligence
    swarm = SwarmController()
    await swarm.initialize()
    print(f"🧠 Phi-3.5 Swarm: {settings.PHI_DRONE_COUNT} drones active")
    
    # Initialize malware protection
    print(f"🛡️ Red Flag Malware Scanner: {scanner.get_status()['status']}")
    
    # Initialize archival
    print(f"📦 Shadow Archive: {settings.SHADOW_ARCHIVE_PATH}")
    
    # Dependency Injection - Vortex is the PRIMARY trading engine
    app.state.vortex = vortex_engine
    app.state.swarm = swarm
    app.state.scanner = scanner
    app.state.archival = archival_service
    
    print("=" * 80)
    print("✅ BERSERKER V6.9 ONLINE - All systems operational")
    print("=" * 80)
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Berserker V6.9...")
    await vortex_engine.shutdown()
    await swarm.shutdown()
    print("✅ Clean shutdown complete")

app = FastAPI(
    title="Berserker V6.9 - MEXC Trading Engine",
    version="6.9.0",
    lifespan=lifespan
)

# Include Routers - Only active routers for Berserker V6.9
app.include_router(auth.router)
app.include_router(telemetry.router)
app.include_router(brain.router)
app.include_router(vortex.router)  # PRIMARY trading interface

@app.get("/")
async def root():
    return {
        "message": "🔥 Berserker V6.9 Online - Hardened MEXC Trading Engine",
        "mode": settings.EXECUTION_MODE,
        "exchange": "MEXC",
        "ui_theme": settings.UI_THEME,
        "safety_modulator": settings.SAFETY_MODULATOR,
        "version": "6.9.0",
        "warning": "Market orders only - No limit orders - Mandatory 1.5% stop-loss"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
