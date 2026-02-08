from fastapi import FastAPI, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from backend.services.vortex import VortexEngine
from backend.core.logging_config import setup_logging
from backend.core.security import get_current_admin

logger = setup_logging("main")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8501",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
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

@app.get("/health")
def health():
    """Public health check endpoint for load balancers"""
    return {"status": "ok"}

@app.get("/")
def home(current_user: str = Depends(get_current_admin)):
    # 🟢 FULL DATA STREAM - Now protected with authentication
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
def get_status(current_user: str = Depends(get_current_admin)):
    return {
        "status": "active",
        "balance": bot.wallet_balance
    }