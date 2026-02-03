import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

# 🛡️ SECURITY WARNING:
# ALL sensitive credentials MUST be set via environment variables in .env file
# NEVER commit .env file to git
# NEVER hardcode API keys, secrets, or tokens in this file
# See SECURITY_CHECKLIST.md for detailed security instructions
#
# ⚡ BERSERKER V6.9 - MEXC EXCLUSIVE:
# This system ONLY supports MEXC exchange. Binance support has been removed.
# Do NOT attempt to use other exchanges - the Vortex engine is hardcoded for MEXC.

class Settings(BaseSettings):
    PROJECT_NAME: str = "Berserker V6.9"
    VERSION: str = "6.9.0"
    
    # Security (MUST be set in production via environment variables)
    SECRET_KEY: str = ""  # REQUIRED: Set via environment or generate with: openssl rand -hex 32
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # MEXC Exchange API Keys - ⚠️ CRITICAL: Set these in .env file, NOT here!
    # BERSERKER V6.9 supports MEXC ONLY - all other exchange code has been removed
    MEXC_API_KEY: str = ""
    MEXC_SECRET_KEY: str = ""
    EXECUTION_MODE: Literal["PAPER", "TESTNET", "LIVE"] = "PAPER"
    
    # Risk
    MAX_ORDER_NOTIONAL: float = 100.0  # Safety clamp in USDT
    
    # Vortex Berserker Engine Configuration
    # These values implement the Commander's mandate for Berserker V6.9
    VORTEX_STAKE_USDT: float = 8.0  # $8 USDT per trade (Commander's mandate)
    VORTEX_STOP_LOSS_PCT: float = 0.015  # 1.5% ejector seat (MANDATORY, cannot be disabled)
    VORTEX_PULSE_SECONDS: int = 8  # 8-second aggressive trading pulse
    
    # V19 Fleet Configuration
    UI_THEME: Literal["OVERKILL", "ZEN"] = "OVERKILL"
    SAFETY_MODULATOR: int = 5  # 0-10 scale for trade aggression
    ENABLE_GITHUB_AUTH: bool = False
    GITHUB_CLIENT_ID: str = ""
    
    # Swarm Configuration
    PHI_DRONE_COUNT: int = 6
    ENABLE_MALWARE_PROTECTION: bool = True
    
    # Archival
    ENABLE_GITHUB_PAGES_EXPORT: bool = False
    SHADOW_ARCHIVE_PATH: str = "/tmp/shadow_archive"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
