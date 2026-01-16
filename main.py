from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from backend.services.vortex import VortexEngine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bot = VortexEngine()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bot.start_loop())

@app.get("/")
def home():
    # 🟢 SENDING DATA IN EVERY POSSIBLE FORMAT
    bal = bot.wallet_balance
    return {
        "status": "💰 LIVE",
        "mode": "ACTIVE",
        
        # KEY VARIATIONS
        "balance": bal,           # Common
        "wallet_balance": bal,    # Backend name
        "wallet": bal,            # Short
        "value": bal,             # Generic
        "amount": bal,            # Finance
        "usdt": bal,              # Crypto
        "total": bal,             # Sum
        
        # STRING VERSIONS (In case HUD expects text)
        "balance_str": f"{bal:.2f}",
        "display_balance": f"{bal:.2f} USDT",
        
        "active_slots": bot.slots
    }

@app.get("/status")
def get_status():
    return {
        "status": "active",
        "balance": bot.wallet_balance
    }