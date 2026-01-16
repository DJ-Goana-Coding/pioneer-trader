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
    # 🟢 SEND THE BALANCE WITH EVERY POSSIBLE NAME
    return {
        "status": "active",
        "mode": "LIVE",
        "balance": bot.wallet_balance,        # <--- HUD likely wants this
        "wallet_balance": bot.wallet_balance, # <--- Backup
        "usdt": bot.wallet_balance,           # <--- Backup
        "active_slots": bot.slots
    }

@app.get("/status")
def get_status():
    return {
        "status": "active",
        "balance": bot.wallet_balance, 
        "active_slots": bot.slots
    }