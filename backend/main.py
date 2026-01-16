import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.services.vortex import VortexEngine

app = FastAPI()

# FORCE OPEN ALL DOORS FOR THE HUD
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
    import asyncio
    asyncio.create_task(bot.start_loop())

@app.get("/")
async def home():
    try:
        return {
            "status": "LIVE",
            "wallet_balance": f"{bot.wallet_balance:.2f}",
            "total_equity": f"{bot.total_equity:.2f}",
            "total_profit": f"{bot.total_profit:.2f}",
            "active_slots": bot.active_slots,
            "next_slot_cost": f"{bot.next_slot_price:.2f}",
            "held_coins": bot.held_coins,
            "slot_status": bot.slot_status
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}