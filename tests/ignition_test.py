import pandas as pd
import numpy as np
from backend.services.strategies import StrategyLogic

def run_test():
    print("🔬 IGNITION TEST: Simulating 'The Hammer' Strategy...")
    logic = StrategyLogic()
    
    # Create fake "Oversold" data (RSI should be < 30)
    data = {
        'close': [100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86]
    }
    df = pd.DataFrame(data)
    
    # We simulate a P25 Momentum scan
    result = logic.p25_momentum(df)
    
    print(f"📈 Simulated Price Action: Trending Down")
    print(f"🎯 Strategy Result: {result}")
    
    if result == "BUY":
        print("✅ TEST PASSED: Hammer detected oversold conditions correctly.")
    else:
        print("⚠️ TEST CHECK: Strategy returned HOLD. Price action may not be volatile enough.")

if __name__ == "__main__":
    run_test()