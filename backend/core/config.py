from pydantic import BaseModel
import os
class Settings(BaseModel):
    PROJECT_NAME: str = "Pioneer Trader"
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_SECRET_KEY: str = os.getenv("BINANCE_SECRET_KEY", "")
settings = Settings()
