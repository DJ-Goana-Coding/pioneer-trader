import ccxt.async_support as ccxt
import os
import asyncio

class StrategyEngine:
    def __init__(self):
        self.exchange = None
        self.last_reload = "Init"
        self.last_strategy = "None"
        
        # Load Creds from Environment (Set in Render Dashboard)
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.secret = os.getenv("BINANCE_SECRET_KEY")

    async def _init_exchange(self):
        if not self.exchange:
            # Defaulting to Binance US or Global based on typical setup
            # If using Testnet, change 'enableRateLimit': True to include 'options': {'defaultType': 'spot'}
            self.exchange = ccxt.binance({
                'apiKey': self.api_key,
                'secret': self.secret,
                'enableRateLimit': True,
                # 'options': {'defaultType': 'future'} # Uncomment if trading futures
            })
            # If in Sandbox/Paper mode, you might need:
            # self.exchange.set_sandbox_mode(True) 

    async def reload_strategy(self, name: str) -> bool:
        self.last_reload = "Success"
        self.last_strategy = name
        print(f"🔄 Reloading Strategy: {name}")
        return True

    async def get_telemetry(self) -> dict:
        # 1. Ensure Exchange is Connected
        if not self.api_key or not self.secret:
            return {
                "status": "Blind", 
                "error": "BINANCE_API_KEY or SECRET not set in Render Env",
                "engine": "Frankfurt"
            }
        
        await self._init_exchange()
        
        try:
            # 2. Fetch Real Balance
            balance = await self.exchange.fetch_balance()
            
            # Filter for non-zero assets (The "Hot Wallet")
            assets = {
                k: v['free'] 
                for k, v in balance.items() 
                if v['free'] > 0 or v['used'] > 0
            }
            
            return {
                "status": "Active",
                "engine": "Frankfurt",
                "wallet": assets,
                "strategy": self.last_strategy
            }
            
        except Exception as e:
            return {
                "status": "Error",
                "error": str(e),
                "engine": "Frankfurt"
            }
        finally:
            if self.exchange:
                await self.exchange.close()
                self.exchange = None
