# ================================================================
# 📡 STRATEGY ENGINE - MEXC MIGRATION
# ================================================================
import ccxt.async_support as ccxt
import os
import asyncio

class StrategyEngine:
    def __init__(self):
        self.exchange = None
        self.last_reload = "Init"
        self.last_strategy = "None"
        
        self.api_key = os.getenv("MEXC_API_KEY")
        self.secret = os.getenv("MEXC_SECRET")

    async def _init_exchange(self):
        if not self.exchange:
            self.exchange = ccxt.mexc({
                'apiKey': self.api_key,
                'secret': self.secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                    'createMarketBuyOrderRequiresPrice': False
                }
            })

    async def reload_strategy(self, name: str) -> bool:
        self.last_reload = "Success"
        self.last_strategy = name
        print(f"🔄 Reloading Strategy: {name}")
        return True

    async def get_telemetry(self) -> dict:
        if not self.api_key or not self.secret:
            return {
                "status": "Blind", 
                "error": "MEXC_API_KEY or MEXC_SECRET not set",
                "engine": "Frankfurt",
                "exchange": "MEXC"
            }
        
        await self._init_exchange()
        
        try:
            balance = await self.exchange.fetch_balance()
            
            assets = {
                k: v['free'] 
                for k, v in balance.items() 
                if isinstance(v, dict) and (v.get('free', 0) > 0 or v.get('used', 0) > 0)
            }
            
            return {
                "status": "Active",
                "engine": "Frankfurt",
                "exchange": "MEXC",
                "wallet": assets,
                "strategy": self.last_strategy
            }
            
        except Exception as e:
            return {
                "status": "Error",
                "error": str(e),
                "engine": "Frankfurt",
                "exchange": "MEXC"
            }
        finally:
            if self.exchange:
                await self.exchange.close()
                self.exchange = None
