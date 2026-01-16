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

# 🟢 FIX: NO ARGUMENTS (Prevents Crash)
bot = VortexEngine()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bot.start_loop())

# 🟢 HEALTH CHECK (Prevents Render 405 Error)
@app.head("/")
def health_check():
    return Response(status_code=200)

@app.get("/")
def home():
    # 🟢 FULL DATA STREAM FOR VERCEL
    bal = bot.wallet_balance
    return {
        "status": "💰 LIVE",
        "balance": bal,
        "wallet_balance": bal, # Backup key
        
        # RICH DATA
        "profit_total": f"{bot.total_profit:.2f}",
        "next_slot_cost": f"{bot.next_slot_price:.2f}",
        "active_slots": bot.active_slots,
        "portfolio": bot.held_coins,  # {"PEPE": "4000", "SOL": "0.5"}
        "strategies": bot.slot_status # [{"slot": 1, "pair": "SOL", "rsi": 30}]
    }

@app.get("/status")
def get_status():
    return {
        "status": "active",
        "balance": bot.wallet_balance
    }