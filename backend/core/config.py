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
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
