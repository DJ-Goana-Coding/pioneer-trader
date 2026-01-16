from fastapi import FastAPI, Response
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

# 🟢 THE KEY TO UNLOCKING RENDER (Passes the Health Check)
@app.head("/")
def health_check():
    return Response(status_code=200)

@app.get("/")
def home():
    # 🟢 SEND THE BALANCE (The "Shotgun" approach included)
    bal = bot.wallet_balance
    return {
        "status": "💰 LIVE",
        "mode": "ACTIVE",
        "balance": bal,           
        "wallet_balance": bal,    
        "usdt": bal,              
        "active_slots": bot.slots
    }

@app.get("/status")
def get_status():
    return {
        "status": "active",
        "balance": bot.wallet_balance
    }