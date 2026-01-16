import os
import asyncio
import ccxt
import pandas as pd
import pandas_ta as ta

class VortexEngine:
    def __init__(self, active_slots=2):
        self.stake = 10.50
        self.slots = active_slots
        self.pairs = ['SOL/USDT', 'XRP/USDT', 'PEPE/USDT', 'DOGE/USDT', 'RENDER/USDT']
        self.exchange = ccxt.binance({
            'apiKey': os.environ.get('BINANCE_API_KEY'),
            'secret': os.environ.get('BINANCE_SECRET_KEY'),
            'enableRateLimit': True,
        })

    async def start_loop(self):
        print(f"🛰️ VORTEX ARMED: Hunting {self.pairs}")
        while True:
            balance = (await self.exchange.fetch_balance())['total'].get('USDT', 0)
            print(f"💰 WALLET: {balance} USDT")
            
            for pair in self.pairs[:self.slots]:
                # 1. Fetch OHLCV Data
                bars = self.exchange.fetch_ohlcv(pair, timeframe='1m', limit=50)
                df = pd.DataFrame(bars, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
                
                # 2. Strategy: P25 Sniper (RSI + Bollinger)
                df['rsi'] = ta.rsi(df['c'], length=14)
                current_rsi = df['rsi'].iloc[-1]
                
                print(f"🔍 {pair} | RSI: {current_rsi:.2f}")
                
                if current_rsi < 30:
                    print(f"🚀 BUY SIGNAL: {pair} oversold. Executing ${self.stake} stake.")
                    # Execute Buy Order Here
                elif current_rsi > 70:
                    print(f"🔥 SELL SIGNAL: {pair} overbought. Harvesting profit.")
                    # Execute Sell Order Here
            
            await asyncio.sleep(60)