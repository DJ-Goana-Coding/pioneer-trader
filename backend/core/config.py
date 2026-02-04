# ================================================================
# ⚙️ PIONEER TRADER: UNIVERSAL CONFIG
# ================================================================
import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Pioneer Trader"
    
    # --- COMMANDER MANDATE: LIVE FIRE ---
    EXECUTION_MODE: str = "LIVE"
    VORTEX_STAKE_USDT: float = 8.0
    VORTEX_STOP_LOSS_PCT: float = 0.015
    
    # MEXC EXCHANGE CREDENTIALS (Primary)
    MEXC_API_KEY: str = os.getenv("MEXC_API_KEY", "")
    MEXC_SECRET: str = os.getenv("MEXC_SECRET", "")
    
    # LEGACY BINANCE (For migration reference - can be removed later)
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_SECRET_KEY: str = os.getenv("BINANCE_SECRET_KEY", "") or os.getenv("BINANCE_SECRET", "")
    
    # REDIS CONFIGURATION
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "True").lower() == "true"
    
    # RISK MANAGEMENT
    MAX_ORDER_NOTIONAL: float = float(os.getenv("MAX_ORDER_NOTIONAL", "50.0"))
    MIN_SLOT_SIZE: float = 8.0
    
    # SYSTEM CONFIG
    PORT: int = int(os.getenv("PORT", "10000"))
    DIAGNOSTIC_MODE: bool = os.getenv("DIAGNOSTIC_MODE", "True").lower() == "true"
    
    # V19 SECURITY & ARCHIVAL
    ENABLE_MALWARE_PROTECTION: bool = os.getenv("ENABLE_MALWARE_PROTECTION", "True").lower() == "true"
    SHADOW_ARCHIVE_PATH: str = os.getenv("SHADOW_ARCHIVE_PATH", "/tmp/shadow_archive")
    ENABLE_GITHUB_PAGES_EXPORT: bool = os.getenv("ENABLE_GITHUB_PAGES_EXPORT", "False").lower() == "true"

settings = Settings()

# DIRECT EXPORTS (For legacy imports)
MEXC_API_KEY = settings.MEXC_API_KEY
MEXC_SECRET = settings.MEXC_SECRET
