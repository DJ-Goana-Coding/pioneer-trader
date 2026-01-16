from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from backend.services.vortex import VortexEngine

app = FastAPI()

# ALLOW VERCEL TO TALK TO RENDER
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all connections (Simplest for now)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# INIT ENGINE
bot = VortexEngine()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bot.start_loop())

@app.get("/")
def home():
    return {"status": "Vortex Engine Active", "mode": "LIVE"}

@app.get("/status")
def get_status():
    # RETURN THE SAVED BALANCE TO VERCEL
    return {
        "status": "active",
        "wallet_balance": bot.wallet_balance, 
        "active_slots": bot.slots
    }