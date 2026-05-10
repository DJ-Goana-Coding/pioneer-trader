# ================================================================
# ⚙️ PIONEER TRADER: UNIVERSAL CONFIG
# ================================================================
import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Pioneer Trader"
    
    # --- COMMANDER MANDATE: PAPER TRADING BY DEFAULT ---
    EXECUTION_MODE: str = os.getenv("EXECUTION_MODE", "PAPER")
    VORTEX_STAKE_USDT: float = 8.0
    VORTEX_STOP_LOSS_PCT: float = 0.015
    
    # MEXC EXCHANGE CREDENTIALS (Primary)
    MEXC_API_KEY: str = os.getenv("MEXC_API_KEY", "")
    MEXC_SECRET: str = os.getenv("MEXC_SECRET", "")
    
    # LEGACY BINANCE (For migration reference - can be removed later)
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_SECRET_KEY: str = os.getenv("BINANCE_SECRET_KEY", "") or os.getenv("BINANCE_SECRET", "")
    
    # REDIS CONFIGURATION
    # Default disabled: no Redis service is bundled; set REDIS_ENABLED=True when a
    # Redis instance is available via REDIS_URL.
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "False").lower() == "true"
    
    # RISK MANAGEMENT
    MAX_ORDER_NOTIONAL: float = float(os.getenv("MAX_ORDER_NOTIONAL", "50.0"))
    MIN_SLOT_SIZE: float = 8.0
    
    # SYSTEM CONFIG
    PORT: int = int(os.getenv("PORT", "7860"))
    DIAGNOSTIC_MODE: bool = os.getenv("DIAGNOSTIC_MODE", "True").lower() == "true"
    
    # V19 SECURITY & ARCHIVAL
    ENABLE_MALWARE_PROTECTION: bool = os.getenv("ENABLE_MALWARE_PROTECTION", "True").lower() == "true"
    SHADOW_ARCHIVE_PATH: str = os.getenv("SHADOW_ARCHIVE_PATH", "/tmp/shadow_archive")
    ENABLE_GITHUB_PAGES_EXPORT: bool = os.getenv("ENABLE_GITHUB_PAGES_EXPORT", "False").lower() == "true"
    
    # AUTHENTICATION & SECURITY
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

settings = Settings()

# Fail fast at startup if critical secrets are missing in a non-test environment.
# Tests set PIONEER_SKIP_SECRET_CHECK=1 to suppress this guard.
if not os.getenv("PIONEER_SKIP_SECRET_CHECK"):
    _missing = []
    if not settings.SECRET_KEY:
        _missing.append("SECRET_KEY")
    if not settings.ADMIN_PASSWORD:
        _missing.append("ADMIN_PASSWORD")
    if _missing:
        raise RuntimeError(
            f"STARTUP ABORTED: required secret(s) not set: {', '.join(_missing)}. "
            "Set these environment variables before starting the server."
        )

# DIRECT EXPORTS (For legacy imports)
MEXC_API_KEY = settings.MEXC_API_KEY
MEXC_SECRET = settings.MEXC_SECRET
