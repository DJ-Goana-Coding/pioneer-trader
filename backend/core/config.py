import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pioneer-Admiral V1"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Exchange
    BINANCE_API_KEY: str = ""
    BINANCE_SECRET_KEY: str = ""
    EXECUTION_MODE: Literal["PAPER", "TESTNET", "LIVE"] = "PAPER"
    
    # Risk
    MAX_ORDER_NOTIONAL: float = 100.0  # Safety clamp in USDT
    
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
