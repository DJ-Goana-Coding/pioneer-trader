from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from backend.services.vortex import VortexEngine
from backend.core.logging_config import setup_logging

logger = setup_logging("main")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🟢 THE FIX: Initialize without arguments
bot = VortexEngine()

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting VortexEngine...")
    asyncio.create_task(bot.start_loop())

@app.head("/")
def health_check():
    return Response(status_code=200)

@app.get("/")
def home():
    # 🟢 FULL DATA STREAM
    bal = bot.wallet_balance
    return {
        "status": "💰 LIVE",
        "balance": bal,
        "wallet_balance": bal, 
        "profit_total": f"{bot.total_profit:.2f}",
        "next_slot_cost": f"{bot.next_slot_price:.2f}",
        "active_slots": bot.active_slots,
        "portfolio": bot.held_coins,
        "strategies": bot.slot_status
    }

@app.get("/status")
def get_status():
    return {
        "status": "active",
        "balance": bot.wallet_balance
    }