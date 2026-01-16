from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from backend.services.vortex import VortexEngine

app = FastAPI()

# ENABLE VERCEL ACCESS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# INIT ENGINE
bot = VortexEngine()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bot.start_loop())

# 🟢 THE FIX: SEND EVERYTHING ON THE HOME PAGE
@app.get("/")
def home():
    return {
        "status": "active", 
        "mode": "LIVE",
        "wallet_balance": bot.wallet_balance,  # <--- HERE IT IS
        "active_slots": bot.slots
    }

@app.get("/status")
def get_status():
    return {
        "status": "active",
        "wallet_balance": bot.wallet_balance,
        "active_slots": bot.slots
    }