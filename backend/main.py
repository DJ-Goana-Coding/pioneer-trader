from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.core.config import settings
from backend.core.security_constants import MIN_API_KEY_LENGTH, MIN_SECRET_KEY_LENGTH
from backend.routers import auth, telemetry, strategy, trade, brain, vortex
from backend.services.exchange import ExchangeService
from backend.services.oms import OMS
from backend.services.strategy_engine import StrategyEngine
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
    print(f"Starting Pioneer-Admiral V1 in {settings.EXECUTION_MODE} mode...")
    print(f"UI Theme: {settings.UI_THEME} | Safety Modulator: {settings.SAFETY_MODULATOR}")
    
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
            print("2. Replace PLACEHOLDER values with your actual credentials")
            print("3. NEVER commit the .env file to git")
            print("4. See SECURITY_CHECKLIST.md for detailed instructions")
            print("!" * 80)
            raise ValueError("Invalid credentials - cannot start in LIVE mode with placeholders")
    
    print("=" * 80)
    
    # Initialize Services
    exchange_service = ExchangeService()
    await exchange_service.initialize()
    
    strategy_engine = StrategyEngine()
    oms = OMS(exchange_service)
    
    # Initialize V19 Swarm
    swarm = SwarmController()
    await swarm.initialize()
    
    # Initialize malware protection
    print(f"🛡️ Red Flag Malware Protection: {scanner.get_status()['status']}")
    
    # Initialize archival
    print(f"📦 Shadow Archive: {settings.SHADOW_ARCHIVE_PATH}")
    
    # Initialize Vortex Berserker Engine
    vortex_engine = VortexBerserker()
    await vortex_engine.initialize()
    print(f"🔥 Vortex Berserker: Initialized (Stake=${settings.VORTEX_STAKE_USDT}, Stop-Loss={settings.VORTEX_STOP_LOSS_PCT*100}%)")
    
    # Dependency Injection
    app.state.exchange_service = exchange_service
    app.state.strategy_engine = strategy_engine
    app.state.oms = oms
    app.state.swarm = swarm
    app.state.scanner = scanner
    app.state.archival = archival_service
    app.state.vortex = vortex_engine
    
    yield
    
    # Shutdown
    print("Shutting down Pioneer-Admiral V1...")
    await vortex_engine.shutdown()
    await exchange_service.shutdown()
    await swarm.shutdown()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Include Routers
app.include_router(auth.router)
app.include_router(telemetry.router)
app.include_router(strategy.router)
app.include_router(trade.router)
app.include_router(brain.router)
app.include_router(vortex.router)

@app.get("/")
async def root():
    return {
        "message": "Pioneer-Admiral V1 Online - V19 Fleet Command",
        "mode": settings.EXECUTION_MODE,
        "ui_theme": settings.UI_THEME,
        "safety_modulator": settings.SAFETY_MODULATOR,
        "version": "V19"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
